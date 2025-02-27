import hashlib
import hmac
import json
import os

import pytest
from flask import jsonify

from src.app import app


def compute_signature(secret_key: str, data: bytes) -> str:
    return hmac.new(secret_key.encode('utf-8'), data, digestmod=hashlib.sha256).hexdigest()


@pytest.fixture
def flask_app_context():
    with app.app_context():
        yield


def test_new_action_no_json(monkeypatch, flask_app_context):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    payload = ''
    data_bytes = payload.encode('utf-8')
    correct_signature = compute_signature(secret_key, data_bytes)

    with app.test_client() as client:
        headers = {
            "X-Huntflow-Signature": correct_signature,
            "x-huntflow-event": "PING"
        }
        response = client.post(
            "/huntflow/webhook/applicant",
            data=None,
            content_type="application/json",
            headers=headers
        )

        assert response.status_code == 400


def test_new_action_missing_signature(monkeypatch, flask_app_context):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    payload = json.dumps({"key": "value"})
    with app.test_client() as client:
        response = client.post(
            "/huntflow/webhook/applicant",
            data=payload,
            content_type="application/json"
        )
        assert response.status_code == 401
        data = response.get_json()
        assert "Отсутствует заголовок X-Huntflow-Signature" in data["error"]


def test_new_action_invalid_signature(monkeypatch, flask_app_context):
    """
    Если переданная подпись неверна, эндпоинт должен вернуть 401 с сообщением "Неверная подпись".
    """
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    payload = json.dumps({"key": "value"})
    data_bytes = payload.encode('utf-8')
    correct_signature = compute_signature(secret_key, data_bytes)

    invalid_signature = correct_signature[:-1] + ("0" if correct_signature[-1] != "0" else "1")
    with app.test_client() as client:
        headers = {
            "X-Huntflow-Signature": invalid_signature,
            "x-huntflow-event": "PING"
        }
        response = client.post(
            "/huntflow/webhook/applicant",
            data=payload,
            content_type="application/json",
            headers=headers
        )
        assert response.status_code == 401
        data = response.get_json()
        assert "Неверная подпись" in data["error"]


def test_new_action_ping_event(monkeypatch, flask_app_context):
    """
    Если заголовок x-huntflow-event равен "PING", эндпоинт должен вернуть строку "Ping received" со статусом 200.
    """
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    payload = json.dumps({"key": "value"})
    data_bytes = payload.encode('utf-8')
    signature = compute_signature(secret_key, data_bytes)
    with app.test_client() as client:
        headers = {
            "X-Huntflow-Signature": signature,
            "x-huntflow-event": "PING"
        }
        response = client.post(
            "/huntflow/webhook/applicant",
            data=payload,
            content_type="application/json",
            headers=headers
        )
        assert response.status_code == 200
        # Для PING возвращается простая строка, а не JSON
        assert response.data.decode("utf-8") == "Ping received"


def test_new_action_applicant_event(monkeypatch, flask_app_context):
    """
    Если заголовок x-huntflow-event равен "APPLICANT", вызывается функция handle_request,
    которая внутри вызывает handle_applicant. Здесь мы подменяем handle_applicant, чтобы вернуть
    фиктивный ответ, и проверяем, что эндпоинт возвращает его.
    """
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    payload = json.dumps({"key": "value"})
    data_bytes = payload.encode('utf-8')
    signature = compute_signature(secret_key, data_bytes)

    # Фиктивная реализация handle_applicant, возвращающая JSON-ответ
    def dummy_handle_applicant(request_json):
        return jsonify({"message": "Processed applicant"}), 200

    # Подменяем handle_applicant в модуле request_handler, который импортирован в app
    import src.service.request_handler as req_handler
    monkeypatch.setattr(req_handler, "handle_applicant", dummy_handle_applicant)

    with app.test_client() as client:
        headers = {
            "X-Huntflow-Signature": signature,
            "x-huntflow-event": "APPLICANT"
        }
        response = client.post(
            "/huntflow/webhook/applicant",
            data=payload,
            content_type="application/json",
            headers=headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data.get("message") == "Processed applicant"


def test_new_action_unknown_event(monkeypatch, flask_app_context):
    """
    Если значение заголовка x-huntflow-event неизвестно (не PING и не APPLICANT),
    эндпоинт должен вернуть ошибку 400 с сообщением "Неизвестное событие".
    """
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    payload = json.dumps({"key": "value"})
    data_bytes = payload.encode('utf-8')
    signature = compute_signature(secret_key, data_bytes)
    with app.test_client() as client:
        headers = {
            "X-Huntflow-Signature": signature,
            "x-huntflow-event": "UNKNOWN"
        }
        response = client.post(
            "/huntflow/webhook/applicant",
            data=payload,
            content_type="application/json",
            headers=headers
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "Неизвестное событие" in data["error"]
