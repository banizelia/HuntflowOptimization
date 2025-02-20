from pydantic import BaseModel
from model.TargetStage import TargetStage

class CandidateEvaluationAnswer(BaseModel):
    target_stage: TargetStage
    comment: str