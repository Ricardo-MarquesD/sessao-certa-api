from .user import UserModel, UserRole
from .plan import PlanModel, TypePlan
from .client import ClientModel
from .establishment import EstablishmentModel
from .customer import CustomerModel
from .employee import EmployeeModel
from .marketing_message import MarketingMessageModel
from .payment import PaymentModel, PaymentType, PaymentStatus
from .service import ServiceModel
from .scheduling import SchedulingModel, AppointmentStatus
from .stock import StockProductModel, StockMovementModel, MovementType

# Friendly aliases without the `Model` suffix to match test imports
User = UserModel
Plan = PlanModel
Client = ClientModel
Establishment = EstablishmentModel
Customer = CustomerModel
Employee = EmployeeModel
MarketingMessage = MarketingMessageModel
Payment = PaymentModel
Service = ServiceModel
Scheduling = SchedulingModel
StockProduct = StockProductModel
StockMovement = StockMovementModel
