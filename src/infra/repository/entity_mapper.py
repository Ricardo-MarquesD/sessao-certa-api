"""
Mapper centralizado para converter modelos ORM em entidades de domínio.
Evita duplicação de código nos repositórios.
"""
from infra.models import UserModel, PlanModel, ClientModel, EstablishmentModel
from domain.entities import User, Plan, Client, Establishment


class EntityMapper:
    """Classe com métodos estáticos para converter ORM em entidades"""
    
    @staticmethod
    def user_to_entity(user_model: UserModel) -> User:
        """Converte UserModel em User entity"""
        return User(
            id=user_model.uuid,
            user_name=user_model.user_name,
            email=user_model.email,
            phone_number=user_model.phone_number,
            password_hash=user_model.password_hash,
            role=user_model.role,
            active_status=user_model.active_status,
            img_url=user_model.img_url,
            created_at=user_model.create_in,
            updated_at=user_model.update_in
        )
    
    @staticmethod
    def plan_to_entity(plan_model: PlanModel) -> Plan:
        """Converte PlanModel em Plan entity"""
        return Plan(
            id=plan_model.id,
            type_plan=plan_model.type_plan,
            basic_price=plan_model.basic_price,
            max_employee=plan_model.max_employee,
            allow_stock=plan_model.allow_stock,
            allow_advanced_analysis=plan_model.allow_advanced_analysis
        )
    
    @staticmethod
    def client_to_entity(client_model: ClientModel) -> Client:
        """Converte ClientModel em Client entity"""
        user = EntityMapper.user_to_entity(client_model.user)
        plan = EntityMapper.plan_to_entity(client_model.plan)
        
        return Client(
            id=client_model.id,
            user=user,
            plan=plan,
            stripe_customer_id=client_model.stripe_customer_id
        )
    
    @staticmethod
    def establishment_to_entity(establishment_model: EstablishmentModel) -> Establishment:
        """Converte EstablishmentModel em Establishment entity"""
        client = EntityMapper.client_to_entity(establishment_model.client)
        
        return Establishment(
            id=establishment_model.uuid,
            client=client,
            stripe_subscription_id=establishment_model.stripe_subscription_id,
            waba_id=establishment_model.waba_id,
            whatsapp_business_token=establishment_model.whatsapp_business_token,
            google_calendar_access_token=establishment_model.google_calendar_access_token,
            google_calendar_refresh_token=establishment_model.google_calendar_refresh_token,
            google_calendar_expiry=establishment_model.google_calendar_expiry,
            google_calendar_id=establishment_model.google_calendar_id,
            establishment_name=establishment_model.establishment_name,
            cnpj=establishment_model.cnpj,
            chatbot_phone_number=establishment_model.chatbot_phone_number,
            address=establishment_model.address,
            img_url=establishment_model.img_url,
            subscription_date=establishment_model.subscription_date,
            due_date=establishment_model.due_date,
            trial_active=establishment_model.trial_active
        )
