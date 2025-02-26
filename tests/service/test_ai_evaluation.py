from src.model.CandidateEvaluationAnswer import CandidateEvaluationAnswer
from src.model.TargetStage import TargetStage
from src.service import ai_evaluation


# Функция-замена для get_applicant, возвращает фиктивного кандидата с двумя резюме
def dummy_get_applicant(c_id: int):
    return {
        "external": [
            {"id": "resume1", "updated": 2},
            {"id": "resume2", "updated": 1},
        ]
    }


# Функция-замена для get_resume, возвращает фиктивное содержание резюме
def dummy_get_resume(c_id: int, resume_id: str):
    return {"dummy": f"resume content for {resume_id}"}


# Функция-замена для форматирования резюме
def dummy_format_resume(resume: dict) -> str:
    # Формируем строку на основе переданного фиктивного резюме
    return f"Formatted {resume.get('dummy')}"


# Функция-замена для get_vacancy_desc, возвращает фиктивное описание вакансии
def dummy_get_vacancy_desc(vacancy_id: int):
    return {"dummy": f"vacancy content for {vacancy_id}"}


# Функция-замена для форматирования вакансии
def dummy_format_vacancy(vacancy: dict) -> str:
    return f"Formatted {vacancy.get('dummy')}"


# Функция-замена для ask_gpt, возвращает фиктивный ответ от GPT
def dummy_ask_gpt(vacancy_description: str, full_resume: str) -> CandidateEvaluationAnswer:
    return CandidateEvaluationAnswer(
        target_stage=TargetStage.NEW,
        comment="Test evaluation comment"
    )


def test_evaluate_candidate(monkeypatch):
    # Подменяем зависимости в модуле ai_evaluation
    monkeypatch.setattr(ai_evaluation, "get_applicant", dummy_get_applicant)
    monkeypatch.setattr(ai_evaluation, "get_resume", dummy_get_resume)
    monkeypatch.setattr(ai_evaluation, "get_vacancy_desc", dummy_get_vacancy_desc)
    monkeypatch.setattr(ai_evaluation, "ask_gpt", dummy_ask_gpt)
    monkeypatch.setattr(ai_evaluation, "format_resume", dummy_format_resume)
    monkeypatch.setattr(ai_evaluation, "format_vacancy", dummy_format_vacancy)

    candidate_id = 123
    vacancy_id = 456

    # Вызываем тестируемую функцию
    result = ai_evaluation.evaluate_candidate(candidate_id, vacancy_id)

    # Проверяем, что результат соответствует фиктивному ответу от ask_gpt
    assert result.target_stage == TargetStage.NEW
    assert result.comment == "Test evaluation comment"

    # Дополнительно можно проверить корректность формирования полного резюме
    expected_resume = (
        "Резюме 0 \n\n Formatted resume content for resume1 \n\n"
        "Резюме 1 \n\n Formatted resume content for resume2 \n\n"
    )
    full_resume = ai_evaluation.get_formatted_full_resume(candidate_id)
    assert expected_resume.strip() == full_resume.strip()

    # Проверяем форматирование описания вакансии
    expected_vacancy = "Formatted vacancy content for 456"
    vacancy_description = ai_evaluation.get_formatted_vacancy(vacancy_id)
    assert expected_vacancy == vacancy_description
