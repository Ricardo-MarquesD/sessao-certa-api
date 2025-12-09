import unittest
from datetime import datetime
from sqlalchemy import inspect
from config import Session, Base, engine, connection_test
from src.models import (
    User, UserRole, Plan, TypePlan, Client, Establishment, Customer, Employee,
    MarketingMessage, Payment, PaymentType, PaymentStatus, Service, Scheduling,
    AppointmentStatus, StockProduct, StockMovement, MovementType
)

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Testa conexão com MySQL
        connection_test(engine)
        # Remove tabelas existentes para recriar do zero
        Base.metadata.drop_all(bind=engine)
        # Cria todas as tabelas
        Base.metadata.create_all(bind=engine)
        cls.session = Session()
    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def test_create_tables(self):
        # Verifica se as tabelas foram criadas
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        self.assertGreater(len(tables), 0)

    def test_user_creation(self):
        user = User(
            user_name="Test User",
            password_hash="hashed_password",
            phone_number="123456789",
            email="test@example.com",
            role=UserRole.ADMIN,
            active_status=True
        )
        self.session.add(user)
        self.session.commit()
        self.assertIsNotNone(user.id)

    def test_plan_creation(self):
        plan = Plan(
            type_plan=TypePlan.BRONZE,
            basic_price=100.00,
            max_employee=5,
            allow_stock=False,
            allow_advanced_analysis=False
        )
        self.session.add(plan)
        self.session.commit()
        self.assertIsNotNone(plan.id)

    def test_client_relationship(self):
        # Cria User e Plan primeiro
        user = User(
            user_name="Client User",
            password_hash="hashed",
            phone_number="987654321",
            email="client@example.com",
            role=UserRole.CLIENT,
            active_status=True
        )
        plan = Plan(
            type_plan=TypePlan.SILVER,
            basic_price=200.00,
            max_employee=10,
            allow_stock=True,
            allow_advanced_analysis=False
        )
        self.session.add(user)
        self.session.add(plan)
        self.session.commit()

        client = Client(users_id=user.id, plans_id=plan.id)
        self.session.add(client)
        self.session.commit()
        self.assertIsNotNone(client.id)
        self.assertEqual(client.user.id, user.id)
        self.assertEqual(client.plan.id, plan.id)

    def test_employee_relationship(self):
        # Cria User e Establishment
        user = User(
            user_name="Employee User",
            password_hash="hashed",
            phone_number="555666777",
            email="employee@example.com",
            role=UserRole.EMPLOYEE,
            active_status=True
        )
        self.session.add(user)  # Correção: adiciona o user à sessão
        # Cria Client e Establishment
        client_user = User(user_name="Client2", password_hash="hash", phone_number="111222333", email="client2@example.com", role=UserRole.CLIENT, active_status=True)
        plan = Plan(type_plan=TypePlan.GOLD, basic_price=300.00, max_employee=20, allow_stock=True, allow_advanced_analysis=True)
        self.session.add(client_user)
        self.session.add(plan)
        self.session.commit()
        client = Client(users_id=client_user.id, plans_id=plan.id)
        self.session.add(client)
        self.session.commit()
        establishment = Establishment(
            clients_id=client.id,
            establishment_name="Test Estab",
            cnpj="12345678000123",
            chatbot_phone_number="444555666",
            address="Test Address",
            due_date=datetime(2025, 12, 31)
        )
        self.session.add(establishment)
        self.session.commit()

        employee = Employee(
            users_id=user.id,
            establishments_id=establishment.id,
            percentage_commission=10.00,
            available_hours={"monday": ["09:00-17:00"]}
        )
        self.session.add(employee)
        self.session.commit()
        self.assertIsNotNone(employee.id)
        self.assertEqual(employee.user.id, user.id)
        self.assertEqual(employee.establishment.id, establishment.id)

    def test_customer_relationship(self):
        # Cria Establishment
        client_user = User(user_name="Client3", password_hash="hash", phone_number="777888999", email="client3@example.com", role=UserRole.CLIENT, active_status=True)
        plan = Plan(type_plan=TypePlan.BRONZE, basic_price=100.00, max_employee=5, allow_stock=False, allow_advanced_analysis=False)
        self.session.add(client_user)
        self.session.add(plan)
        self.session.commit()
        client = Client(users_id=client_user.id, plans_id=plan.id)
        self.session.add(client)
        self.session.commit()
        establishment = Establishment(
            clients_id=client.id,
            establishment_name="Estab2",
            cnpj="98765432000198",
            chatbot_phone_number="333444555",
            address="Address2",
            due_date=datetime(2025, 12, 31)
        )
        self.session.add(establishment)
        self.session.commit()

        customer = Customer(phone_number="222333444", establishments_id=establishment.id)
        self.session.add(customer)
        self.session.commit()
        self.assertIsNotNone(customer.id)
        self.assertEqual(customer.establishment.id, establishment.id)

    def test_service_relationship(self):
        # Usa Establishment do teste anterior
        establishment = self.session.query(Establishment).filter_by(establishment_name="Estab2").first()
        service = Service(
            establishments_id=establishment.id,
            service_name="Haircut",
            description_service="Basic haircut",
            time_duration=30,
            price=50.00,
            active=True
        )
        self.session.add(service)
        self.session.commit()
        self.assertIsNotNone(service.id)
        self.assertEqual(service.establishment.id, establishment.id)

    def test_scheduling_relationship(self):
        # Cria Employee se não existir
        employee = self.session.query(Employee).first()
        if not employee:
            user = User(user_name="Employee User", password_hash="hashed", phone_number="555666777", email="employee@example.com", role=UserRole.EMPLOYEE, active_status=True)
            self.session.add(user)
            client_user = User(user_name="Client2", password_hash="hash", phone_number="111222333", email="client2@example.com", role=UserRole.CLIENT, active_status=True)
            plan = Plan(type_plan=TypePlan.GOLD, basic_price=300.00, max_employee=20, allow_stock=True, allow_advanced_analysis=True)
            self.session.add(client_user)
            self.session.add(plan)
            self.session.commit()
            client = Client(users_id=client_user.id, plans_id=plan.id)
            self.session.add(client)
            self.session.commit()
            establishment = Establishment(clients_id=client.id, establishment_name="Test Estab", cnpj="12345678000123", chatbot_phone_number="444555666", address="Test Address", due_date=datetime(2025, 12, 31))
            self.session.add(establishment)
            self.session.commit()
            employee = Employee(users_id=user.id, establishments_id=establishment.id, percentage_commission=10.00, available_hours={"monday": ["09:00-17:00"]})
            self.session.add(employee)
            self.session.commit()
        
        # Cria Customer se não existir
        customer = self.session.query(Customer).first()
        if not customer:
            client_user = User(user_name="Client3", password_hash="hash", phone_number="777888999", email="client3@example.com", role=UserRole.CLIENT, active_status=True)
            plan = Plan(type_plan=TypePlan.BRONZE, basic_price=100.00, max_employee=5, allow_stock=False, allow_advanced_analysis=False)
            self.session.add(client_user)
            self.session.add(plan)
            self.session.commit()
            client = Client(users_id=client_user.id, plans_id=plan.id)
            self.session.add(client)
            self.session.commit()
            establishment = Establishment(clients_id=client.id, establishment_name="Estab2", cnpj="98765432000198", chatbot_phone_number="333444555", address="Address2", due_date=datetime(2025, 12, 31))
            self.session.add(establishment)
            self.session.commit()
            customer = Customer(phone_number="222333444", establishments_id=establishment.id)
            self.session.add(customer)
            self.session.commit()
        
        # Cria Service se não existir
        service = self.session.query(Service).first()
        if not service:
            establishment = self.session.query(Establishment).filter_by(establishment_name="Estab2").first()
            if not establishment:
                # Mesmo código de criação acima
                client_user = User(user_name="Client3", password_hash="hash", phone_number="777888999", email="client3@example.com", role=UserRole.CLIENT, active_status=True)
                plan = Plan(type_plan=TypePlan.BRONZE, basic_price=100.00, max_employee=5, allow_stock=False, allow_advanced_analysis=False)
                self.session.add(client_user)
                self.session.add(plan)
                self.session.commit()
                client = Client(users_id=client_user.id, plans_id=plan.id)
                self.session.add(client)
                self.session.commit()
                establishment = Establishment(clients_id=client.id, establishment_name="Estab2", cnpj="98765432000198", chatbot_phone_number="333444555", address="Address2", due_date=datetime(2025, 12, 31))
                self.session.add(establishment)
                self.session.commit()
            service = Service(establishments_id=establishment.id, service_name="Haircut", description_service="Basic haircut", time_duration=30, price=50.00, active=True)
            self.session.add(service)
            self.session.commit()
        
        scheduling = Scheduling(
            establishments_id=employee.establishments_id,
            employees_id=employee.id,
            customers_id=customer.id,
            services_id=service.id,
            appointment_date=datetime(2025, 12, 10, 10, 0),
            appointment_status=AppointmentStatus.SCHEDULED,
            notification_sent=False
        )
        self.session.add(scheduling)
        self.session.commit()
        self.assertIsNotNone(scheduling.id)
        self.assertEqual(scheduling.employee.id, employee.id)
        self.assertEqual(scheduling.customer.id, customer.id)
        self.assertEqual(scheduling.service.id, service.id)

    def test_stock_product_relationship(self):
        establishment = self.session.query(Establishment).filter_by(establishment_name="Estab2").first()
        if not establishment:
            # Mesmo código de criação acima
            client_user = User(user_name="Client3", password_hash="hash", phone_number="777888999", email="client3@example.com", role=UserRole.CLIENT, active_status=True)
            plan = Plan(type_plan=TypePlan.BRONZE, basic_price=100.00, max_employee=5, allow_stock=False, allow_advanced_analysis=False)
            self.session.add(client_user)
            self.session.add(plan)
            self.session.commit()
            client = Client(users_id=client_user.id, plans_id=plan.id)
            self.session.add(client)
            self.session.commit()
            establishment = Establishment(
                clients_id=client.id,
                establishment_name="Estab2",
                cnpj="98765432000198",
                chatbot_phone_number="333444555",
                address="Address2",
                due_date=datetime(2025, 12, 31)
            )
            self.session.add(establishment)
            self.session.commit()
        
        stock_product = StockProduct(
            establishments_id=establishment.id,
            product_name="Shampoo",
            quantity=100,
            price=10.00
        )
        self.session.add(stock_product)
        self.session.commit()
        self.assertIsNotNone(stock_product.id)
        self.assertEqual(stock_product.establishment.id, establishment.id)

    def test_stock_movement_relationship(self):
        stock_product = self.session.query(StockProduct).first()
        if not stock_product:
            establishment = self.session.query(Establishment).filter_by(establishment_name="Estab2").first()
            if not establishment:
                # Mesmo código de criação acima
                client_user = User(user_name="Client3", password_hash="hash", phone_number="777888999", email="client3@example.com", role=UserRole.CLIENT, active_status=True)
                plan = Plan(type_plan=TypePlan.BRONZE, basic_price=100.00, max_employee=5, allow_stock=False, allow_advanced_analysis=False)
                self.session.add(client_user)
                self.session.add(plan)
                self.session.commit()
                client = Client(users_id=client_user.id, plans_id=plan.id)
                self.session.add(client)
                self.session.commit()
                establishment = Establishment(
                    clients_id=client.id,
                    establishment_name="Estab2",
                    cnpj="98765432000198",
                    chatbot_phone_number="333444555",
                    address="Address2",
                    due_date=datetime(2025, 12, 31)
                )
                self.session.add(establishment)
                self.session.commit()
            stock_product = StockProduct(
                establishments_id=establishment.id,
                product_name="Shampoo",
                quantity=100,
                price=10.00
            )
            self.session.add(stock_product)
            self.session.commit()
        
        stock_movement = StockMovement(
            stock_products_id=stock_product.id,
            movement_type=MovementType.INPUT,
            quantity=50
        )
        self.session.add(stock_movement)
        self.session.commit()
        self.assertIsNotNone(stock_movement.id)
        self.assertEqual(stock_movement.stock_product.id, stock_product.id)

    def test_payment_relationship(self):
        establishment = self.session.query(Establishment).filter_by(establishment_name="Estab2").first()
        payment = Payment(
            establishments_id=establishment.id,
            valor=200.00,
            payment_day=datetime(2025, 12, 1),
            payment_status=PaymentStatus.PENDING,
            payment_type=PaymentType.MONTHLY_SUBSCRIPTION,
            employee_quantity=5,
            gateway_transaction_id="txn123"
        )
        self.session.add(payment)
        self.session.commit()
        self.assertIsNotNone(payment.id)
        self.assertEqual(payment.establishment.id, establishment.id)

    def test_marketing_message_relationship(self):
        establishment = self.session.query(Establishment).filter_by(establishment_name="Estab2").first()
        message = MarketingMessage(
            establishments_id=establishment.id,
            title="Promo",
            content="Discount on services"
        )
        self.session.add(message)
        self.session.commit()
        self.assertIsNotNone(message.id)
        self.assertEqual(message.establishment.id, establishment.id)

if __name__ == '__main__':
    unittest.main()