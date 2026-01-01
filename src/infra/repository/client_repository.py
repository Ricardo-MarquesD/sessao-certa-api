from sqlalchemy import select
from sqlalchemy.orm import Session
from domain.entities import Client
from domain.interface import ClientInterface
from infra.models import ClientModel
from uuid import UUID

class ClientRepository(ClientInterface):
    pass