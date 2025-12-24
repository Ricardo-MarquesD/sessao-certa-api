import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from domain.entities import Scheduling
from domain.entities import Establishment
from domain.entities import Employee
from domain.entities import Customer
from domain.entities import Service
from domain.entities import Client
from domain.entities import User
from domain.entities import Plan
from utils.enum import UserRole, TypePlan, AppointmentStatus


class TestSchedulingEntity:
    """Testes unitários para a entidade Scheduling"""
    
    @pytest.fixture
    def mock_establishment(self):
        """Fixture para criar um establishment de teste"""
        user = User(
            id="user-client-123",
            user_name="João Silva",
            email="joao@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.CLIENT,
            active_status=True,
            img_url=None,
            created_at=None,
            updated_at=None
        )
        
        plan = Plan(
            id=1,
            type_plan=TypePlan.BRONZE,
            basic_price=Decimal("29.90"),
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        
        client = Client(
            id=1,
            user=user,
            plan=plan
        )
        
        establishment = Establishment(
            id="est-123",
            client=client,
            establishment_name="Barbearia João",
            cnpj="12345678901234",
            chatbot_phone_number="11987654321",
            address="Rua Teste, 123",
            img_url=None,
            subscription_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            trial_active=False
        )
        
        return establishment
    
    @pytest.fixture
    def mock_employee(self, mock_establishment):
        """Fixture para criar um employee de teste"""
        user = User(
            id="user-emp-123",
            user_name="Maria Silva",
            email="maria@example.com",
            phone_number="11987654321",
            password_hash="$2b$12$hashedpassword",
            role=UserRole.EMPLOYEE,
            active_status=True,
            img_url=None,
            created_at=None,
            updated_at=None
        )
        
        return Employee(
            id="emp-123",
            user=user,
            establishment=mock_establishment,
            percentage_commission=Decimal("10.00"),
            available_hours=None
        )
    
    @pytest.fixture
    def mock_customer(self, mock_establishment):
        """Fixture para criar um customer de teste"""
        return Customer(
            id="cust-123",
            establishment=mock_establishment,
            customer_name="Carlos Souza",
            phone_number="11999887766"
        )
    
    @pytest.fixture
    def mock_service(self, mock_establishment):
        """Fixture para criar um service de teste"""
        return Service(
            id="srv-123",
            establishment=mock_establishment,
            service_name="Corte de Cabelo",
            time_duration=30,
            price=Decimal("35.00"),
            description_service=None,
            active=True
        )
    
    def test_create_scheduling_with_valid_data(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa criação de agendamento com dados válidos"""
        appointment_date = datetime.now() + timedelta(hours=2)
        
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.SCHEDULED,
            appointment_date=appointment_date,
            notification_sent=False,
            created_at=datetime.now()
        )
        
        assert scheduling.appointment_status == AppointmentStatus.SCHEDULED
        assert scheduling.notification_sent is False
    
    def test_create_scheduling_with_invalid_establishment_raises_error(self, mock_employee, mock_customer, mock_service):
        """Testa que establishment inválido levanta erro"""
        with pytest.raises(ValueError, match="Establishment must be an Establishment instance"):
            Scheduling(
                id="sch-123",
                establishment="invalid",
                employee=mock_employee,
                customer=mock_customer,
                service=mock_service,
                appointment_status=AppointmentStatus.SCHEDULED,
                appointment_date=None,
                notification_sent=None,
                created_at=None
            )
    
    def test_create_scheduling_with_invalid_employee_raises_error(self, mock_establishment, mock_customer, mock_service):
        """Testa que employee inválido levanta erro"""
        with pytest.raises(ValueError, match="Employee must be an Employee instance"):
            Scheduling(
                id="sch-123",
                establishment=mock_establishment,
                employee="invalid",
                customer=mock_customer,
                service=mock_service,
                appointment_status=AppointmentStatus.SCHEDULED,
                appointment_date=None,
                notification_sent=None,
                created_at=None
            )
    
    def test_create_scheduling_with_invalid_customer_raises_error(self, mock_establishment, mock_employee, mock_service):
        """Testa que customer inválido levanta erro"""
        with pytest.raises(ValueError, match="Customer must be a Customer instance"):
            Scheduling(
                id="sch-123",
                establishment=mock_establishment,
                employee=mock_employee,
                customer="invalid",
                service=mock_service,
                appointment_status=AppointmentStatus.SCHEDULED,
                appointment_date=None,
                notification_sent=None,
                created_at=None
            )
    
    def test_create_scheduling_with_invalid_service_raises_error(self, mock_establishment, mock_employee, mock_customer):
        """Testa que service inválido levanta erro"""
        with pytest.raises(ValueError, match="Service must be a Service instance"):
            Scheduling(
                id="sch-123",
                establishment=mock_establishment,
                employee=mock_employee,
                customer=mock_customer,
                service="invalid",
                appointment_status=AppointmentStatus.SCHEDULED,
                appointment_date=None,
                notification_sent=None,
                created_at=None
            )
    
    def test_create_scheduling_with_invalid_status_raises_error(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa que appointment_status inválido levanta erro"""
        with pytest.raises(ValueError, match="Appointment status must be an AppointmentStatus enum"):
            Scheduling(
                id="sch-123",
                establishment=mock_establishment,
                employee=mock_employee,
                customer=mock_customer,
                service=mock_service,
                appointment_status="INVALID",
                appointment_date=None,
                notification_sent=None,
                created_at=None
            )
    
    def test_can_cancel_returns_true_for_scheduled_status(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa can_cancel() retorna True para status SCHEDULED"""
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.SCHEDULED,
            appointment_date=None,
            notification_sent=None,
            created_at=None
        )
        
        assert scheduling.can_cancel() is True
    
    def test_can_cancel_returns_true_for_confirmed_status(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa can_cancel() retorna True para status CONFIRMED"""
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.CONFIRMED,
            appointment_date=None,
            notification_sent=None,
            created_at=None
        )
        
        assert scheduling.can_cancel() is True
    
    def test_can_cancel_returns_false_for_completed_status(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa can_cancel() retorna False para status COMPLETED"""
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.COMPLETED,
            appointment_date=None,
            notification_sent=None,
            created_at=None
        )
        
        assert scheduling.can_cancel() is False
    
    def test_can_cancel_returns_false_for_cancelled_status(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa can_cancel() retorna False para status CANCELLED"""
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.CANCELED,
            appointment_date=None,
            notification_sent=None,
            created_at=None
        )
        
        assert scheduling.can_cancel() is False
    
    def test_mark_notification_sent_sets_flag_to_true(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa mark_notification_sent() define flag como True"""
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.SCHEDULED,
            appointment_date=None,
            notification_sent=False,
            created_at=None
        )
        
        scheduling.mark_notification_sent()
        
        assert scheduling.notification_sent is True
    
    def test_calculate_end_time_adds_service_duration(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa calculate_end_time() adiciona duração do serviço"""
        appointment_date = datetime(2025, 12, 24, 10, 0, 0)
        
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.SCHEDULED,
            appointment_date=appointment_date,
            notification_sent=False,
            created_at=None
        )
        
        end_time = scheduling.calculate_end_time()
        
        # Serviço tem 30 minutos
        expected_end = datetime(2025, 12, 24, 10, 30, 0)
        assert end_time == expected_end
    
    def test_calculate_end_time_with_none_appointment_date_raises_error(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa calculate_end_time() com appointment_date None levanta erro"""
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.SCHEDULED,
            appointment_date=None,
            notification_sent=False,
            created_at=None
        )
        
        with pytest.raises(ValueError, match="appointment_date must be a datetime"):
            scheduling.calculate_end_time()
    
    def test_needs_notification_returns_true_within_window(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa needs_notification() retorna True dentro da janela de 20-30min"""
        # Agendamento em 25 minutos
        appointment_date = datetime.now() + timedelta(minutes=25)
        
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.SCHEDULED,
            appointment_date=appointment_date,
            notification_sent=False,
            created_at=None
        )
        
        assert scheduling.needs_notification() is True
    
    def test_needs_notification_returns_false_before_window(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa needs_notification() retorna False antes da janela"""
        # Agendamento em 40 minutos
        appointment_date = datetime.now() + timedelta(minutes=40)
        
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.SCHEDULED,
            appointment_date=appointment_date,
            notification_sent=False,
            created_at=None
        )
        
        assert scheduling.needs_notification() is False
    
    def test_needs_notification_returns_false_after_window(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa needs_notification() retorna False depois da janela"""
        # Agendamento em 10 minutos
        appointment_date = datetime.now() + timedelta(minutes=10)
        
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.SCHEDULED,
            appointment_date=appointment_date,
            notification_sent=False,
            created_at=None
        )
        
        assert scheduling.needs_notification() is False
    
    def test_needs_notification_returns_false_when_already_sent(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa needs_notification() retorna False quando já enviada"""
        # Agendamento em 25 minutos
        appointment_date = datetime.now() + timedelta(minutes=25)
        
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.SCHEDULED,
            appointment_date=appointment_date,
            notification_sent=True,  # Já enviada
            created_at=None
        )
        
        assert scheduling.needs_notification() is False
    
    def test_to_dict_returns_correct_structure(self, mock_establishment, mock_employee, mock_customer, mock_service):
        """Testa to_dict() retorna estrutura correta"""
        appointment_date = datetime(2025, 12, 24, 14, 0, 0)
        created_at = datetime(2025, 12, 20, 10, 0, 0)
        
        scheduling = Scheduling(
            id="sch-123",
            establishment=mock_establishment,
            employee=mock_employee,
            customer=mock_customer,
            service=mock_service,
            appointment_status=AppointmentStatus.SCHEDULED,
            appointment_date=appointment_date,
            notification_sent=False,
            created_at=created_at
        )
        
        scheduling_dict = scheduling.to_dict()
        
        assert scheduling_dict["id"] == "sch-123"
        assert scheduling_dict["appointment_status"] == "SCHEDULED"
        assert scheduling_dict["notification_sent"] is False
        assert "establishment" in scheduling_dict
        assert "employee" in scheduling_dict
