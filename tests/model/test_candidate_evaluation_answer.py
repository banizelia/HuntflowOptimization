import pytest
from pydantic import ValidationError

from src.model.CandidateEvaluationAnswer import CandidateEvaluationAnswer
from src.model.TargetStage import TargetStage


def test_valid_candidate_evaluation_answer_with_enum():
    answer = CandidateEvaluationAnswer(
        target_stage=TargetStage.NEW,
        comment="Все критерии удовлетворены."
    )
    assert answer.target_stage == TargetStage.NEW
    assert answer.comment == "Все критерии удовлетворены."


def test_valid_candidate_evaluation_answer_with_string():
    answer = CandidateEvaluationAnswer(
        target_stage="приоритет",
        comment="Кандидат соответствует ключевым требованиям."
    )
    assert answer.target_stage == TargetStage.PRIORITY
    assert answer.comment == "Кандидат соответствует ключевым требованиям."


def test_invalid_target_stage():
    with pytest.raises(ValidationError):
        CandidateEvaluationAnswer(
            target_stage="неизвестный_статус",
            comment="Неверный статус."
        )


def test_missing_comment_field():
    with pytest.raises(ValidationError):
        CandidateEvaluationAnswer(
            target_stage="резерв"
        )
