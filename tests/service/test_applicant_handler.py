import os

import pytest
from flask import Flask

from src.service import applicant_handler


# Фиктивные реализации зависимостей для успешного сценария
def dummy_evaluate_candidate(candidate_id, vacancy_id):
    from src.model.CandidateEvaluationAnswer import CandidateEvaluationAnswer
    from src.model.TargetStage import TargetStage
    return CandidateEvaluationAnswer(target_stage=TargetStage.NEW, comment="Test comment")


def dummy_get_status_id_by_name(status_name):
    return 1


def dummy_update_candidate_status(candidate_id, target_status_id, vacancy_id, comment):
    return {"dummy": True}


# Фикстура для создания контекста приложения Flask
@pytest.fixture
def flask_app_context():
    app = Flask(__name__)
    with app.app_context():
        yield


# Вспомогательная функция для установки переменной окружения и обновления модуля
def set_from_stage(monkeypatch, value="Отклики"):
    monkeypatch.setenv("HUNTFLOW_FROM_STAGE", value)
    # Обновляем значение, сохранённое в модуле, чтобы не было None
    applicant_handler.from_stage_name = os.getenv("HUNTFLOW_FROM_STAGE") or value


def test_handle_applicant_invalid_action_type(monkeypatch, flask_app_context):
    """
    Если поле action_type не равно "STATUS", функция должна вернуть ошибку 400.
    """
    set_from_stage(monkeypatch)
    data = {
        "event": {
            "applicant_log": {
                "applicant_log": "ADD",  # неверный тип действия
            }
        }
    }
    response, status_code = applicant_handler.handle_applicant(data)
    assert status_code == 400
    json_data = response.get_json()
    assert "Обработка только для 'STATUS'" in json_data["error"]


def test_handle_applicant_status_mismatch(monkeypatch, flask_app_context):
    """
    Если статус кандидата не соответствует значению HUNTFLOW_FROM_STAGE, функция возвращает ошибку 400.
    """
    set_from_stage(monkeypatch)
    data = {
        "event": {
            "applicant_log": {
                "applicant_log": "STATUS",
                "status": {"name": "Новый"},  # не совпадает с "Отклики"
            }
        }
    }
    response, status_code = applicant_handler.handle_applicant(data)
    assert status_code == 400
    json_data = response.get_json()
    assert "не соответствует" in json_data["error"]


def test_handle_applicant_missing_candidate_id(monkeypatch, flask_app_context):
    """
    Если в данных отсутствует ID кандидата, функция должна вернуть ошибку 400.
    """
    set_from_stage(monkeypatch)
    data = {
        "event": {
            "applicant_log": {
                "applicant_log": "STATUS",
                "status": {"name": "Отклики"},
                "vacancy": {"id": 123}
            },
            "applicant": {}  # отсутствует ID кандидата
        }
    }
    response, status_code = applicant_handler.handle_applicant(data)
    assert status_code == 400
    json_data = response.get_json()
    assert "ID кандидата не найден" in json_data["error"]


def test_handle_applicant_missing_vacancy_id(monkeypatch, flask_app_context):
    """
    Если в данных отсутствует ID вакансии, функция должна вернуть ошибку 400.
    """
    set_from_stage(monkeypatch)
    data = {
        "event": {
            "applicant_log": {
                "applicant_log": "STATUS",
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
    """
    При корректных входных данных функция должна вызвать оценку кандидата и вернуть успешный ответ.
    """
    set_from_stage(monkeypatch)
    # Подменяем зависимости: evaluate_candidate, get_status_id_by_name, update_candidate_status
    monkeypatch.setattr(applicant_handler, "evaluate_candidate", dummy_evaluate_candidate)
    monkeypatch.setattr(applicant_handler, "get_status_id_by_name", dummy_get_status_id_by_name)
    monkeypatch.setattr(applicant_handler, "update_candidate_status", dummy_update_candidate_status)

    data = {
        "event": {
            "applicant_log": {
                "applicant_log": "STATUS",
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
    """
    Если в переданных данных отсутствует ключ 'event', функция должна корректно обработать ситуацию.
    В данном случае action_type будет {} и не равен "STATUS".
    """
    set_from_stage(monkeypatch)
    data = {}  # отсутствует 'event'
    response, status_code = applicant_handler.handle_applicant(data)
    assert status_code == 400
    json_data = response.get_json()
    assert "Обработка только для 'STATUS'" in json_data["error"]
