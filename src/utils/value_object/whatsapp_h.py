from utils.enum import FlowState, MachineAnwser


class WhatsappProcessHelper:

    @staticmethod
    def resolve_state(context) -> FlowState:
        try:
            return FlowState(context.context_arrow) if context.context_arrow else FlowState.initial_message
        except ValueError:
            return FlowState.initial_message

    @staticmethod
    def _has_active_scheduling(state_machine, context) -> bool:
        if not context.customers_id:
            return False

        active_schedulings = state_machine.scheduling_repository.list_active_by_customer_internal_id(
            context.customers_id
        )
        return bool(active_schedulings)

    @staticmethod
    def dispatch_answer(state_machine, context) -> MachineAnwser:
        current_state = WhatsappProcessHelper.resolve_state(context)

        if current_state == FlowState.initial_message:
            has_scheduling = WhatsappProcessHelper._has_active_scheduling(state_machine, context)
            return state_machine.initial_message(single=False, has_scheduling=has_scheduling)

        if current_state == FlowState.service_message:
            return state_machine.service_message(single=False)

        if current_state == FlowState.employeee_message:
            return state_machine.employeee_message(single=False)

        if current_state == FlowState.date_message:
            return state_machine.date_message(single=False)

        if current_state == FlowState.hour_message:
            return state_machine.hour_message(single=False)

        if current_state == FlowState.list_message:
            return state_machine.list_message(single=False)

        if current_state == FlowState.cancel_message:
            return state_machine.cancel_message()

        if current_state == FlowState.confirm_message:
            return state_machine.confirm_message()

        if current_state == FlowState.ok_message:
            return state_machine.ok_message()

        if current_state == FlowState.complete_message:
            return state_machine.complete_message()

        if current_state == FlowState.unmarked_message:
            return state_machine.unmarked_message()

        return state_machine.error_message()

    @staticmethod
    def update_context(context, answer: MachineAnwser):
        if answer.data not in (None, {}):
            context.context_data = answer.data

        if answer.next_state is not None:
            context.context_arrow = answer.next_state.value

        if answer.is_end:
            context.close()
        else:
            context.is_open = True

        return context