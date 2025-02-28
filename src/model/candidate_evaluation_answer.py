from pydantic import BaseModel

from src.model.target_stage import TargetStage


class CandidateEvaluationAnswer(BaseModel):
    target_stage: TargetStage
    comment: str
