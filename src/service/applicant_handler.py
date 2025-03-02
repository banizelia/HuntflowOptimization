import os
import logging
from fastapi.responses import JSONResponse
from src.api_clients.huntflow_api import get_status_id_by_name, update_candidate_status
from src.service.ai_evaluation import evaluate_candidate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from_stage_name = os.getenv("HUNTFLOW_FROM_STAGE")

async def handle_applicant(data: dict):
    event = data.get('event', {})
    applicant_log = event.get('applicant_log', {})

    action_type = applicant_log.get('type', {})
    if action_type != "STATUS":
        logger.info("action_type = %s. Обработка только для 'STATUS'.", action_type)
        return JSONResponse(content={"error": f"action_type = {action_type}. Обработка только для 'STATUS'."}, status_code=400)

    status_name = applicant_log.get('status', {}).get('name')
    if from_stage_name.lower() != status_name.lower():
        logger.info("Статус кандидата: %s, не соответствует '%s'.", status_name, from_stage_name)
        return JSONResponse(content={"error": f"Статус кандидата: {status_name}, не соответствует '{from_stage_name}'."}, status_code=400)

    applicant_id = event.get('applicant', {}).get('id')
    if not applicant_id:
        logger.error("ID кандидата не найден.")
        return JSONResponse(content={"error": "ID кандидата не найден."}, status_code=400)

    vacancy_id = applicant_log.get('vacancy', {}).get('id')
    if not vacancy_id:
        logger.error("ID вакансии не найден.")
        return JSONResponse(content={"error": "ID вакансии не найден."}, status_code=400)

    logger.info("Кандидат перешёл на этап '%s'. ID кандидата: %s, ID вакансии: %s", from_stage_name, applicant_id, vacancy_id)
    candidate_evaluation_answer = evaluate_candidate(applicant_id, vacancy_id)

    target_stage_name = candidate_evaluation_answer.target_stage.value
    comment = candidate_evaluation_answer.comment

    target_stage_id = get_status_id_by_name(target_stage_name)
    update_candidate_status(applicant_id, target_stage_id, vacancy_id, f"Оценка от ИИ: \n\n {comment}")

    return JSONResponse(content={"success": "Данные обработаны"}, status_code=200)
