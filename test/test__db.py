from datetime import datetime
from models import (
    AppointmentStatus,
    Client,
    Customer,
    Employee,
    Establishment,
    MarketingMessage,
    MovementType,
    Payment,
    PaymentStatus,
    PaymentType,
    Plan,
    Scheduling,
    Service,
    StockMovement,
    StockProduct,
    TypePlan,
    User,
    UserRole,
)

def test_user_model(db_session, user_db):
    #Create
    db_session.add(user_db)
    db_session.flush()
    assert user_db.id is not None
    assert user_db.user_name == "Test User"
    assert user_db.email == "test@example.com"
    assert user_db.role == UserRole.ADMIN
    assert user_db.active_status is True

    #Read
    read = db_session.query(User).filter_by(user_name = "Test User").first()
    assert read is not None
    assert read.id == user_db.id

    #Update
    db_session.query(User).filter_by(user_name = "Test User").update({"user_name": "Test User Update"})
    db_session.flush()
    assert user_db.user_name == "Test User Update"

    #Delete
    db_session.delete(user_db)
    db_session.flush()
    result = db_session.query(User).filter_by(user_name = "Test User Update").first()
    assert result is None

def test_plan_model(db_session, plan_db):
    #Create
    db_session.add(plan_db)
    db_session.flush()
    assert plan_db.id is not None
    assert plan_db.type_plan == TypePlan.SILVER
    assert float(plan_db.basic_price) == 15.9
    assert plan_db.max_employee == 3
    assert plan_db.allow_stock is False
    assert plan_db.allow_advanced_analysis is True

    #Read
    read = db_session.query(Plan).filter_by(id = plan_db.id).first()
    assert read is not None
    assert read.id == plan_db.id

    #Update
    db_session.query(Plan).filter_by(id = plan_db.id).update({"type_plan": TypePlan.GOLD})
    db_session.flush()
    assert plan_db.type_plan == TypePlan.GOLD

    #Delete
    db_session.delete(plan_db)
    db_session.flush()
    result = db_session.query(Plan).filter_by(id = plan_db.id).first()
    assert result is None

def test_client_model(db_session, client_db):
    client, user, plan = client_db

    #Create
    db_session.add(client)
    db_session.flush()
    assert client.id is not None
    assert client.users_id == user.id
    assert client.plans_id == plan.id

    #Read
    read = db_session.query(Client).filter_by(id=client.id).first()
    assert read is not None
    assert read.id == client.id

    #Delete
    db_session.delete(client)
    db_session.flush()
    result = db_session.query(Client).filter_by(id=client.id).first()
    assert result is None

def test_establishment_model(db_session, establishment_db):
    establishment, client = establishment_db
    
    #Create
    db_session.add(establishment)
    db_session.flush()
    assert establishment.id is not None
    assert establishment.clients_id == client.id
    assert establishment.establishment_name == "Test Establishment"
    assert establishment.cnpj == "12123123000122"
    assert establishment.chatbot_phone_number == "5521990032455"
    assert establishment.address == "Avenida Test Rua Test 1"
    assert establishment.due_date == datetime(2030, 2, 11)
    assert establishment.trial_active == False

    #Read
    read = db_session.query(Establishment).filter_by(id=establishment.id).first()
    assert read is not None
    assert read.id == establishment.id

    #Update
    db_session.query(Establishment).filter_by(id=establishment.id).update({"establishment_name": "Test Establishment Updated"})
    db_session.flush()
    assert establishment.establishment_name == "Test Establishment Updated"

    #Delete
    db_session.delete(establishment)
    db_session.flush()
    result = db_session.query(Establishment).filter_by(id=establishment.id).first()
    assert result is None

def test_customer_model(db_session, customer_db):
    customer, establishment = customer_db

    # Create
    db_session.add(customer)
    db_session.flush()
    assert customer.id is not None
    assert customer.customer_name == "Test Customer"
    assert customer.phone_number == "5511980657662"
    assert customer.establishments_id == establishment.id

    # Read
    read = db_session.query(Customer).filter_by(id=customer.id).first()
    assert read is not None
    assert read.id == customer.id

    # Update
    db_session.query(Customer).filter_by(id=customer.id).update({"customer_name": "Test Customer Updated"})
    db_session.flush()
    assert customer.customer_name == "Test Customer Updated"

    # Delete
    db_session.delete(customer)
    db_session.flush()
    result = db_session.query(Customer).filter_by(id=customer.id).first()
    assert result is None

def test_employee_model(db_session, employee_db):
    employee, user, establishment = employee_db

    # Create
    db_session.add(employee)
    db_session.flush()
    assert employee.id is not None
    assert employee.users_id == user.id
    assert employee.establishments_id == establishment.id
    assert employee.percentage_commission == 0.07
    assert employee.available_hours == {"hour_able": "10:00am - 4:00pm", "days_able": "Monday - Friday"}

    # Read
    read = db_session.query(Employee).filter_by(id=employee.id).first()
    assert read is not None
    assert read.id == employee.id

    # Update
    db_session.query(Employee).filter_by(id=employee.id).update({"percentage_commission": 0.10})
    db_session.flush()
    assert employee.percentage_commission == 0.10

    # Delete
    db_session.delete(employee)
    db_session.flush()
    result = db_session.query(Employee).filter_by(id=employee.id).first()
    assert result is None

