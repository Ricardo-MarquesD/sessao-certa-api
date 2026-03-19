from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from uuid import UUID, uuid4
from domain.entities import Context, Scheduling
from infra.repository import ServiceRepository, EmployeeRepository, EstablishmentRepository, SchedulingRepository, CustomerRepository
from utils.enum import FlowState, MachineAnwser, AppointmentStatus
from utils.value_object import SchedulingHelper

class StateMachine:

    def __init__(self, context: Context, *, message: str, db: Session):
        self.context = context
        self.message = (message or "").strip()
        self.db = db
        self.service_repository = ServiceRepository(db)
        self.employee_repository = EmployeeRepository(db)
        self.establishment_repository = EstablishmentRepository(db)
        self.scheduling_repository = SchedulingRepository(db)
        self.customer_repository = CustomerRepository(db)

    def _merge_data(self, new_data: dict | None) -> dict | None:
        if not new_data:
            return self.context.context_data or None
        merged = dict(self.context.context_data or {})
        merged.update(new_data)
        return merged

    def _get_work_window_for_day(self, *, day_iso: str, employee_id: int | None) -> tuple[int, int] | None:
        if employee_id is not None:
            employee = self.employee_repository.get_by_id(employee_id)
            available_hours: dict = (employee.available_hours if employee else None) or {}
        else:
            establishment = self.establishment_repository.get_by_internal_id(self.context.establishments_id)
            available_hours: dict = (establishment.available_hours if establishment else None) or {}

        return SchedulingHelper.get_work_window_for_day(available_hours, day_iso)

    def initial_message(self, *, single: bool, has_scheduling: bool) -> MachineAnwser:
        self.message = self.message.lower().strip()

        if single:
            scheduling_option = "2 - Meus Agendamentos" if has_scheduling else ""
            return MachineAnwser(
                anwser= "Olá, como posso te ajudar?\n"
                "1 - Agendar\n"
                f"{scheduling_option}",
                next_state=FlowState.initial_message,
                is_end=False,
                data={'phone_number': self.context.phone_number}
            )

        if self.message in {"1", "um", "one"}:
            return self.service_message(single = 1)

        if self.message in {"2", "dois", "two"}:
            return self.list_message(single = 1)

        return self.error_message()
    
    def service_message(self, *, single: bool) -> MachineAnwser:
        self.message = self.message.lower().strip()

        services = self.service_repository.list_active_by_establishment_internal_id(self.context.establishments_id)

        if single:
            if not services:
                return MachineAnwser(
                    anwser="No momento não há serviços disponíveis.",
                    next_state=FlowState.initial_message,
                    is_end=True,
                    data=None,
                )

            options = "\n".join(
                f"{i + 1} - {s.service_name}" for i, s in enumerate(services)
            )
            return MachineAnwser(
                anwser=f"Gostaria de marcar qual de nossos serviços?\n{options}",
                next_state=FlowState.service_message,
                is_end=False,
                data=None,
            )

        if not self.message.isdigit():
            return self.error_message()

        choice = int(self.message)
        if not (1 <= choice <= len(services)):
            return self.error_message()

        chosen = services[choice - 1]
        answer = self.employeee_message(single=True)
        answer.data = self._merge_data(
            {
                "service_id": str(chosen.id),
                "service_name": chosen.service_name,
            }
        )
        return answer

    def employeee_message(self, *, single: bool) -> MachineAnwser:
        self.message = self.message.lower().strip()

        employees = self.employee_repository.list_by_establishment_internal_id(self.context.establishments_id)

        no_option = len(employees) + 1
        if single:
            options = "\n".join(
                f"{i + 1} - {e.user.user_name}" for i, e in enumerate(employees)
            )
            return MachineAnwser(
                anwser=(
                    f"Tem preferência por algum de nossos funcionários?\n"
                    f"{options}\n"
                    f"{no_option} - Sem preferência"
                ),
                next_state=FlowState.employeee_message,
                is_end=False,
                data=None,
            )

        if self.message == str(no_option) or self.message in {"nao", "não", "n", "no"}:
            answer = self.date_message(single=True, employee_id=None)
            answer.data = self._merge_data({"employee_id": None})

            return answer

        if not self.message.isdigit():
            return self.error_message()

        choice = int(self.message)
        if not (1 <= choice <= len(employees)):
            return self.error_message()

        chosen = employees[choice - 1]
        answer = self.date_message(single=True, employee_id=chosen.id)
        answer.data = self._merge_data({"employee_id": chosen.id})

        return answer

    def date_message(self, *, single: bool, employee_id: int | None = None) -> MachineAnwser:
        self.message = self.message.lower().strip()

        if not single:
            employee_id = (self.context.context_data or {}).get("employee_id")

        if employee_id is not None:
            employee = self.employee_repository.get_by_id(employee_id)
            available_hours: dict = (employee.available_hours if employee else None) or {}
        else:
            establishment = self.establishment_repository.get_by_internal_id(
                self.context.establishments_id
            )
            available_hours: dict = (
                establishment.available_hours if establishment else None
            ) or {}

        if single:
            today = date.today()
            available_days: list[str] = []

            for offset in range(1, 8):
                candidate = today + timedelta(days=offset)
                weekday_name = candidate.strftime("%A").lower()

                if weekday_name not in available_hours:
                    continue

                hours = available_hours[weekday_name]
                work_start = datetime.strptime(hours[0], "%H:%M").time()
                work_end = datetime.strptime(hours[1], "%H:%M").time()

                appointments = self.scheduling_repository.list_active_by_day_and_scope(
                    day=candidate,
                    establishment_internal_id=self.context.establishments_id,
                    employee_id=employee_id,
                )

                if SchedulingHelper.has_available_slot(work_start, work_end, appointments):
                    available_days.append(candidate.isoformat())

            if not available_days:
                return MachineAnwser(
                    anwser=(
                        "Não há dias disponíveis para agendamento essa semana, "
                        "por favor tente novamente mais tarde."
                    ),
                    next_state=FlowState.initial_message,
                    is_end=True,
                    data=None,
                )

            options = "\n".join(
                f"{i + 1} - {SchedulingHelper.format_day(d)}" for i, d in enumerate(available_days)
            )
            return MachineAnwser(
                anwser=f"Temos esses dias disponíveis para agendamento:\n{options}",
                next_state=FlowState.date_message,
                is_end=False,
                data=self._merge_data({"available_days": available_days}),
            )

        # single=False: valida a escolha do usuário
        available_days = (self.context.context_data or {}).get("available_days", [])

        if not self.message.isdigit():
            return self.error_message()

        choice = int(self.message)
        if not (1 <= choice <= len(available_days)):
            return self.error_message()

        chosen_date = available_days[choice - 1]
        answer = self.hour_message(single=True, scheduling_date=chosen_date, employee_id=employee_id)
        if answer is not None:
            answer.data = self._merge_data({"scheduling_date": chosen_date, "employee_id": employee_id})
        return answer

    def hour_message(self, *, single: bool, scheduling_date: str | None = None, employee_id: int | None = None) -> MachineAnwser:
        self.message = self.message.lower().strip()

        context_data = self.context.context_data or {}
        if not single:
            scheduling_date = scheduling_date or context_data.get("scheduling_date")
            employee_id = context_data.get("employee_id") if employee_id is None else employee_id

        if not scheduling_date:
            return self.error_message()

        service_id_str = context_data.get("service_id")
        if not service_id_str:
            return self.error_message()

        try:
            service_uuid = UUID(service_id_str)
            day = date.fromisoformat(scheduling_date)
        except (TypeError, ValueError):
            return self.error_message()

        service = self.service_repository.get_by_id(service_uuid)
        if service is None:
            return self.error_message()

        window = self._get_work_window_for_day(day_iso=scheduling_date, employee_id=employee_id)
        if window is None:
            return MachineAnwser(
                anwser="Não há horários disponíveis para o dia selecionado.",
                next_state=FlowState.date_message,
                is_end=False,
                data=self._merge_data({"scheduling_date": scheduling_date}),
            )

        start_min, end_min = window
        all_day_appointments = self.scheduling_repository.list_active_by_day_and_scope(
            day=day,
            establishment_internal_id=self.context.establishments_id,
            employee_id=employee_id,
        )

        candidate_minutes = SchedulingHelper.build_slot_candidates(
            start_min=start_min,
            end_min=end_min,
            appointments=all_day_appointments,
        )

        available_slots: list[str] = []
        slot_employee_map: dict[str, int] = {}

        employees_for_fallback = self.employee_repository.list_by_establishment_internal_id(self.context.establishments_id)
        employees_for_fallback.sort(key=lambda e: e.id or 0)

        for minute in candidate_minutes:
            slot_start = datetime.combine(day, datetime.strptime(SchedulingHelper.format_minute(minute), "%H:%M").time())
            slot_end = service.calculate_end_time(slot_start)

            if (slot_end.hour * 60 + slot_end.minute) > end_min:
                continue

            if employee_id is not None:
                if SchedulingHelper.has_conflict_interval(start_dt=slot_start, end_dt=slot_end, appointments=all_day_appointments):
                    continue
                slot_text = SchedulingHelper.format_minute(minute)
                available_slots.append(slot_text)
                slot_employee_map[slot_text] = employee_id
                continue

            selected_employee_id: int | None = None
            for emp in employees_for_fallback:
                if emp.id is None:
                    continue
                emp_appointments = self.scheduling_repository.list_active_by_day_and_scope(
                    day=day,
                    establishment_internal_id=self.context.establishments_id,
                    employee_id=emp.id,
                )
                if not SchedulingHelper.has_conflict_interval(start_dt=slot_start, end_dt=slot_end, appointments=emp_appointments):
                    selected_employee_id = emp.id
                    break

            if selected_employee_id is None:
                continue

            slot_text = SchedulingHelper.format_minute(minute)
            available_slots.append(slot_text)
            slot_employee_map[slot_text] = selected_employee_id

        if single:
            if not available_slots:
                return MachineAnwser(
                    anwser="Não há horários disponíveis para o dia selecionado.",
                    next_state=FlowState.date_message,
                    is_end=False,
                    data=self._merge_data({"scheduling_date": scheduling_date}),
                )

            options = "\n".join(
                f"{i + 1} - {slot}" for i, slot in enumerate(available_slots)
            )
            return MachineAnwser(
                anwser=f"Nesse dia temos os seguintes horários de atendimento:\n{options}",
                next_state=FlowState.hour_message,
                is_end=False,
                data=self._merge_data(
                    {
                        "scheduling_date": scheduling_date,
                        "available_slots": available_slots,
                        "slot_employee_map": slot_employee_map,
                        "employee_id": employee_id,
                    }
                ),
            )

        available_slots = context_data.get("available_slots", [])
        slot_employee_map = context_data.get("slot_employee_map", {})

        if not self.message.isdigit():
            return self.error_message()

        choice = int(self.message)
        if not (1 <= choice <= len(available_slots)):
            return self.error_message()

        chosen_time = available_slots[choice - 1]
        selected_employee_id = slot_employee_map.get(chosen_time, employee_id)
        try:
            day_obj = date.fromisoformat(scheduling_date)
        except ValueError:
            return self.error_message()

        answer = MachineAnwser(
            anwser=(
                f"Um(a) {context_data.get('service_name', 'serviço')} às {chosen_time} "
                f"no dia {day_obj.strftime('%d/%m/%Y')}, certo?\n"
                "1 - Confirmar\n"
                "2 - Desmarcar"
            ),
            next_state=FlowState.confirm_message,
            is_end=False,
            data=self._merge_data(
                {
                    "scheduling_time": chosen_time,
                    "employee_id": selected_employee_id,
                    "scheduling_date": scheduling_date,
                }
            ),
        )
        return answer

    def list_message(self, *, single: bool) -> MachineAnwser:
        customer_internal_id = self.context.customers_id
        self.message = (self.message or "").lower().strip()

        if not customer_internal_id:
            return MachineAnwser(
                anwser="Você não possui nenhum agendamento ativo no momento.",
                next_state=FlowState.list_message,
                is_end=False,
                data=None,
            )

        if single:
            schedulings = self.scheduling_repository.list_active_by_customer_internal_id(customer_internal_id)

            if not schedulings:
                return MachineAnwser(
                    anwser="Você não possui nenhum agendamento ativo no momento.",
                    next_state=FlowState.list_message,
                    is_end=False,
                    data=None,
                )

            options: list[str] = []
            scheduling_ids: list[str] = []

            for idx, scheduling in enumerate(schedulings, start=1):
                dt = scheduling.appointment_date
                if dt is not None:
                    datetime_str = dt.strftime("%d/%m/%Y às %H:%M")
                else:
                    datetime_str = "Data e horário não informados"

                options.append(
                    f"{idx} - {scheduling.service.service_name} com {scheduling.employee.user.user_name} em {datetime_str}"
                )
                scheduling_ids.append(str(getattr(scheduling, "id", "")))

            back_option = len(options) + 1
            anwser = (
                "Olá, como posso te ajudar?\n"
                + "\n".join(options)
                + f"\n{back_option} - Voltar"
            )

            return MachineAnwser(
                anwser=anwser,
                next_state=FlowState.list_message,
                is_end=False,
                data=self._merge_data({"active_scheduling_ids": scheduling_ids}),
            )

        scheduling_ids = (self.context.context_data or {}).get("active_scheduling_ids", [])
        back_option = len(scheduling_ids) + 1

        if not self.message.isdigit():
            return self.error_message()

        choice = int(self.message)
        if choice == back_option:
            has_scheduling = bool(scheduling_ids)
            return self.initial_message(single=True, has_scheduling=has_scheduling)

        if not (1 <= choice <= len(scheduling_ids)):
            return self.error_message()

        chosen_id = scheduling_ids[choice - 1]
        return MachineAnwser(
            anwser="Gostaria de desmarcar esse agendamento?\n1 - Sim\n2 - Não",
            next_state=FlowState.cancel_message,
            is_end=False,
            data=self._merge_data({"scheduling_id": chosen_id}),
        )

    def ok_message(self) -> MachineAnwser:
        return MachineAnwser(
            anwser="Ok",
            next_state=FlowState.ok_message,
            is_end=True,
            data=None,
        )

    def cancel_message(self) -> MachineAnwser:
        self.message = (self.message or "").lower().strip()

        # Espera-se que o agendamento selecionado esteja em context_data["scheduling_id"]
        context_data = self.context.context_data or {}
        scheduling_id_str = context_data.get("scheduling_id")

        if self.message in {"1", "sim", "s", "yes"}:
            if not scheduling_id_str:
                return self.error_message()

            try:
                scheduling_uuid = UUID(scheduling_id_str)
            except (TypeError, ValueError):
                return self.error_message()

            scheduling = self.scheduling_repository.get_by_id(scheduling_uuid)
            if scheduling is None:
                return self.error_message()

            # Apenas marca como cancelado se ainda puder ser cancelado
            if hasattr(scheduling, "can_cancel") and callable(scheduling.can_cancel) and not scheduling.can_cancel():
                return self.error_message()

            scheduling.appointment_status = AppointmentStatus.CANCELED
            self.scheduling_repository.update(scheduling)

            return self.unmarked_message()

        if self.message in {"2", "nao", "não", "n", "no"}:
            return self.ok_message()

        return self.error_message()

    def confirm_message(self) -> MachineAnwser:
        self.message = (self.message or "").lower().strip()
        context_data = self.context.context_data or {}

        # Quando usuário confirma (1), verificamos conflito de horário
        if self.message in {"1", "sim", "s", "yes"}:
            service_id_str = context_data.get("service_id")
            scheduling_date_str = context_data.get("scheduling_date")
            scheduling_time_str = context_data.get("scheduling_time")
            employee_id = context_data.get("employee_id")
            customer_internal_id = self.context.customers_id

            if not (service_id_str and scheduling_date_str and scheduling_time_str and employee_id and customer_internal_id):
                # Dados insuficientes para confirmar
                return self.error_message()

            try:
                service_uuid = UUID(service_id_str)
                day = date.fromisoformat(scheduling_date_str)
                time_obj = datetime.strptime(scheduling_time_str, "%H:%M").time()
            except (ValueError, TypeError):
                return self.error_message()

            service = self.service_repository.get_by_id(service_uuid)
            if service is None:
                return self.error_message()

            employee = self.employee_repository.get_by_id(int(employee_id))
            if employee is None:
                return self.error_message()

            customer = self.customer_repository.get_by_internal_id(int(customer_internal_id))
            if customer is None:
                return self.error_message()

            start_dt = datetime.combine(day, time_obj)
            end_dt = service.calculate_end_time(start_dt)

            # Busca agendamentos ativos para o dia e escopo (estabelecimento/funcionário)
            appointments = self.scheduling_repository.list_active_by_day_and_scope(
                day=day,
                establishment_internal_id=self.context.establishments_id,
                employee_id=int(employee_id),
            )

            has_conflict = False
            for appt in appointments:
                if not getattr(appt, "appointment_date", None):
                    continue
                appt_start = appt.appointment_date
                appt_duration = getattr(getattr(appt, "service", None), "time_duration", None)
                if appt_duration is None:
                    continue

                appt_end = appt_start + timedelta(minutes=appt_duration)

                # Verifica sobreposição de intervalos
                if start_dt < appt_end and end_dt > appt_start:
                    has_conflict = True
                    break

            if has_conflict:
                answer = self.hour_message(
                    single=True,
                    scheduling_date=scheduling_date_str,
                    employee_id=int(employee_id),
                )
                answer.anwser = (
                    "Infelizmente encontramos um conflito de horário, por favor "
                    "remarque para outro horário nesse dia.\n\n"
                    f"{answer.anwser}"
                )
                return answer

            # Sem conflito: cria agendamento e confirma no fluxo de conversa
            new_scheduling = Scheduling(
                id=uuid4(),
                establishment=service.establishment,
                employee=employee,
                customer=customer,
                service=service,
                appointment_status=AppointmentStatus.SCHEDULED,
                appointment_date=start_dt,
                notification_sent=False,
                created_at=datetime.now(),
            )
            self.scheduling_repository.create(new_scheduling)
            return self.complete_message()

        # Usuário optou por desmarcar na tela de confirmação (2 - Desmarcar)
        if self.message in {"2", "nao", "não", "n", "no"}:
            return self.unmarked_message()

        return self.error_message()

    def complete_message(self) -> MachineAnwser:
        return MachineAnwser(
            anwser="Agendamento feito com sucesso, agradecemos a preferência",
            next_state=FlowState.complete_message,
            is_end=True,
            data=None,
        )

    def unmarked_message(self) -> MachineAnwser:
        return MachineAnwser(
            anwser="Sessão desmarcada com sucesso",
            next_state=FlowState.unmarked_message,
            is_end=True,
            data=None,
        )

    def error_message(self) -> MachineAnwser:
        current_state = self.context.context_arrow or FlowState.initial_message.value
        try:
            next_state = FlowState(current_state)
        except ValueError:
            next_state = FlowState.initial_message

        return MachineAnwser(
            anwser="Poderia repetir por favor, não foi possível identificar sua resposta",
            next_state=next_state,
            data={},
            is_end=False
        )