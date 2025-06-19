import aiohttp
import os

from aiohttp.web import HTTPUnauthorized, HTTPConflict
from dotenv import load_dotenv
from typing import Union

load_dotenv()

class Api:
    def __init__(self) -> None:
        self.domain = os.getenv("SERVER_DOMAIN")
        self.admin_username = os.getenv("ADMIN_USERNAME")
        self.admin_password = os.getenv("ADMIN_PASSWORD")
        self.bearer_token = None

    async def init(self) -> None:
        self.bearer_token = await self.get_token()
        
    async def get_token(self):
        url = f"{self.domain}/api/admin/token"
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
            
    async def get_stats(self):
        try:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}"
            }
            url = f"{self.domain}/api/system"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise aiohttp.ClientResponseError(
                            request_info=resp.request_info,
                            history=resp.history,
                            status=resp.status,
                            message=f"Error when get server stats: {error_text}",
                            headers=resp.headers
                        )
                    return await resp.json()
        except HTTPUnauthorized:
            await self.init()
            
    async def add_user_template(self, name: str, data_limit: int = 0, expire_duration: int = 0, inbounds: dict = None):
        """
        Добавляет новый шаблон пользователя.

        :param name: Имя шаблона (до 64 символов).
        :param data_limit: Лимит данных в байтах (>= 0).
        :param expire_duration: Продолжительность истечения в секундах (>= 0).
        :param inbounds: Словарь протоколов и их входящих тегов. Пустой означает все входящие.
                         Пример: {"vless": ["VLESS_INBOUND"], "vmess": ["VMESS_INBOUND"]}
        :return: Ответ в формате JSON.
        """
        try:
            if inbounds is None:
                inbounds = {}

            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            url = f"{self.domain}/api/user_template"
            payload = {
                "name": name,
                "data_limit": data_limit,
                "expire_duration": expire_duration,
                "inbounds": inbounds
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise aiohttp.ClientResponseError(
                            request_info=resp.request_info,
                            history=resp.history,
                            status=resp.status,
                            message=f"Error when adding user template: {error_text}",
                            headers=resp.headers
                        )
                    return await resp.json()
        except HTTPUnauthorized:
            await self.init()

    async def get_user_templates(self, offset: int = 0, limit: int = 100):
        """
        Получает список шаблонов пользователей с опциональной пагинацией.

        :param offset: Смещение.
        :param limit: Максимальное количество для получения.
        :return: Список шаблонов пользователей в формате JSON.
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Accept": "application/json"
            }
            url = f"{self.domain}/api/user_template?offset={offset}&limit={limit}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise aiohttp.ClientResponseError(
                            request_info=resp.request_info,
                            history=resp.history,
                            status=resp.status,
                            message=f"Error when getting user templates: {error_text}",
                            headers=resp.headers
                        )
                    return await resp.json()
        except HTTPUnauthorized:
            await self.init()

    async def check_user_template_exists(self, name: str) -> bool:
        templates = await self.get_user_templates(offset=0, limit=1000000)
        for template in templates:
            if template["name"] == name:
                return True
        return False
    
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
        try:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
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

            url = f"{self.domain}/api/user"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Failed to add user: {response.status} {error_text}")
        except HTTPUnauthorized:
            await self.init()