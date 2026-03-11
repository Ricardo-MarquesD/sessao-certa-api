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
    async def process_menssage():
        ...

    @staticmethod
    async def send_menssage():
        ...