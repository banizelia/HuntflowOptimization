from src.api_clients import openai_api
from src.model.CandidateEvaluationAnswer import CandidateEvaluationAnswer
from src.model.TargetStage import TargetStage

class DummyMessage:
    def __init__(self, parsed):
        self.parsed = parsed

class DummyChoice:
    def __init__(self, parsed):
        self.message = DummyMessage(parsed)

class DummyCompletion:
    def __init__(self, choices):
        self.choices = choices

def dummy_parse(*args, **kwargs):
    dummy_answer = CandidateEvaluationAnswer(
        target_stage=TargetStage.NEW,
        comment="Test comment"
    )
    return DummyCompletion([DummyChoice(dummy_answer)])


def test_ask_gpt(monkeypatch):
    monkeypatch.setattr(openai_api.client.beta.chat.completions, "parse", dummy_parse)

    vacancy_description = "Test vacancy description"
    candidate_resume = "Test candidate resume"

    answer = openai_api.ask_gpt(vacancy_description, candidate_resume)

    assert isinstance(answer, CandidateEvaluationAnswer)
    assert answer.target_stage == TargetStage.NEW
    assert answer.comment == "Test comment"
