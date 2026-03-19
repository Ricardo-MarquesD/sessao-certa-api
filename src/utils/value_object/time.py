from datetime import datetime, timedelta, date, time


_WEEKDAYS_PT: dict[str, str] = {
    "monday": "Segunda-feira",
    "tuesday": "Terça-feira",
    "wednesday": "Quarta-feira",
    "thursday": "Quinta-feira",
    "friday": "Sexta-feira",
    "saturday": "Sábado",
    "sunday": "Domingo",
}


class TimeManipulation:
    @staticmethod
    def time_diference(date: datetime, date_sub: datetime | None = None)->timedelta:
        if date_sub is None:
            date_sub = datetime.now()
        if not isinstance(date, datetime):
            raise ValueError("date must be a datetime")
        if not isinstance(date_sub, datetime):
            raise ValueError("date_sub must be a datetime")
        
        return date - date_sub
    
    @staticmethod
    def time_duration(start_time: datetime, min_duration: int)->datetime:
        if not isinstance(start_time, datetime):
            raise ValueError("start_time must be a datetime")
        if not isinstance(min_duration, int):
            raise ValueError("min-duration must be a integer")

        return start_time + timedelta(minutes=min_duration)


class SchedulingHelper:
    SLOT_THRESHOLD = 30  # minutos mínimos para considerar um dia disponível

    @staticmethod
    def format_minute(minute: int) -> str:
        return f"{minute // 60:02d}:{minute % 60:02d}"

    @staticmethod
    def get_work_window_for_day(available_hours: dict | None, day_iso: str) -> tuple[int, int] | None:
        if not isinstance(available_hours, dict):
            return None

        try:
            day_obj = date.fromisoformat(day_iso)
        except ValueError:
            return None

        weekday_name = day_obj.strftime("%A").lower()
        hours = available_hours.get(weekday_name)
        if not isinstance(hours, list) or len(hours) < 2:
            return None

        try:
            start_time = datetime.strptime(hours[0], "%H:%M").time()
            end_time = datetime.strptime(hours[1], "%H:%M").time()
        except (TypeError, ValueError):
            return None

        start_min = start_time.hour * 60 + start_time.minute
        end_min = end_time.hour * 60 + end_time.minute
        if end_min <= start_min:
            return None

        return start_min, end_min

    @staticmethod
    def build_slot_candidates(
        start_min: int,
        end_min: int,
        appointments: list,
    ) -> list[int]:
        slots = set(range(start_min, end_min, 30))

        for appt in appointments:
            appt_start_dt = getattr(appt, "appointment_date", None)
            if appt_start_dt is None:
                continue

            service = getattr(appt, "service", None)
            appt_duration = getattr(service, "time_duration", None)
            if not isinstance(appt_duration, int) or appt_duration <= 0:
                continue

            appt_start = appt_start_dt.hour * 60 + appt_start_dt.minute
            appt_end = appt_start + appt_duration

            clipped_start = max(appt_start, start_min)
            clipped_end = min(appt_end, end_min)

            if clipped_start < clipped_end:
                for minute in list(slots):
                    if clipped_start <= minute < clipped_end:
                        slots.discard(minute)

                if start_min <= clipped_end < end_min:
                    slots.add(clipped_end)

        return sorted(slots)

    @staticmethod
    def has_conflict_interval(
        start_dt: datetime,
        end_dt: datetime,
        appointments: list,
    ) -> bool:
        for appt in appointments:
            appt_start = getattr(appt, "appointment_date", None)
            if appt_start is None:
                continue

            service = getattr(appt, "service", None)
            appt_duration = getattr(service, "time_duration", None)
            if not isinstance(appt_duration, int) or appt_duration <= 0:
                continue

            appt_end = appt_start + timedelta(minutes=appt_duration)
            if start_dt < appt_end and end_dt > appt_start:
                return True

        return False

    @staticmethod
    def format_day(iso_date: str) -> str:
        d = date.fromisoformat(iso_date)
        weekday_pt = _WEEKDAYS_PT[d.strftime("%A").lower()]
        return f"{weekday_pt}, {d.strftime('%d/%m')}"

    @staticmethod
    def has_available_slot(
        work_start: time,
        work_end: time,
        appointments: list,
    ) -> bool:
        """Verifica se há pelo menos um slot de 30 min livre dentro do horário de trabalho."""
        start_min = work_start.hour * 60 + work_start.minute
        end_min = work_end.hour * 60 + work_end.minute

        if end_min - start_min < SchedulingHelper.SLOT_THRESHOLD:
            return False

        booked: list[tuple[int, int]] = []
        for appt in appointments:
            appt_start = appt.appointment_date.hour * 60 + appt.appointment_date.minute
            appt_end = appt_start + appt.service.time_duration
            clipped_start = max(appt_start, start_min)
            clipped_end = min(appt_end, end_min)
            if clipped_start < clipped_end:
                booked.append((clipped_start, clipped_end))

        booked.sort()
        cursor = start_min
        for appt_start, appt_end in booked:
            if appt_start - cursor >= SchedulingHelper.SLOT_THRESHOLD:
                return True
            cursor = max(cursor, appt_end)

        return end_min - cursor >= SchedulingHelper.SLOT_THRESHOLD


if __name__ == "__main__":
    res = TimeManipulation.time_diference(datetime(2025,12,31,15,30,45))
    print(type(res))
    print(res)