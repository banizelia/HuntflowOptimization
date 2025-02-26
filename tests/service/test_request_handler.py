import hashlib
import hmac
import os

import pytest
from flask import Flask, jsonify

from src.service.request_handler import handle_request


# Класс-обёртка для имитации объекта запроса
class DummyRequest:
    def __init__(self, headers, data, json_data):
        self.headers = headers
        self.data = data  # байтовая строка
        self._json = json_data

    def get_json(self):
        return self._json


# Фикстура для создания контекста Flask-приложения
@pytest.fixture
def flask_app_context():
    app = Flask(__name__)
    with app.app_context():
        yield


# Вспомогательная функция для вычисления HMAC подписи
def compute_signature(secret_key: str, data: bytes) -> str:
    return hmac.new(
        key=secret_key.encode('utf-8'),
        msg=data,
        digestmod=hashlib.sha256
    ).hexdigest()


def test_handle_request_no_request(flask_app_context):
    """Если request равен None, возвращается ошибка 400 с сообщением 'Отсутствуют данные'."""
    response, status_code = handle_request(None)
    assert status_code == 400
    json_data = response.get_json()
    assert json_data.get("error") == "Отсутствуют данные"


def test_handle_request_no_json(flask_app_context):
    """Если request.get_json() возвращает None, возвращается ошибка 400 с сообщением 'Отсутствуют данные'."""
    dummy_req = DummyRequest(
        headers={"X-Huntflow-Signature": "dummy"},
        data=b"{}",
        json_data=None
    )
    response, status_code = handle_request(dummy_req)
    assert status_code == 400
    json_data = response.get_json()
    assert json_data.get("error") == "Отсутствуют данные"


def test_handle_request_missing_signature_header(flask_app_context):
    """Если отсутствует заголовок X-Huntflow-Signature, возвращается ошибка 401."""
    dummy_req = DummyRequest(
        headers={},  # отсутствует подпись
        data=b"some data",
        json_data={"key": "value"}
    )
    response, status_code = handle_request(dummy_req)
    assert status_code == 401
    json_data = response.get_json()
    assert "Отсутствует заголовок X-Huntflow-Signature" in json_data.get("error", "")


def test_handle_request_invalid_signature(flask_app_context, monkeypatch):
    """Если вычисленная подпись не совпадает с заголовком, возвращается ошибка 401 с сообщением 'Неверная подпись'."""
    # Задаём секретный ключ
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    # Данные запроса
    data = b"important payload"
    # Вычисляем корректную подпись и затем изменим её, чтобы симулировать ошибку
    correct_signature = compute_signature(secret_key, data)
    invalid_signature = correct_signature[:-1] + ("0" if correct_signature[-1] != "0" else "1")
    dummy_req = DummyRequest(
        headers={
            "X-Huntflow-Signature": invalid_signature,
            "x-huntflow-event": "PING"
        },
        data=data,
        json_data={"key": "value"}
    )
    response, status_code = handle_request(dummy_req)
    assert status_code == 401
    json_data = response.get_json()
    assert "Неверная подпись" in json_data.get("error", "")


def test_handle_request_ping_event(flask_app_context, monkeypatch):
    """При event_type 'PING' возвращается строка 'Ping received' и статус 200."""
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    data = b"ping data"
    signature = compute_signature(secret_key, data)
    dummy_req = DummyRequest(
        headers={
            "X-Huntflow-Signature": signature,
            "x-huntflow-event": "PING"
        },
        data=data,
        json_data={"key": "value"}
    )
    response, status_code = handle_request(dummy_req)
    # При PING возвращается строка, а не объект jsonify
    assert status_code == 200
    assert response == "Ping received"


def test_handle_request_applicant_event(flask_app_context, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    data = b"applicant data"
    signature = compute_signature(secret_key, data)

    dummy_json = {"dummy": "data"}

    def dummy_handle_applicant(json_data):
        return jsonify({"success": "Handled applicant"}), 200

    monkeypatch.setattr("src.service.request_handler.handle_applicant", dummy_handle_applicant)

    dummy_req = DummyRequest(
        headers={
            "X-Huntflow-Signature": signature,
            "x-huntflow-event": "APPLICANT"
        },
        data=data,
        json_data=dummy_json
    )
    response, status_code = handle_request(dummy_req)
    assert status_code == 200
    json_data = response.get_json()
    assert json_data.get("success") == "Handled applicant"


def test_handle_request_unknown_event(flask_app_context, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    data = b"unknown event data"
    signature = compute_signature(secret_key, data)

    dummy_req = DummyRequest(
        headers={
            "X-Huntflow-Signature": signature,
            "x-huntflow-event": "UNKNOWN"
        },
        data=data,
        json_data={"key": "value"}
    )
    response, status_code = handle_request(dummy_req)
    assert status_code == 400
    json_data = response.get_json()
    assert "Неизвестное событие" in json_data.get("error", "")


def test_handle_request_missing_secret_key(flask_app_context, monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    data = b"some data"
    dummy_req = DummyRequest(
        headers={
            "X-Huntflow-Signature": "dummy_signature",
            "x-huntflow-event": "PING"
        },
        data=data,
        json_data={"key": "value"}
    )
    with pytest.raises(ValueError) as exc_info:
        handle_request(dummy_req)
    assert "SECRET_KEY не найден" in str(exc_info.value)
