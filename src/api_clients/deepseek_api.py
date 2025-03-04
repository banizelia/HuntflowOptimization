import logging

from src.model.base_api_client import BaseAPIClient

logger = logging.getLogger()

deepseek_client = BaseAPIClient(
    token_env="DEEPSEEK_API_TOKEN",
    base_url_env="DEEPSEEK_BASE_URL",
    service_name="Deepseek"
)


def ask_deepseek(system_prompt: str, user_prompt: str, model: str = "deepseek-chat") -> str:
    logger.info(f"Формируется запрос к {model} для Deepseek")
    completion = deepseek_client.ask(system_prompt, user_prompt, model)
    answer = completion.choices[0].message.content
    logger.debug(f"Ответ от {model} получен: {answer}")
    return answer
