import os
import asyncio
import aiohttp
from typing import Union
from dotenv import load_dotenv
from aiohttp.web import HTTPConflict

load_dotenv()

class Api:
    def __init__(self) -> None:
        self.domain = os.getenv("SERVER_DOMAIN")
        self.admin_username = os.getenv("ADMIN_USERNAME")
        self.admin_password = os.getenv("ADMIN_PASSWORD")
        self.bearer_token = None
        self._token_lock = asyncio.Lock()

    async def init(self) -> None:
        async with self._token_lock:
            if self.bearer_token is not None:
                return
            self.bearer_token = await self.get_token()

    async def get_token(self):
        url = f"{self.domain}/api/admin/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
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

    async def _request(self, method, url, headers=None, **kwargs):
        """
        Универсальный метод для запросов с автоматическим обновлением токена при 401.
        """
        if headers is None:
            headers = {}

        # Добавляем токен
        headers["Authorization"] = f"Bearer {self.bearer_token}"

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, **kwargs) as resp:
                if resp.status == 401:
                    # Токен истёк, обновляем
                    async with self._token_lock:
                        # Обновляем токен
                        self.bearer_token = await self.get_token()
                    # Повторяем запрос с новым токеном
                    headers["Authorization"] = f"Bearer {self.bearer_token}"
                    async with session.request(method, url, headers=headers, **kwargs) as resp2:
                        if resp2.status != 200:
                            error_text = await resp2.text()
                            raise aiohttp.ClientResponseError(
                                request_info=resp2.request_info,
                                history=resp2.history,
                                status=resp2.status,
                                message=f"Request failed after token refresh: {error_text}",
                                headers=resp2.headers
                            )
                        return await resp2.json()

                elif resp.status != 200:
                    error_text = await resp.text()
                    raise aiohttp.ClientResponseError(
                        request_info=resp.request_info,
                        history=resp.history,
                        status=resp.status,
                        message=f"Request failed: {error_text}",
                        headers=resp.headers
                    )
                return await resp.json()

    async def get_stats(self):
        url = f"{self.domain}/api/system"
        return await self._request("GET", url)

    async def add_user_template(self, name: str, data_limit: int = 0, expire_duration: int = 0, inbounds: dict = None):
        if inbounds is None:
            inbounds = {}

        url = f"{self.domain}/api/user_template"
        payload = {
            "name": name,
            "data_limit": data_limit,
            "expire_duration": expire_duration,
            "inbounds": inbounds
        }
        headers = {"Content-Type": "application/json"}
        return await self._request("POST", url, headers=headers, json=payload)

    async def get_user_templates(self, offset: int = 0, limit: int = 100):
        url = f"{self.domain}/api/user_template?offset={offset}&limit={limit}"
        headers = {"Accept": "application/json"}
        return await self._request("GET", url, headers=headers)

    async def add_user(
        self,
        username: Union[str, int],
        status: str = "active",
        expire: int = 0,
        data_limit: int = 0,
        data_limit_reset_strategy: str = "no_reset",
        proxies: dict = {"vless": {}},
        inbounds: dict = {"vless": ["VLESS TCP REALITY"]},
        note: str = "",
        on_hold_timeout: str = None,
        on_hold_expire_duration: int = 0,
        next_plan: dict = None
    ):
        proxies = proxies or {"vless": {}}
        inbounds = inbounds or {"vless": ["VLESS TCP REALITY"]}

        url = f"{self.domain}/api/user"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = {
            "username": str(username),
            "status": status,
            "expire": expire,
            "data_limit": data_limit,
            "data_limit_reset_strategy": data_limit_reset_strategy,
            "proxies": proxies,
            "inbounds": inbounds,
            "note": note,
            "on_hold_expire_duration": on_hold_expire_duration
        }
        if on_hold_timeout:
            payload["on_hold_timeout"] = on_hold_timeout

        if next_plan is not None:
            payload["next_plan"] = next_plan

        try:
            return await self._request("POST", url, headers=headers, json=payload)
        except aiohttp.ClientResponseError as e:
            if e.status == 409:
                raise HTTPConflict()
            else:
                raise