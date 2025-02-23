from pydantic import BaseModel

from src.model.TargetStage import TargetStage


class CandidateEvaluationAnswer(BaseModel):
    target_stage: TargetStage
    comment: str