def test_marketing_model(db_session, marketing_db):
    marketing_message, establishment = marketing_db

    # Create
    db_session.add(marketing_message)
    db_session.flush()
    assert marketing_message.id is not None
    assert marketing_message.establishments_id == establishment.id
    assert marketing_message.title == "Tittle Test"
    assert marketing_message.content == "Content Test"

    # Read
    read = db_session.query(MarketingMessage).filter_by(id=marketing_message.id).first()
    assert read is not None
    assert read.id == marketing_message.id

    # Update
    db_session.query(MarketingMessage).filter_by(id=marketing_message.id).update({"title": "Tittle Test Updated"})
    db_session.flush()
    assert marketing_message.title == "Tittle Test Updated"

    # Delete
    db_session.delete(marketing_message)
    db_session.flush()
    result = db_session.query(MarketingMessage).filter_by(id=marketing_message.id).first()
    assert result is None

def test_payment_model(db_session, payment_db):
    payment, establishment = payment_db

    # Create
    db_session.add(payment)
    db_session.flush()
    assert payment.id is not None
    assert payment.establishments_id == establishment.id
    assert float(payment.valor) == 99.90
    assert payment.payment_day == datetime(2030, 1, 1, 10, 0, 0)
    assert payment.payment_status == PaymentStatus.PENDING
    assert payment.payment_type == PaymentType.MONTHLY_SUBSCRIPTION
    assert payment.employee_quantity == 5
    assert payment.gateway_transaction_id == "GTX123456"

    # Read
    read = db_session.query(Payment).filter_by(id=payment.id).first()
    assert read is not None
    assert read.id == payment.id

    # Update
    db_session.query(Payment).filter_by(id=payment.id).update({"payment_status": PaymentStatus.APPROVED})
    db_session.flush()
    assert payment.payment_status == PaymentStatus.APPROVED

    # Delete
    db_session.delete(payment)
    db_session.flush()
    result = db_session.query(Payment).filter_by(id=payment.id).first()
    assert result is None

def test_product_model(db_session, stock_product_db):
    stock_product, establishment = stock_product_db

    # Create
    db_session.add(stock_product)
    db_session.flush()
    assert stock_product.id is not None
    assert stock_product.establishments_id == establishment.id
    assert stock_product.product_name == "Test Product"
    assert stock_product.quantity == 100
    assert float(stock_product.price) == 25.50

    # Read
    read = db_session.query(StockProduct).filter_by(id=stock_product.id).first()
    assert read is not None
    assert read.id == stock_product.id

    # Update
    db_session.query(StockProduct).filter_by(id=stock_product.id).update({"product_name": "Test Product Updated"})
    db_session.flush()
    assert stock_product.product_name == "Test Product Updated"

    # Delete
    db_session.delete(stock_product)
    db_session.flush()
    result = db_session.query(StockProduct).filter_by(id=stock_product.id).first()
    assert result is None

def test_movement_product_model(db_session, stock_movement_db):
    stock_movement, stock_product, _ = stock_movement_db

    # Create
    db_session.add(stock_movement)
    db_session.flush()
    assert stock_movement.id is not None
    assert stock_movement.stock_products_id == stock_product.id
    assert stock_movement.movement_type == MovementType.INPUT
    assert stock_movement.quantity == 50
    assert stock_movement.date == datetime(2030, 1, 2, 15, 0, 0)

    # Read
    read = db_session.query(StockMovement).filter_by(id=stock_movement.id).first()
    assert read is not None
    assert read.id == stock_movement.id

    # Update
    db_session.query(StockMovement).filter_by(id=stock_movement.id).update({"quantity": 75})
    db_session.flush()
    assert stock_movement.quantity == 75

    # Delete
    db_session.delete(stock_movement)
    db_session.flush()
    result = db_session.query(StockMovement).filter_by(id=stock_movement.id).first()
    assert result is None

def test_service_model(db_session, service_db):
    service, establishment = service_db

    # Create
    db_session.add(service)
    db_session.flush()
    assert service.id is not None
    assert service.establishments_id == establishment.id
    assert service.service_name == "Test Service"
    assert service.description_service == "Test Description"
    assert service.time_duration == 30
    assert float(service.price) == 50.00
    assert service.active is True

    # Read
    read = db_session.query(Service).filter_by(id=service.id).first()
    assert read is not None
    assert read.id == service.id

    # Update
    db_session.query(Service).filter_by(id=service.id).update({"service_name": "Test Service Update"})
    db_session.flush()
    assert service.service_name == "Test Service Update"

    # Delete
    db_session.delete(service)
    db_session.flush()
    result = db_session.query(Service).filter_by(id=service.id).first()
    assert result is None

def test_scheduling_model(db_session, scheduling_db):
    scheduling, establishment, employee, customer, service = scheduling_db

    # Create
    db_session.add(scheduling)
    db_session.flush()
    assert scheduling.id is not None
    assert scheduling.establishments_id == establishment.id
    assert scheduling.employees_id == employee.id
    assert scheduling.customers_id == customer.id
    assert scheduling.services_id == service.id
    assert scheduling.appointment_date == datetime(2030, 3, 10, 14, 0, 0)
    assert scheduling.appointment_status == AppointmentStatus.SCHEDULED
    assert scheduling.notification_sent is False

    # Read
    read = db_session.query(Scheduling).filter_by(id=scheduling.id).first()
    assert read is not None
    assert read.id == scheduling.id

    # Update
    db_session.query(Scheduling).filter_by(id=scheduling.id).update({"appointment_status": AppointmentStatus.CONFIRMED})
    db_session.flush()
    assert scheduling.appointment_status == AppointmentStatus.CONFIRMED

    # Delete
    db_session.delete(scheduling)
    db_session.flush()
    result = db_session.query(Scheduling).filter_by(id=scheduling.id).first()
    assert result is None