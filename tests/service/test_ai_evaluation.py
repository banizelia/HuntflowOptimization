from src.service.ai_evaluation import evaluate_candidate, get_formatted_vacancy
from src.model.candidate_evaluation_answer import CandidateEvaluationAnswer
from src.model.target_stage import TargetStage


# Фиктивные реализации для зависимостей

# 1. Сценарий: кандидат без резюме (external пустой)
def dummy_get_applicant_no_resume(applicant_id: int):
    return {"external": []}


# 2. Сценарий: кандидат имеет резюме, но не готов к переезду
def dummy_get_applicant_with_resume(applicant_id: int):
    return {"external": [{"id": "resume1", "updated": 100}]}


def dummy_get_resume_not_ready(applicant_id: int, resume_id: str):
    # Резюме с информацией, что кандидат "не готов к переезду"
    return {
        "resume": {
            "area": {"city": {"name": "Москва"}},
            "relocation": {"type": {"name": "Не готов к переезду"}},
            "position": "Developer",
            "wanted_salary": {"amount": "100000", "currency": "RUB"},
            "skill_set": ["Python"],
            "experience": [],
            "education": {}
        }
    }


# 3. Сценарий: кандидат готов к переезду, поэтому оценка передается GPT
def dummy_get_resume_ready(applicant_id: int, resume_id: str):
    return {
        "resume": {
            "area": {"city": {"name": "Пермь"}},  # Город, в котором переезд разрешен
            "relocation": {"type": {"name": "Готов к переезду"}},
            "position": "Developer",
            "wanted_salary": {"amount": "100000", "currency": "RUB"},
            "skill_set": ["Python"],
            "experience": [],
            "education": {}
        }
    }


# Для форматирования вакансии – достаточно вернуть любой словарь, который корректно обработается функцией format_vacancy
def dummy_get_vacancy_desc(vacancy_id: int):
    return {
        "position": "Developer",
        "money": "100000 RUB",
        "body": "<p>Описание вакансии</p>",
        "requirements": "<p>Требования</p>",
        "conditions": "<p>Условия</p>"
    }


# Фиктивная реализация ask_gpt, возвращающая заранее заданный результат
def dummy_ask_gpt(system_prompt: str, user_prompt: str):
    return CandidateEvaluationAnswer(target_stage=TargetStage.NEW, comment="Хороший кандидат")


# Фиктивные функции, которые не должны вызываться в определённых сценариях
def dummy_get_vacancy_desc_exception(vacancy_id: int):
    raise Exception("get_vacancy_desc не должен вызываться")


def dummy_ask_gpt_exception(system_prompt: str, user_prompt: str):
    raise Exception("ask_gpt не должен вызываться")


# Тест: Кандидат без резюме
def test_evaluate_candidate_no_resume(monkeypatch):
    monkeypatch.setattr("src.service.ai_evaluation.get_applicant", dummy_get_applicant_no_resume)
    result = evaluate_candidate(1, 1)
    assert result.comment == "Нет резюме"
    assert result.target_stage == TargetStage.RESERVE


# Тест: Кандидат не готов к переезду (релокация с фразой "не готов к переезду", город не содержит "пермь")
def test_evaluate_candidate_not_ready(monkeypatch):
    monkeypatch.setattr("src.service.ai_evaluation.get_applicant", dummy_get_applicant_with_resume)
    monkeypatch.setattr("src.service.ai_evaluation.get_resume", dummy_get_resume_not_ready)
    # В этом сценарии функции, связанные с вакансией и GPT, не должны вызываться
    monkeypatch.setattr("src.service.ai_evaluation.get_vacancy_desc", dummy_get_vacancy_desc_exception)
    monkeypatch.setattr("src.service.ai_evaluation.ask_gpt", dummy_ask_gpt_exception)

    result = evaluate_candidate(1, 1)
    assert result.comment == "Не готов к переезду в Пермь"
    assert result.target_stage == TargetStage.RESERVE


# Тест: Кандидат соответствует требованиям – вызывается GPT
def test_evaluate_candidate_success(monkeypatch):
    monkeypatch.setattr("src.service.ai_evaluation.get_applicant", dummy_get_applicant_with_resume)
    monkeypatch.setattr("src.service.ai_evaluation.get_resume", dummy_get_resume_ready)
    monkeypatch.setattr("src.service.ai_evaluation.get_vacancy_desc", dummy_get_vacancy_desc)
    monkeypatch.setattr("src.service.ai_evaluation.ask_gpt", dummy_ask_gpt)

    result = evaluate_candidate(1, 2)
    assert result.comment == "Хороший кандидат"
    assert result.target_stage == TargetStage.NEW


# Тест для функции get_formatted_vacancy
def test_get_formatted_vacancy(monkeypatch):
    monkeypatch.setattr("src.service.ai_evaluation.get_vacancy_desc", dummy_get_vacancy_desc)
    formatted = get_formatted_vacancy(123)
    # Проверяем, что отформатированное описание вакансии содержит основные элементы
    assert "Вакансия:" in formatted
    assert "Ограничения по зп:" in formatted
