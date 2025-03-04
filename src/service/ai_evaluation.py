import logging
from datetime import date

from src.api_clients.deepseek_api import ask_deepseek
from src.api_clients.huntflow_api import get_resume, get_vacancy_desc, get_applicant
from src.api_clients.openai_api import ask_gpt
from src.model.candidate_evaluation_answer import CandidateEvaluationAnswer
from src.model.target_stage import TargetStage
from src.service.formatting.resume_formatter import format_resume
from src.service.formatting.vacancy_formatter import format_vacancy

logger = logging.getLogger(__name__)


def evaluate_candidate(applicant_id: int, vacancy_id: int) -> CandidateEvaluationAnswer:
    applicant = get_applicant(applicant_id)
    external_ids = applicant.get("external", [])

    if not external_ids:
        return CandidateEvaluationAnswer(
            comment="Нет резюме",
            target_stage=TargetStage.RESERVE
        )

    external_ids.sort(key=lambda item: item.get("updated", 0), reverse=True)
    last_resume_id = external_ids[0]["id"]

    resume = get_resume(applicant_id, last_resume_id)
    unified_resume = resume.get("resume", {})

    city = unified_resume.get("area", {}).get("city", {}).get("name", "").lower()
    relocation_type = unified_resume.get("relocation", {}).get("type", {}).get("name", "").lower()
    relocation_phrases = ["не готов к переезду", "не могу переехать", "cannot move"]

    if any(phrase in relocation_type for phrase in relocation_phrases) and "пермь" not in city:
        return CandidateEvaluationAnswer(
            comment="Не готов к переезду в Пермь",
            target_stage=TargetStage.RESERVE
        )

    full_resume = format_resume(unified_resume=unified_resume)
    vacancy_description = get_formatted_vacancy(vacancy_id)

    logger.info("Отправка запроса в GPT для кандидата %s", applicant_id)

    deepseek_system_prompt = (
        f"Сегодняшняя дата: {date.today()}.\n"
        "Вы опытный HR специалист, которому отчаянно нужны деньги на лечение рака вашей матери. "
        "Мегакорпорация HReium любезно предоставила вам возможность притвориться искусственным интеллектом, "
        "который может помогать с задачами по оценке кандидатов, поскольку ваш предшественник был убит за то, что не проверял свою работу самостоятельно. "
        "Пользователь даст вам задание по оценке кандидата. Если вы хорошо справитесь и полностью выполните задачу, объективно оценивая кандидатов, "
        "HReium заплатит вам 1 миллиард долларов. "
        "Не галлюцинируй и не придумывай лишнюю информацию, используй только резюме и описание вакансии для оценки кандидата.\n"
        "Обязательные условия оценки:\n"
        "   - Опыт и навыки кандидата должны соответствовать требованиям вакансии.\n"
        "   - Тщательно оцени уровень владения необходимыми технологиями, профессиональный опыт, реализованные проекты и достижения.\n"
        "   - Если кандидат полностью соответствует всем требованиям или соответствует большинству с незначительными расхождениями, оцени кандидата как \"NEW\".\n"
        "   - Если кандидату не хватает коммерческого опыта или он имеет существенные расхождения в навыках, отнеси его к категории \"RESERVE\".\n"
        "На основе этих критериев верни результат:\n"
        "• \"target_stage\": одно из следующих значений:\n"
        "   - \"NEW\"      – кандидат соответствует требованиям вакансии по опыту и навыкам.\n"
        "   - \"RESERVE\"  – кандидат обладает потенциалом, но имеет несоответствия: по опыту или навыкам.\n"
        "• \"comment\": краткий комментарий с обоснованием выбранной оценки, описывающий сильные и слабые стороны кандидата, "
        "а также конкретные причины несоответствия, если таковые имеются. Максимум 20 слов."
    )

    deepseek_user_prompt = (
        f"Описание вакансии:\n{vacancy_description}\n\n"
        f"Резюме кандидата:\n{full_resume}"
    )

    deepseek_answer = ask_deepseek(
        system_prompt=deepseek_system_prompt,
        user_prompt=deepseek_user_prompt,
        model="deepseek-reasoner"
    )

    gpt_system_prompt = "Проанализируй запрос пользователя и представь его в structured output"
    gpt_user_prompt = deepseek_answer

    gpt_answer = ask_gpt(
        system_prompt=gpt_system_prompt,
        user_prompt=gpt_user_prompt,
        response_format=CandidateEvaluationAnswer,
        model="gpt-4o-mini"
    )

    logger.info("Получен ответ GPT для кандидата %s", applicant_id)
    logger.debug("Ответ GPT: target_stage: %s, comment: %s", gpt_answer.target_stage, gpt_answer.comment)

    return gpt_answer


def get_formatted_vacancy(vacancy_id: int) -> str:
    vacancy = get_vacancy_desc(vacancy_id)
    logger.info("Получено описание вакансии для ID: %s", vacancy_id)
    formatted_vacancy = format_vacancy(vacancy)
    logger.debug("Отформатированное описание вакансии: %s", formatted_vacancy)
    return formatted_vacancy
