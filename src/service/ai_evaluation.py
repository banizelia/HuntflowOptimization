import logging

from src.api_clients.huntflow_api import (
    get_resume,
    get_vacancy_desc,
    get_applicant,
)
from src.api_clients.openai_api import ask_gpt
from src.service.formatting.resume_formatter import format_resume
from src.service.formatting.vacancy_formatter import format_vacancy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def evaluate_candidate(c_id: int, vacancy_id: int):
    full_resume = get_formatted_full_resume(c_id)
    vacancy_description = get_formatted_vacancy(vacancy_id)

    logger.info("Отправка запроса в GPT для кандидата %s", c_id)
    answer = ask_gpt(vacancy_description, full_resume)

    logger.info("Получен ответ GPT для кандидата %s", c_id)
    logger.debug("Ответ GPT: target_stage: %s, comment: %s", answer.target_stage, answer.comment)

    return answer


def get_formatted_full_resume(c_id):
    applicant = get_applicant(c_id)
    external_ids = [item for item in applicant.get('external', [])]

    external_ids.sort(key=lambda x: x['updated'], reverse=True)

    logger.debug("Найдено %d резюме для кандидата %s", len(external_ids), c_id)

    # Берем только два последних резюме
    external_ids = external_ids[:2]

    full_resume = ''
    for i, resume_data in enumerate(external_ids):
        resume_id = resume_data['id']
        logger.info("Обработка резюме %d с ID: %s для кандидата %s", i, resume_id, c_id)
        resume = get_resume(c_id, resume_id)

        logger.debug("Получено резюме %d для кандидата %s: %s", i, c_id, resume)
        full_resume += f"Резюме {i} \n\n {format_resume(resume)} \n\n"

    return full_resume


def get_formatted_vacancy(vacancy_id):
    vac = get_vacancy_desc(vacancy_id)
    logger.info("Получено описание вакансии для ID: %s", vacancy_id)
    vac = format_vacancy(vac)
    logger.debug("Отформатированное описание вакансии: %s", vac)
    return vac


