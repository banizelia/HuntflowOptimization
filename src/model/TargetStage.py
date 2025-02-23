from enum import Enum


class TargetStage(str, Enum):
    NEW = "новые"
    PRIORITY = "приоритет"
    RESERVE = "резерв"
    REJECTION = "отказ"
