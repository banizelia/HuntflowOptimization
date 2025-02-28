from src.model.candidate_evaluation_answer import CandidateEvaluationAnswer
from src.model.target_stage import TargetStage
from src.service import ai_evaluation

# Функция-замена для get_applicant, возвращает фиктивного кандидата с двумя резюме
def dummy_get_applicant(applicant_id: int):
    return {
        "external": [
            {"id": "resume1", "updated": 2},
            {"id": "resume2", "updated": 1},
        ]
    }

# Функция-замена для get_resume, возвращает фиктивное содержание резюме
def dummy_get_resume(applicant_id: int, resume_id: str):
    return {"dummy": f"resume content for {resume_id}"}



def dummy_format_resume(resume: dict) -> str:
    return f"Formatted {resume.get('dummy')}"


# Функция-замена для форматирования резюме, добавляющая фразу "не готов к переезду"
def dummy_format_resume_with_not_ready(resume: dict) -> str:
    # Добавляем фразу, чтобы сработала проверка на "не готов к переезду"
    return f"Formatted {resume.get('dummy')} with не готов к переезду"

# Функция-замена для get_vacancy_desc, возвращает фиктивное описание вакансии
def dummy_get_vacancy_desc(vacancy_id: int):
    return {"dummy": f"vacancy content for {vacancy_id}"}

# Функция-замена для форматирования вакансии
def dummy_format_vacancy(vacancy: dict) -> str:
    return f"Formatted {vacancy.get('dummy')}"

# Функция-замена для ask_gpt, возвращает фиктивный ответ от GPT
def dummy_ask_gpt(system_prompt: str, user_prompt: str) -> CandidateEvaluationAnswer:
    return CandidateEvaluationAnswer(
        target_stage=TargetStage.NEW,
        comment="Test evaluation comment"
    )


# Функция-замена для ask_gpt, которая не должна вызываться при наличии "не готов к переезду"
def dummy_ask_gpt_should_not_be_called(system_prompt: str, user_prompt: str) -> CandidateEvaluationAnswer:
    raise Exception("ask_gpt не должен вызываться, когда кандидат не готов к переезду")


# Тест для основного сценария (ветка с вызовом GPT)
def test_evaluate_candidate(monkeypatch):
    monkeypatch.setattr(ai_evaluation, "get_applicant", dummy_get_applicant)
    monkeypatch.setattr(ai_evaluation, "get_resume", dummy_get_resume)
    monkeypatch.setattr(ai_evaluation, "get_vacancy_desc", dummy_get_vacancy_desc)
    monkeypatch.setattr(ai_evaluation, "ask_gpt", dummy_ask_gpt)
    monkeypatch.setattr(ai_evaluation, "format_resume", dummy_format_resume)
    monkeypatch.setattr(ai_evaluation, "format_vacancy", dummy_format_vacancy)

    applicant_id = 123
    vacancy_id = 456

    # Вызываем тестируемую функцию
    result = ai_evaluation.evaluate_candidate(applicant_id, vacancy_id)

    # Проверяем, что результат соответствует фиктивному ответу от ask_gpt
    assert result.target_stage == TargetStage.NEW
    assert result.comment == "Test evaluation comment"

    # Проверяем корректное формирование полного резюме
    expected_resume = (
        "Резюме 0 \n\n Formatted resume content for resume1 \n\n"
        "Резюме 1 \n\n Formatted resume content for resume2 \n\n"
    )
    full_resume = ai_evaluation.get_formatted_full_resume(applicant_id)
    assert expected_resume.strip() == full_resume.strip()

    # Проверяем форматирование описания вакансии
    expected_vacancy = "Formatted vacancy content for 456"
    vacancy_description = ai_evaluation.get_formatted_vacancy(vacancy_id)
    assert expected_vacancy == vacancy_description


# Тест для сценария, когда резюме содержит фразу "не готов к переезду"
def test_evaluate_candidate_not_ready(monkeypatch):
    monkeypatch.setattr(ai_evaluation, "get_applicant", dummy_get_applicant)
    monkeypatch.setattr(ai_evaluation, "get_resume", dummy_get_resume)
    monkeypatch.setattr(ai_evaluation, "get_vacancy_desc", dummy_get_vacancy_desc)
    # ask_gpt не должен вызываться, поэтому подменяем на функцию, которая бросает исключение
    monkeypatch.setattr(ai_evaluation, "ask_gpt", dummy_ask_gpt_should_not_be_called)
    # Используем форматирование, добавляющее "не готов к переезду"
    monkeypatch.setattr(ai_evaluation, "format_resume", dummy_format_resume_with_not_ready)
    monkeypatch.setattr(ai_evaluation, "format_vacancy", dummy_format_vacancy)

    applicant_id = 789
    vacancy_id = 101112

    result = ai_evaluation.evaluate_candidate(applicant_id, vacancy_id)

    # Проверяем, что при наличии фразы "не готов к переезду" возвращается ответ без вызова ask_gpt
    assert result.target_stage == TargetStage.RESERVE
    assert result.comment == "Не готов к переезду в Пермь"
