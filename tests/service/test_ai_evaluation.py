class DummyAnswer:
    def __init__(self):
        self.target_stage = "TEST_STAGE"
        self.comment = "Test comment"


def dummy_format_resume(resume):
    return "Formatted Resume"


def dummy_format_vacancy(vacancy):
    return "Formatted Vacancy"


def test_evaluate_candidate(monkeypatch):
    candidate = {
        "id": 1,
        "external": [{"id": 101}, {"id": 102}]
    }
    vacancy = {
        "position": "Test Position",
        "body": "Test vacancy body"
    }
    resume_dummy = {
        "resume": {
            "position": "Candidate Position",
            "wanted_salary": {"amount": "100000", "currency": "RUB"},
            "area": {"country": "TestCountry", "city": "TestCity", "address": "TestAddress"},
            "relocation": {},
            "skill_set": ["Python"],
            "experience": [],
            "education": {}
        }
    }
    monkeypatch.setattr("src.service.ai_evaluation.get_applicant", lambda c_id: candidate)
    monkeypatch.setattr("src.service.ai_evaluation.get_resume", lambda c_id, resume_id: resume_dummy)
    monkeypatch.setattr("src.service.ai_evaluation.get_vacancy_desc", lambda vacancy_id: vacancy)
    monkeypatch.setattr("src.service.ai_evaluation.format_resume", dummy_format_resume)
    monkeypatch.setattr("src.service.ai_evaluation.format_vacancy", dummy_format_vacancy)
    monkeypatch.setattr("src.service.ai_evaluation.ask_gpt", lambda vacancy_desc, full_resume: DummyAnswer())

    from src.service.ai_evaluation import evaluate_candidate
    answer = evaluate_candidate(1, 1)
    assert answer.target_stage == "TEST_STAGE"
    assert answer.comment == "Test comment"


def test_get_formatted_vacancy(monkeypatch):
    vacancy = {
        "position": "Test Position",
        "body": "Test body",
        "money": "100",
        "requirements": "",
        "conditions": ""
    }
    monkeypatch.setattr("src.service.ai_evaluation.get_vacancy_desc", lambda vid: vacancy)
    monkeypatch.setattr("src.service.ai_evaluation.format_vacancy", lambda vac: "Formatted Vacancy")

    from src.service.ai_evaluation import get_formatted_vacancy
    formatted = get_formatted_vacancy(1)
    assert formatted == "Formatted Vacancy"


def test_get_formatted_full_resume(monkeypatch):
    candidate = {
        "external": [{"id": 101}, {"id": 102}]
    }
    resume_dummy = {
        "resume": {
            "position": "Test",
            "wanted_salary": {"amount": "100", "currency": "USD"},
            "area": {"country": "TestCountry", "city": "TestCity", "address": ""},
            "relocation": {},
            "skill_set": [],
            "experience": [],
            "education": {}
        }
    }
    monkeypatch.setattr("src.service.ai_evaluation.get_applicant", lambda cid: candidate)
    monkeypatch.setattr("src.service.ai_evaluation.get_resume", lambda cid, rid: resume_dummy)
    monkeypatch.setattr("src.service.ai_evaluation.format_resume", lambda res: "Formatted Resume")

    from src.service.ai_evaluation import get_formatted_full_resume
    full_resume = get_formatted_full_resume(1)
    # Ожидается, что "Formatted Resume" появится дважды, так как у кандидата 2 резюме.
    assert full_resume.count("Formatted Resume") == 2
