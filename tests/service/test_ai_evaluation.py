from datetime import date

from src.model.candidate_evaluation_answer import CandidateEvaluationAnswer
from src.model.target_stage import TargetStage
from src.service.ai_evaluation import (
    get_latest_resume,
    is_not_ready_to_relocate,
    build_deepseek_prompts,
    evaluate_candidate,
    get_formatted_vacancy,
)


# --- Тесты для get_latest_resume ---

def test_get_latest_resume_empty(monkeypatch):
    # Если у кандидата отсутствуют внешние резюме, функция должна вернуть пустой словарь.
    def dummy_get_applicant(applicant_id):
        return {"external": []}

    monkeypatch.setattr("src.service.ai_evaluation.get_applicant", dummy_get_applicant)

    # get_resume не вызывается, но подменим для безопасности.
    monkeypatch.setattr("src.service.ai_evaluation.get_resume", lambda a_id, ext_id: {})

    resume = get_latest_resume(123)
    assert resume == {}


def test_get_latest_resume_success(monkeypatch):
    # Подготавливаем данные кандидата с внешними резюме.
    applicant_data = {
        "external": [
            {"id": 1, "updated": 100},
            {"id": 2, "updated": 200},
            {"id": 3, "updated": 150},
        ]
    }
    expected_resume = {"key": "value"}

    def dummy_get_applicant(applicant_id):
        return applicant_data

    def dummy_get_resume(applicant_id, external_id):
        # Ожидаем, что выберется резюме с id=2 (наибольшее значение updated)
        assert external_id == 2
        return {"resume": expected_resume}

    monkeypatch.setattr("src.service.ai_evaluation.get_applicant", dummy_get_applicant)
    monkeypatch.setattr("src.service.ai_evaluation.get_resume", dummy_get_resume)

    resume = get_latest_resume(123)
    assert resume == expected_resume


# --- Тесты для is_not_ready_to_relocate ---

def test_is_not_ready_to_relocate_true():
    # Кандидат не готов к переезду и город не содержит "пермь"
    resume = {
        "area": {"city": {"name": "Москва"}},
        "relocation": {"type": {"name": "не готов к переезду"}},
    }
    assert is_not_ready_to_relocate(resume) is True


def test_is_not_ready_to_relocate_false_by_city():
    # Если город содержит "пермь", то даже если фраза есть – кандидат считается готовым.
    resume = {
        "area": {"city": {"name": "Пермь"}},
        "relocation": {"type": {"name": "не готов к переезду"}},
    }
    assert is_not_ready_to_relocate(resume) is False


def test_is_not_ready_to_relocate_false_no_phrase():
    # Если в relocation нет нужных фраз – кандидат готов.
    resume = {
        "area": {"city": {"name": "Москва"}},
        "relocation": {"type": {"name": "готов к переезду"}},
    }
    assert is_not_ready_to_relocate(resume) is False


# --- Тест для build_deepseek_prompts ---

def test_build_deepseek_prompts():
    vacancy_description = "Vacancy description"
    full_resume = "Candidate resume"
    system_prompt, user_prompt = build_deepseek_prompts(vacancy_description, full_resume)

    # Проверяем, что системный промпт содержит сегодняшнюю дату и основные условия.
    assert str(date.today()) in system_prompt
    assert "Оценка кандидата" not in system_prompt  # просто пример проверки
    # Проверяем, что пользовательский промпт содержит и вакансию, и резюме.
    assert vacancy_description in user_prompt
    assert full_resume in user_prompt


# --- Тест для get_formatted_vacancy ---

def test_get_formatted_vacancy(monkeypatch):
    dummy_vacancy = {"id": 10, "body": "Some HTML", "position": "Developer"}
    formatted = "Formatted vacancy description"

    # Подменяем get_vacancy_desc и format_vacancy.
    monkeypatch.setattr("src.service.ai_evaluation.get_vacancy_desc", lambda vid: dummy_vacancy)
    monkeypatch.setattr("src.service.ai_evaluation.format_vacancy", lambda vac: formatted)

    result = get_formatted_vacancy(10)
    assert result == formatted


# --- Тесты для evaluate_candidate ---

def test_evaluate_candidate_no_resume(monkeypatch):
    # Если get_latest_resume возвращает пустой словарь, то функция должна вернуть оценку с комментарием "Нет резюме"
    monkeypatch.setattr("src.service.ai_evaluation.get_latest_resume", lambda applicant_id: {})

    result = evaluate_candidate(123, 10)
    assert result.comment == "Нет резюме"
    assert result.target_stage == TargetStage.RESERVE


def test_evaluate_candidate_not_ready(monkeypatch):
    # Подменяем get_latest_resume для возврата резюме, которое вызовет is_not_ready_to_relocate.
    resume = {
        "area": {"city": {"name": "Москва"}},
        "relocation": {"type": {"name": "не готов к переезду"}},
    }
    monkeypatch.setattr("src.service.ai_evaluation.get_latest_resume", lambda applicant_id: resume)

    result = evaluate_candidate(123, 10)
    assert result.comment == "Не готов к переезду в Пермь"
    assert result.target_stage == TargetStage.RESERVE


def test_evaluate_candidate_success(monkeypatch):
    # Сценарий, когда кандидат имеет резюме и готов к переезду.
    resume = {
        "area": {"city": {"name": "Санкт-Петербург"}},
        "relocation": {"type": {"name": "готов к переезду"}},
    }
    # Подменяем get_latest_resume, форматирование и получение вакансии.
    monkeypatch.setattr("src.service.ai_evaluation.get_latest_resume", lambda applicant_id: resume)
    monkeypatch.setattr("src.service.ai_evaluation.format_resume", lambda unified_resume: "Formatted Resume")
    monkeypatch.setattr("src.service.ai_evaluation.get_formatted_vacancy", lambda vacancy_id: "Formatted Vacancy")

    # Подменяем ask_deepseek для возврата некого текста.
    monkeypatch.setattr("src.service.ai_evaluation.ask_deepseek",
                        lambda system_prompt, user_prompt, model: "Deepseek answer")

    # Подменяем ask_gpt для возврата корректного объекта CandidateEvaluationAnswer.
    dummy_answer = CandidateEvaluationAnswer(
        target_stage=TargetStage.NEW,
        comment="Approved"
    )
    monkeypatch.setattr("src.service.ai_evaluation.ask_gpt",
                        lambda system_prompt, user_prompt, response_format, model: dummy_answer)

    result = evaluate_candidate(123, 10)
    assert result.comment == "Approved"
    assert result.target_stage == TargetStage.NEW
