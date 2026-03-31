from config import settings
import aiohttp
from sqlalchemy.orm import Session

from domain.entities import Context
from infra.repository import ContextRepository
from middleware.state_machine import StateMachine
from utils.enum import MachineAnwser
from utils.value_object.whatsapp_h import WhatsappProcessHelper


class WhatsappService:

    @staticmethod
    def _resolve_recipient(state_machine: StateMachine, context: Context) -> tuple[str, str, str]:
        establishment = state_machine.establishment_repository.get_by_internal_id(context.establishments_id)
        if establishment is None:
            raise ValueError("Establishment not found for the provided context")

        customer = None
        if context.customers_id:
            customer = state_machine.customer_repository.get_by_internal_id(context.customers_id)

        chatbot_phone_number = establishment.chatbot_phone_number
        wa_id = (customer.wa_id if customer and customer.wa_id else None) or context.phone_number
        token = establishment.whatsapp_business_token

        if not chatbot_phone_number:
            raise ValueError("Establishment does not have a chatbot phone number")

        if not token:
            raise ValueError("Establishment does not have a WhatsApp token")

        if not wa_id:
            raise ValueError("Recipient wa_id/phone number not available")

        return chatbot_phone_number, wa_id, token

    @staticmethod
    async def get_permanent_token(code: str) -> str:
        url = f"https://graph.facebook.com/{settings.whatsapp_app_version}/oauth/access_token"
        params = {
            "client_id": settings.whatsapp_app_id,
            "client_secret": settings.whatsapp_app_secret,
            "code": code,
        }

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if "error" in data:
                    raise ValueError(f"Meta API error: {data['error'].get('message')}")
                token = data.get("access_token")
                if not token:
                    raise ValueError("Meta API did not return an access_token")
                return token

    @staticmethod
    async def subscribe_webhook(waba_id: str, token: str):
        url = f"https://graph.facebook.com/{settings.whatsapp_app_version}/{waba_id}/subscribed_apps"
        headers = {"Authorization": f"Bearer {token}"}

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if "error" in data:
                    raise ValueError(f"Meta API error: {data['error'].get('message')}")

    @staticmethod
    async def unsubscribe_webhook(waba_id: str, token: str):
        url = f"https://graph.facebook.com/{settings.whatsapp_app_version}/{waba_id}/subscribed_apps"
        headers = {"Authorization": f"Bearer {token}"}

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.delete(url, headers=headers) as resp:
                resp.raise_for_status()

                if resp.content_length == 0 or resp.status == 204:
                    return None

                data = await resp.json()
                if "error" in data:
                    raise ValueError(f"Meta API error: {data['error'].get('message')}")

                return data

    @staticmethod
    async def process_message(context: Context, message: str, db: Session) -> MachineAnwser:
        state_machine = StateMachine(context=context, message=message, db=db)
        answer = WhatsappProcessHelper.dispatch_answer(state_machine, context)

        context = WhatsappProcessHelper.update_context(context, answer)
        context_repository = ContextRepository(db)
        if context.id is not None:
            context_repository.update(context)
        else:
            context_repository.create(context)

        chatbot_phone_number, wa_id, token = WhatsappService._resolve_recipient(state_machine, context)
        await WhatsappService.send_message(
            chatbot_phone_number=chatbot_phone_number,
            wa_id=wa_id,
            message=answer.anwser,
            token=token,
        )

        return answer

    @staticmethod
    async def send_message(chatbot_phone_number: str, wa_id: str, message: str, token: str):
        if not all([chatbot_phone_number, wa_id, message, token]):
            raise ValueError("Parâmetros obrigatórios não fornecidos")

        url = f"https://graph.facebook.com/{settings.whatsapp_app_version}/{chatbot_phone_number}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": wa_id,
            "type": "text",
            "text": message,
        }

        timeout = aiohttp.ClientTimeout(total=4)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if "error" in data:
                    raise ValueError(f"Meta API error: {data['error'].get('message')}")
                return data