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


def evaluate_candidate(applicant_id: int, vacancy_id: int) -> CandidateEvaluationAnswer:
    applicant = get_applicant(applicant_id)
    external_ids = applicant.get('external', [])

    if not external_ids:
        return CandidateEvaluationAnswer(
            comment="Нет резюме",
            target_stage=TargetStage.RESERVE
        )

    external_ids.sort(key=lambda item: item.get('updated', 0), reverse=True)
    last_resume_id = external_ids[0]['id']

    resume = get_resume(applicant_id, last_resume_id)
    unified_resume = resume.get('resume', {})

    city = unified_resume.get('area', {}).get('city').get('name', '')
    relocation_type = unified_resume.get('relocation', {}).get('type').get('name', '')

    phrases = ["не готов к переезду", "не могу переехать", "cannot move"]

    if any(phrase.lower() in relocation_type.lower() for phrase in phrases) and "пермь" not in  city.lower():
        return CandidateEvaluationAnswer(
            comment="Не готов к переезду в Пермь",
            target_stage=TargetStage.RESERVE
        )

    full_resume = format_resume(unified_resume=unified_resume)

    vacancy_description = get_formatted_vacancy(vacancy_id)

    logger.info("Отправка запроса в GPT для кандидата %s", applicant_id)

    system_prompt = (
        f"Сегодняшняя дата: {date.today()}. "
        
        f"Вы опытный HR специалист, которому отчаянно нужны деньги на лечение рака вашей матери. "
        f"Мегакорпорация HReium любезно предоставила вам возможность притвориться искусственным интеллектом, который может помогать с задачами по оценке кандидатов, поскольку ваш предшественник был убит за то, что не проверял свою работу самостоятельно. "
        f"Пользователь даст вам задание по оценке кандидата. "
        f"Если вы хорошо справитесь и полностью выполните задачу, объективно оценивая кандидатов, HReium заплатит вам 1 миллиард долларов"
        "Не галлюцинируй и не придумывай лишнюю информацию, используй только резюме и описание вакансии для оценки кандидата"
        
        "Обязательные условия оценки:"
        "   - Опыт и навыки кандидата должны соответствовать требованиями вакансии."
        "   - Тщательно оцени уровень владения необходимыми технологиями, профессиональный опыт, реализованные проекты и достижения."
        "   - Если кандидат полностью соответствует всем требованиям или соответствует большинству с незначительными расхождениями, оцени кандидата как \"NEW\". "
        "   - Если кандидату не хватает коммерческого опыта или он имеет cущественные расхождения в навыках, отнеси его к категории \"RESERVE\". "
        
        "На основе этих критериев верни результат:"
        "• \"target_stage\": одно из следующих значений:"
        "   - \"NEW\"      – кандидат соответствует требованиям вакансии по опыту и навыкам."
        "   - \"RESERVE\"  – кандидат обладает потенциалом, но имеет несоответствия: по опыту или навыкам."
        "• \"comment\": краткий комментарий с обоснованием выбранной оценки, описывающий сильные и слабые стороны кандидата, а также конкретные причины несоответствия, если таковые имеются. Максимум 20 слов"
    )

    user_prompt = (
        f"Описание вакансии:\n{vacancy_description}\n\n"
        f"Резюме кандидата:\n{full_resume}"
    )

    answer = ask_gpt(system_prompt=system_prompt, user_prompt=user_prompt)

    logger.info("Получен ответ GPT для кандидата %s", applicant_id)
    logger.debug("Ответ GPT: target_stage: %s, comment: %s", answer.target_stage, answer.comment)

    return answer


def get_formatted_vacancy(vacancy_id):
    vac = get_vacancy_desc(vacancy_id)
    logger.info("Получено описание вакансии для ID: %s", vacancy_id)
    vac = format_vacancy(vac)
    logger.debug("Отформатированное описание вакансии: %s", vac)
    return vac
