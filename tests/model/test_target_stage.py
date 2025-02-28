import pytest

from src.model.target_stage import TargetStage


def test_target_stage_enum_values():
    assert TargetStage.NEW.value == "новые"
    assert TargetStage.RESERVE.value == "резерв"


def test_target_stage_str_conversion():
    new_stage = TargetStage("новые")
    assert new_stage == TargetStage.NEW

    priority_stage = TargetStage("резерв")
    assert priority_stage == TargetStage.RESERVE


def test_invalid_target_stage_value():
    with pytest.raises(ValueError):
        TargetStage("неизвестный")
