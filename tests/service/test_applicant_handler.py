import json
import os

import pytest
from fastapi.responses import JSONResponse

from src.model.candidate_evaluation_answer import CandidateEvaluationAnswer
from src.model.target_stage import TargetStage
from src.service import applicant_handler


# Фиктивные реализации зависимостей для успешного сценария
def dummy_evaluate_candidate(candidate_id, vacancy_id):
    return CandidateEvaluationAnswer(target_stage=TargetStage.NEW, comment="Test comment")


def dummy_get_status_id_by_name(status_name):
    return 1


def dummy_update_candidate_status(candidate_id, target_status_id, vacancy_id, comment):
    return {"dummy": True}


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    monkeypatch.setenv("HUNTFLOW_FROM_STAGE", "Отклики")
    applicant_handler.from_stage_name = os.getenv("HUNTFLOW_FROM_STAGE") or "Отклики"


@pytest.mark.asyncio
async def test_handle_applicant_invalid_action_type():
    data = {
        "event": {
            "applicant_log": {
                "type": "ADD",
            }
        }
    }
    response: JSONResponse = await applicant_handler.handle_applicant(data)
    assert response.status_code == 400
    result = json.loads(response.body)
    assert "Обработка только для 'STATUS'" in result["error"]


@pytest.mark.asyncio
async def test_handle_applicant_status_mismatch():
    data = {
        "event": {
            "applicant_log": {
                "type": "STATUS",
                "status": {"name": "Новый"},
            }
        }
    }
    response: JSONResponse = await applicant_handler.handle_applicant(data)
    assert response.status_code == 400
    result = json.loads(response.body)
    assert "не соответствует" in result["error"]


@pytest.mark.asyncio
async def test_handle_applicant_missing_candidate_id():
    data = {
        "event": {
            "applicant_log": {
                "type": "STATUS",
                "status": {"name": "Отклики"},
                "vacancy": {"id": 123}
            },
            "applicant": {}
        }
    }
    response: JSONResponse = await applicant_handler.handle_applicant(data)
    assert response.status_code == 400
    result = json.loads(response.body)
    assert "ID кандидата не найден" in result["error"]


@pytest.mark.asyncio
async def test_handle_applicant_missing_vacancy_id():
    data = {
        "event": {
            "applicant_log": {
                "type": "STATUS",
                "status": {"name": "Отклики"},
                "vacancy": {}  # отсутствует ID вакансии
            },
            "applicant": {"id": 456}
        }
    }
    response: JSONResponse = await applicant_handler.handle_applicant(data)
    assert response.status_code == 400
    result = json.loads(response.body)
    assert "ID вакансии не найден" in result["error"]


@pytest.mark.asyncio
async def test_handle_applicant_success(monkeypatch):
    # Подменяем зависимости
    monkeypatch.setattr(applicant_handler, "evaluate_candidate", dummy_evaluate_candidate)
    monkeypatch.setattr(applicant_handler, "get_status_id_by_name", dummy_get_status_id_by_name)
    monkeypatch.setattr(applicant_handler, "update_applicant_status", dummy_update_candidate_status)

    data = {
        "event": {
            "applicant_log": {
                "type": "STATUS",
                "status": {"name": "Отклики"},
                "vacancy": {"id": 123}
            },
            "applicant": {"id": 456}
        }
    }
    response: JSONResponse = await applicant_handler.handle_applicant(data)
    assert response.status_code == 200
    result = json.loads(response.body)
    assert result.get("success") == "Данные обработаны"


@pytest.mark.asyncio
async def test_handle_applicant_missing_event():
    data = {}  # отсутствует 'event'
    response: JSONResponse = await applicant_handler.handle_applicant(data)
    assert response.status_code == 400
    result = json.loads(response.body)
    assert "Обработка только для 'STATUS'" in result["error"]
