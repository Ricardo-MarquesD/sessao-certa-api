from enum import Enum

class AppointmentStatus(Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"