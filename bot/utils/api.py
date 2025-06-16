import aiohttp
import os

from dotenv import load_dotenv

load_dotenv()

class Api:
    def __init__(self) -> None:
        self.domain = os.getenv("SERVER_DOMAIN")
        self.admin_username = os.getenv("ADMIN_USERNAME")
        self.admin_password = os.getenv("ADMIN_PASSWORD")
        self.bearer_token = self.get_token()
        
    async def get_token(self):
        url = f"{self.domain}/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "password",
            "username": self.admin_username,
            "password": self.admin_password,
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise aiohttp.ClientResponseError(
                        request_info=resp.request_info,
                        history=resp.history,
                        status=resp.status,
                        message=f"Auth failed: {error_text}",
                        headers=resp.headers
                    )

                resp_data = await resp.json()
                return resp_data["access_token"]
            
    
