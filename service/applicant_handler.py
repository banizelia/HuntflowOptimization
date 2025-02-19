from service.ai_evaluation import evaluate_candidate
from api_clients.huntflow_api import get_status_id_by_name, update_candidate_status

def handle_applicant(data):
    meta = data.get('meta', {})
    if meta.get('webhook_action') != "STATUS":
        print(f"webhook_action = {meta.get('webhook_action')}. Обработка только для 'STATUS'.")
        return

    event = data.get('event', {})
    applicant_log = event.get('applicant_log', {})
    status_name = applicant_log.get('status', {}).get('name')
    if status_name != "Отклики":
        print(f"Статус кандидата: {status_name}, не соответствует 'Отклики'.")
        return

    applicant = event.get('applicant', {})
    candidate_id = applicant.get('id')
    vacancy_id = applicant_log.get('vacancy', {}).get('id')

    if not candidate_id:
        print("ID кандидата не найден.")
        return
    if not vacancy_id:
        print("ID вакансии не найден.")
        return

    print(f"Кандидат перешёл на этап 'Отклики'. ID кандидата: {candidate_id}, ID вакансии: {vacancy_id}")
    candidate_evaluation_answer = evaluate_candidate(candidate_id, vacancy_id)

    target_stage_name = candidate_evaluation_answer.target_stage.value
    comment = candidate_evaluation_answer.comment

    target_stage_id = get_status_id_by_name(target_stage_name)

    update_candidate_status(candidate_id, target_stage_id, vacancy_id, f"Оценка от ИИ: \n\n {comment}")