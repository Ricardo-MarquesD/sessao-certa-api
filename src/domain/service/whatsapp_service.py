from config import settings
import aiohttp

class WhatsappService():

    @staticmethod
    async def get_permanent_token(code:str)->str:
        url = f"https://graph.facebook.com/{settings.whatsapp_app_version}/oauth/access_token"
        params = {
            "client_id": settings.whatsapp_app_id,
            "client_secret": settings.whatsapp_app_secret,
            "code": code
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
        headers = {
            "Authorization": f"Bearer {token}"
        }

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if "error" in data:
                    raise ValueError(f"Meta API error: {data['error'].get('message')}")
                
    @staticmethod
    async def process_message():
        ...

    @staticmethod
    async def send_message(chatbot_phone_number: str, wa_id: str, message: str, token: str):
        if not all([chatbot_phone_number, wa_id, message, token]):
            raise ValueError("Parâmetros obrigatórios não fornecidos")
        
        url = f"https://graph.facebook.com/{settings.whatsapp_app_version}/{chatbot_phone_number}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": wa_id,
            "type": "text",
            "text": message
        }
        
        timeout = aiohttp.ClientTimeout(total = 4)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if "error" in data:
                    raise ValueError(f"Meta API error: {data['error'].get('message')}")
                return data