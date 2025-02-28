import logging
import os

from openai import OpenAI

from src.model.candidate_evaluation_answer import CandidateEvaluationAnswer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

_client = None


def get_client():
    global _client
    if _client is None:
        token = os.getenv('CHATGPT_API_TOKEN')
        if token:
            logger.debug("Получен API токен для ChatGPT")
            _client = OpenAI(api_key=token)
            logger.info("Клиент OpenAI успешно создан")
        else:
            logger.error("API токен для ChatGPT не найден!")
            _client = None
    return _client


def ask_gpt(system_prompt: str, user_prompt: str) -> CandidateEvaluationAnswer:
    logger.info("Формируется запрос к GPT")

    completion = get_client().beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=CandidateEvaluationAnswer,
    )

    answer = completion.choices[0].message.parsed
    logger.debug("Ответ от GPT получен: %s", answer)
    return answer
