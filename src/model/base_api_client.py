import logging
import os
from openai import OpenAI

logger = logging.getLogger()

class BaseAPIClient:
    def __init__(self, token_env: str, service_name: str, base_url_env: str = None):
        self.token = os.getenv(token_env)
        self.base_url = os.getenv(base_url_env) if base_url_env else None
        self.service_name = service_name
        self._client = None

    def get_client(self):
        if self._client is None:
            if self.token:
                logger.debug(f"Получен API токен для {self.service_name}")
                if self.base_url:
                    self._client = OpenAI(api_key=self.token, base_url=self.base_url)
                else:
                    self._client = OpenAI(api_key=self.token)
                logger.info(f"Клиент {self.service_name} успешно создан")
            else:
                logger.error(f"API токен для {self.service_name} не найден!")
                self._client = None
        return self._client

    def ask(self, system_prompt: str, user_prompt: str, model: str, response_format=None):
        client = self.get_client()
        if client is None:
            raise ValueError(f"Клиент {self.service_name} не инициализирован")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        if response_format:
            completion = client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_format,
            )
        else:
            completion = client.beta.chat.completions.parse(
                model=model,
                messages=messages,
            )
        return completion
