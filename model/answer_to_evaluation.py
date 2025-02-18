from enum import Enum

from pydantic import BaseModel


class TargetStage(str, Enum):
    NEW = "новые"
    PRIORITY = "приоритет"
    RESERVE = "резерв"
    REJECTION = "отказ"


class CandidateEvaluationAnswer(BaseModel):
    target_stage: TargetStage
    comment: str