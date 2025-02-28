import os

import pytest
from flask import Flask

from src.model.target_stage import TargetStage
from src.model.candidate_evaluation_answer import CandidateEvaluationAnswer
from src.service import applicant_handler


# Фиктивные реализации зависимостей для успешного сценария
def dummy_evaluate_candidate(candidate_id, vacancy_id):

    return CandidateEvaluationAnswer(target_stage=TargetStage.NEW, comment="Test comment")


def dummy_get_status_id_by_name(status_name):
    return 1


def dummy_update_candidate_status(candidate_id, target_status_id, vacancy_id, comment):
    return {"dummy": True}


@pytest.fixture
def flask_app_context():
    app = Flask(__name__)
    with app.app_context():
        yield


def set_from_stage(monkeypatch, value="Отклики"):
    monkeypatch.setenv("HUNTFLOW_FROM_STAGE", value)
    # Обновляем значение, сохранённое в модуле, чтобы не было None
    applicant_handler.from_stage_name = os.getenv("HUNTFLOW_FROM_STAGE") or value


def test_handle_applicant_invalid_action_type(monkeypatch, flask_app_context):
    set_from_stage(monkeypatch)
    data = {
        "event": {
            "applicant_log": {
                "type": "ADD",
            }
        }
    }
    response, status_code = applicant_handler.handle_applicant(data)
    assert status_code == 400
    json_data = response.get_json()
    assert "Обработка только для 'STATUS'" in json_data["error"]


def test_handle_applicant_status_mismatch(monkeypatch, flask_app_context):
    set_from_stage(monkeypatch)
    data = {
        "event": {
            "applicant_log": {
                "type": "STATUS",
                "status": {"name": "Новый"},
            }
        }
    }
    response, status_code = applicant_handler.handle_applicant(data)
    assert status_code == 400
    json_data = response.get_json()
    assert "не соответствует" in json_data["error"]


def test_handle_applicant_missing_candidate_id(monkeypatch, flask_app_context):
    set_from_stage(monkeypatch)
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
    response, status_code = applicant_handler.handle_applicant(data)
    assert status_code == 400
    json_data = response.get_json()
    assert "ID кандидата не найден" in json_data["error"]


def test_handle_applicant_missing_vacancy_id(monkeypatch, flask_app_context):
    set_from_stage(monkeypatch)
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
    response, status_code = applicant_handler.handle_applicant(data)
    assert status_code == 400
    json_data = response.get_json()
    assert "ID вакансии не найден" in json_data["error"]


def test_handle_applicant_success(monkeypatch, flask_app_context):
    set_from_stage(monkeypatch)
    # Подменяем зависимости: evaluate_candidate, get_status_id_by_name, update_candidate_status
    monkeypatch.setattr(applicant_handler, "evaluate_candidate", dummy_evaluate_candidate)
    monkeypatch.setattr(applicant_handler, "get_status_id_by_name", dummy_get_status_id_by_name)
    monkeypatch.setattr(applicant_handler, "update_candidate_status", dummy_update_candidate_status)

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
    response, status_code = applicant_handler.handle_applicant(data)
    assert status_code == 200
    json_data = response.get_json()
    assert json_data.get("success") == "Данные обработаны"


def test_handle_applicant_missing_event(monkeypatch, flask_app_context):
    set_from_stage(monkeypatch)
    data = {}  # отсутствует 'event'
    response, status_code = applicant_handler.handle_applicant(data)
    assert status_code == 400
    json_data = response.get_json()
    assert "Обработка только для 'STATUS'" in json_data["error"]
