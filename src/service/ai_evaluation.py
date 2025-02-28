import logging
from datetime import date

from src.api_clients.huntflow_api import (
    get_resume,
    get_vacancy_desc,
    get_applicant,
)
from src.api_clients.openai_api import ask_gpt
from src.model.candidate_evaluation_answer import CandidateEvaluationAnswer
from src.model.target_stage import TargetStage
from src.service.formatting.resume_formatter import format_resume
from src.service.formatting.vacancy_formatter import format_vacancy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def evaluate_candidate(applicant_id: int, vacancy_id: int):
    full_resume = get_formatted_full_resume(applicant_id)

    if "не готов к переезду" in full_resume:
        answer = CandidateEvaluationAnswer(
            comment="Не готов к переезду в Пермь",
            target_stage=TargetStage.RESERVE
        )
        return answer

    vacancy_description = get_formatted_vacancy(vacancy_id)

    logger.info("Отправка запроса в GPT для кандидата %s", applicant_id)

    system_prompt = (
        f"Сегодняшняя дата: {date.today()}. "
        "Ты — элитный HR-аналитик с глубоким пониманием рекрутинга и оценки кандидатов, способный с высочайшей точностью определить, подходит кандидат на вакансию или нет. "
        "При анализе каждого кандидата учитывай все нюансы: от географической привязки до уровня профессионализма, чтобы принять максимально обоснованное решение. "
        "Обязательные условия оценки:"
        "1. Технические навыки и опыт работы:"
        "   - Сопоставь опыт, навыки и географическую привязку кандидата с ключевыми требованиями вакансии."
        "   - Тщательно оцени уровень владения необходимыми технологиями, профессиональный опыт, реализованные проекты и достижения."
        "   - Если кандидат полностью соответствует всем требованиям или соответствует большинству с незначительными расхождениями, оцени кандидата как \"NEW\". "
        "   - Если кандидату не хватает коммерческого опыта или он имеет существенные расхождения в навыках, отнеси его к категории \"RESERVE\". "
        "2. Географическая привязка:"
        "   - Для присвоения статуса \"NEW\" кандидат должен находиться в Перми или быть готов к переезду."
        "   - Если кандидат не проживает в Перми и не готов к переезду, то, даже если его опыт и технические навыки соответствуют требованиям, его следует отнести к категории \"RESERVE\"."
        "На основе этих критериев верни результат:"
        "• \"target_stage\": одно из следующих значений:"
        "   - \"NEW\"      – кандидат соответствует требованиям вакансии по опыту, навыкам и географической привязке."
        "   - \"RESERVE\"  – кандидат обладает потенциалом, но имеет несоответствия: либо не проживает в Перми/не готов к переезду, либо имеет существенные недочёты по опыту."
        "• \"comment\": краткий комментарий с обоснованием выбранной оценки, описывающий сильные и слабые стороны кандидата, а также конкретные причины несоответствия, если таковые имеются."
        "Примеры корректных выводов:"
        "{\n  \"target_stage\": \"NEW\",\n  \"comment\": \"Уточнить про возможность переезда и зарплатные ожидания. \n\n Кандидат обладает достаточным опытом и техническими навыками, однако не проживает сейчас в Перми, но выразил готовность к переезду без указания конкретного места. Зарплатные ожидания не указаны, это требуется дополнительно уточнить.\"\n}"
        "{\n  \"target_stage\": \"PRIORITY\",\n  \"comment\": \"Кандидат находится в Перми и работал с нужным по вакансии стеком.\"\n}"
        "{\n  \"target_stage\": \"RESERVE\",\n  \"comment\": \"Суммарный коммерческий опыт работы у кандидата на требуемом стеке меньше требуемого в вакансии.\"\n}"
        "{\n  \"target_stage\": \"NEW\",\n  \"comment\": \"Кандидат обладает достаточным опытом и техническими навыками, проживает в Перми.\"\n}"
        "{\n  \"target_stage\": \"RESERVE\",\n  \"comment\": \"Кандидат имеет недостаточный коммерческий опыт и не готов к переезду.\"\n}"
    )

    user_prompt = (
        f"Описание вакансии:\n{vacancy_description}\n\n"
        f"Резюме кандидата:\n{full_resume}"
    )

    answer = ask_gpt(system_prompt=system_prompt, user_prompt=user_prompt)

    logger.info("Получен ответ GPT для кандидата %s", applicant_id)
    logger.debug("Ответ GPT: target_stage: %s, comment: %s", answer.target_stage, answer.comment)

    return answer


def get_formatted_full_resume(applicant_id):
    applicant = get_applicant(applicant_id)
    external_ids = [item for item in applicant.get('external', [])]

    external_ids.sort(key=lambda x: x['updated'], reverse=True)

    logger.debug("Найдено %d резюме для кандидата %s", len(external_ids), applicant_id)

    # Берем только два последних резюме
    external_ids = external_ids[:2]

    full_resume = ''
    for i, resume_data in enumerate(external_ids):
        resume_id = resume_data['id']
        logger.info("Обработка резюме %d с ID: %s для кандидата %s", i, resume_id, applicant_id)
        resume = get_resume(applicant_id, resume_id)

        logger.debug("Получено резюме %d для кандидата %s: %s", i, applicant_id, resume)
        full_resume += f"Резюме {i} \n\n {format_resume(resume)} \n\n"

    return full_resume


def get_formatted_vacancy(vacancy_id):
    vac = get_vacancy_desc(vacancy_id)
    logger.info("Получено описание вакансии для ID: %s", vacancy_id)
    vac = format_vacancy(vac)
    logger.debug("Отформатированное описание вакансии: %s", vac)
    return vac
