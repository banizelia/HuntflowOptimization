import pytest
from pydantic import ValidationError

from src.model.candidate_evaluation_answer import CandidateEvaluationAnswer
from src.model.target_stage import TargetStage


def test_valid_candidate_evaluation_answer_with_enum():
    answer = CandidateEvaluationAnswer(
        target_stage=TargetStage.NEW,
        comment="Все критерии удовлетворены."
    )
    assert answer.target_stage == TargetStage.NEW
    assert answer.comment == "Все критерии удовлетворены."

def test_missing_comment_field():
    with pytest.raises(ValidationError):
        CandidateEvaluationAnswer(
            target_stage="резерв"
        )
