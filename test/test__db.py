from datetime import datetime
from models import (
    User, UserRole, Plan, TypePlan, Client, Establishment, Customer, Employee,
    MarketingMessage, Payment, PaymentType, PaymentStatus, Service, Scheduling,
    AppointmentStatus, StockProduct, StockMovement, MovementType
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

    