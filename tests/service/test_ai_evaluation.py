class DummyAnswer:
    def __init__(self):
        self.target_stage = "TEST_STAGE"
        self.comment = "Test comment"


def dummy_format_resume(resume):
    return "Formatted Resume"


def dummy_format_vacancy(vacancy):
    return "Formatted Vacancy"

@pytest.fixture(autouse=True)
def mock_openai(monkeypatch):
    monkeypatch.setenv("CHATGPT_API_TOKEN", "test_chatgpt_token")
    mock_openai = MagicMock()

    mock_answer = DummyAnswer()
    mock_openai.return_value.ask_gpt.return_value = mock_answer
    monkeypatch.setattr("src.api_clients.openai_api.client", mock_openai)


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
        "id": 1,
        "external": [{"id": 101, "updated": "2023-01-01"}, {"id": 102, "updated": "2023-01-02"}]
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
