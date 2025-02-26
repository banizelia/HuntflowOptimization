import logging
import os

from flask import jsonify

from src.api_clients.huntflow_api import get_status_id_by_name, update_candidate_status
from src.service.ai_evaluation import evaluate_candidate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from_stage_name = os.getenv("HUNTFLOW_FROM_STAGE")

def handle_applicant(data):
    meta = data.get('meta', {})
    if meta.get('webhook_action') != "STATUS":
        logger.info("webhook_action = %s. Обработка только для 'STATUS'.", meta.get('webhook_action'))
        return

    event = data.get('event', {})
    applicant_log = event.get('applicant_log', {})
    status_name = applicant_log.get('status', {}).get('name')

    if from_stage_name.lower() != status_name.lower():
        logger.info("Статус кандидата: %s, не соответствует '%s'.", status_name, from_stage_name)
        return jsonify({"error": f"Статус кандидата: {status_name}, не соответствует '{from_stage_name}'."}), 400

    applicant = event.get('applicant', {})
    candidate_id = applicant.get('id')
    vacancy_id = applicant_log.get('vacancy', {}).get('id')

    if not candidate_id:
        logger.error("ID кандидата не найден.")
        return jsonify({"error": f"ID кандидата не найден."}), 400
    if not vacancy_id:
        logger.error("ID вакансии не найден.")
        return jsonify({"error": f"ID вакансии не найден."}), 400

    logger.info("Кандидат перешёл на этап '%s'. ID кандидата: %s, ID вакансии: %s",from_stage_name, candidate_id, vacancy_id)
    candidate_evaluation_answer = evaluate_candidate(candidate_id, vacancy_id)

    target_stage_name = candidate_evaluation_answer.target_stage.value
    comment = candidate_evaluation_answer.comment

    target_stage_id = get_status_id_by_name(target_stage_name)

    update_candidate_status(candidate_id, target_stage_id, vacancy_id, f"Оценка от ИИ: \n\n {comment}")

    return jsonify({"success": "Данные обработаны"}), 200