from enum import Enum
from dataclasses import dataclass

@dataclass
class MachineAnwser:
    anwser: str
    next_state: FlowState
    is_end: bool | None
    data: dict | None


class FlowState(str, Enum):
    initial_message = "initial_message"
    service_message = "service_message"
    employeee_message = "employeee_message"
    date_message = "date_message"
    hour_message = "hour_message"
    list_message = "list_message"
    ok_message = "ok_message"                  # finaliza conversa
    cancel_message = "cancel_message"
    confirm_message = "confirm_message"
    complete_message = "complete_message"      # finaliza conversa
    unmarked_message = "unmarked_message"      # finaliza conversa
    error_message = "error_message"            # mantém estado e NÃO salva no DB