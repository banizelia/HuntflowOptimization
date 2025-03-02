import os
import json
import hmac
import hashlib
from fastapi.responses import JSONResponse

import pytest
from src.service.request_handler import handle_request

class DummyRequest:
    def __init__(self, headers, data, json_data):
        self._headers = headers
        self._data = data
        self._json_data = json_data

    @property
    def headers(self):
        return self._headers

    async def body(self):
        return self._data

    async def json(self):
        if self._json_data is None:
            raise Exception("No JSON")
        return self._json_data

def compute_signature(secret_key: str, data: bytes) -> str:
    return hmac.new(secret_key.encode('utf-8'), data, digestmod=hashlib.sha256).hexdigest()

@pytest.mark.asyncio
async def test_handle_request_no_json(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    data = b'{}'
    signature = compute_signature(secret_key, data)
    dummy_req = DummyRequest(
        headers={
            "X-Huntflow-Signature": signature,
            "x-huntflow-event": "PING"
        },
        data=data,
        json_data=None
    )
    response: JSONResponse = await handle_request(dummy_req)
    assert response.status_code == 400
    result = json.loads(response.body)
    assert result.get("error") == "Отсутствуют данные или неверный формат"

@pytest.mark.asyncio
async def test_handle_request_missing_signature():
    dummy_req = DummyRequest(
        headers={},  # отсутствует подпись
        data=b"some data",
        json_data={"key": "value"}
    )
    response: JSONResponse = await handle_request(dummy_req)
    assert response.status_code == 401
    result = json.loads(response.body)
    assert "Отсутствует заголовок X-Huntflow-Signature" in result.get("error", "")

@pytest.mark.asyncio
async def test_handle_request_invalid_signature(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    data = b"important payload"
    correct_signature = compute_signature(secret_key, data)
    # Изменяем последнюю цифру для имитации неверной подписи
    invalid_signature = correct_signature[:-1] + ("0" if correct_signature[-1] != "0" else "1")
    dummy_req = DummyRequest(
        headers={
            "X-Huntflow-Signature": invalid_signature,
            "x-huntflow-event": "PING"
        },
        data=data,
        json_data={"key": "value"}
    )
    response: JSONResponse = await handle_request(dummy_req)
    assert response.status_code == 401
    result = json.loads(response.body)
    assert "Неверная подпись" in result.get("error", "")

@pytest.mark.asyncio
async def test_handle_request_ping_event(monkeypatch):
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
    response = await handle_request(dummy_req)
    # При PING возвращается строка "Ping received"
    # Так как мы возвращаем JSONResponse с контентом-строкой, можно проверить так:
    assert response.status_code == 200
    result = json.loads(response.body)
    assert result == "Ping received"

@pytest.mark.asyncio
async def test_handle_request_applicant_event(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    data = b"applicant data"
    signature = compute_signature(secret_key, data)
    dummy_json = {"dummy": "data"}

    # Фиктивная реализация handle_applicant, возвращающая JSONResponse
    async def dummy_handle_applicant(json_data):
        return JSONResponse(content={"success": "Handled applicant"}, status_code=200)

    monkeypatch.setattr("src.service.request_handler.handle_applicant", dummy_handle_applicant)

    dummy_req = DummyRequest(
        headers={
            "X-Huntflow-Signature": signature,
            "x-huntflow-event": "APPLICANT"
        },
        data=data,
        json_data=dummy_json
    )
    response: JSONResponse = await handle_request(dummy_req)
    assert response.status_code == 200
    result = json.loads(response.body)
    assert result.get("success") == "Handled applicant"

@pytest.mark.asyncio
async def test_handle_request_unknown_event(monkeypatch):
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
    response: JSONResponse = await handle_request(dummy_req)
    assert response.status_code == 400
    result = json.loads(response.body)
    assert "Неизвестное событие" in result.get("error", "")

@pytest.mark.asyncio
async def test_handle_request_missing_secret_key(monkeypatch):
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
        await handle_request(dummy_req)
    assert "SECRET_KEY не найден" in str(exc_info.value)
