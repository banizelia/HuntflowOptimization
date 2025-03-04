import logging
from typing import Type, TypeVar

from src.model.base_api_client import BaseAPIClient

T = TypeVar("T")
logger = logging.getLogger()

openai_client = BaseAPIClient(
    token_env="CHATGPT_API_TOKEN",
    service_name="OpenAI"
)

def ask_gpt(system_prompt: str, user_prompt: str, response_format: Type[T], model: str = "gpt-4o") -> T:
    logger.info(f"Формируется запрос к {model} для GPT")
    completion = openai_client.ask(system_prompt, user_prompt, model, response_format=response_format)
    answer = completion.choices[0].message.parsed
    logger.debug(f"Ответ от {model} получен: {answer}")
    return answer
