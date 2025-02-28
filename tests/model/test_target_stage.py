import pytest

from src.model.target_stage import TargetStage


def test_target_stage_enum_values():
    assert TargetStage.NEW.value == "новые"
    assert TargetStage.PRIORITY.value == "приоритет"
    assert TargetStage.RESERVE.value == "резерв"
    assert TargetStage.REJECTION.value == "отказ"


def test_target_stage_str_conversion():
    new_stage = TargetStage("новые")
    assert new_stage == TargetStage.NEW

    priority_stage = TargetStage("приоритет")
    assert priority_stage == TargetStage.PRIORITY


def test_invalid_target_stage_value():
    with pytest.raises(ValueError):
        TargetStage("неизвестный")
