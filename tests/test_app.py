import os
import json
import hmac
import hashlib
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def compute_signature(secret_key: str, data: bytes) -> str:
    return hmac.new(secret_key.encode('utf-8'), data, digestmod=hashlib.sha256).hexdigest()

def test_new_action_no_json(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    payload = ''  # пустое тело
    data_bytes = payload.encode('utf-8')
    correct_signature = compute_signature(secret_key, data_bytes)
    headers = {
        "X-Huntflow-Signature": correct_signature,
        "x-huntflow-event": "PING",
        "Content-Type": "application/json"
    }
    response = client.post(
        "/huntflow/webhook/applicant",
        content=payload,
        headers=headers
    )
    assert response.status_code == 400
    result = response.json()
    assert "Отсутствуют данные" in result.get("error", "")

def test_new_action_missing_signature(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    payload = json.dumps({"key": "value"})
    headers = {
        "Content-Type": "application/json"
    }
    response = client.post(
        "/huntflow/webhook/applicant",
        content=payload,
        headers=headers
    )
    assert response.status_code == 401
    result = response.json()
    assert "Отсутствует заголовок X-Huntflow-Signature" in result.get("error", "")

def test_new_action_invalid_signature(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    payload = json.dumps({"key": "value"})
    data_bytes = payload.encode('utf-8')
    correct_signature = compute_signature(secret_key, data_bytes)
    invalid_signature = correct_signature[:-1] + ("0" if correct_signature[-1] != "0" else "1")
    headers = {
        "X-Huntflow-Signature": invalid_signature,
        "x-huntflow-event": "PING",
        "Content-Type": "application/json"
    }
    response = client.post(
        "/huntflow/webhook/applicant",
        content=payload,
        headers=headers
    )
    assert response.status_code == 401
    result = response.json()
    assert "Неверная подпись" in result.get("error", "")

def test_new_action_ping_event(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    payload = json.dumps({"key": "value"})
    data_bytes = payload.encode('utf-8')
    signature = compute_signature(secret_key, data_bytes)
    headers = {
        "X-Huntflow-Signature": signature,
        "x-huntflow-event": "PING",
        "Content-Type": "application/json"
    }
    response = client.post(
        "/huntflow/webhook/applicant",
        content=payload,
        headers=headers
    )
    assert response.status_code == 200
    result = response.json()
    assert result == "Ping received"

def test_new_action_applicant_event(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    payload = json.dumps({"key": "value"})
    data_bytes = payload.encode('utf-8')
    signature = compute_signature(secret_key, data_bytes)

    # Фиктивная реализация handle_applicant, возвращающая JSONResponse
    async def dummy_handle_applicant(data):
        from fastapi.responses import JSONResponse
        return JSONResponse(content={"message": "Processed applicant"}, status_code=200)

    monkeypatch.setattr("src.service.request_handler.handle_applicant", dummy_handle_applicant)

    headers = {
        "X-Huntflow-Signature": signature,
        "x-huntflow-event": "APPLICANT",
        "Content-Type": "application/json"
    }
    response = client.post(
        "/huntflow/webhook/applicant",
        content=payload,
        headers=headers
    )
    assert response.status_code == 200
    result = response.json()
    assert result.get("message") == "Processed applicant"

def test_new_action_unknown_event(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    secret_key = os.getenv("SECRET_KEY")
    payload = json.dumps({"key": "value"})
    data_bytes = payload.encode('utf-8')
    signature = compute_signature(secret_key, data_bytes)
    headers = {
        "X-Huntflow-Signature": signature,
        "x-huntflow-event": "UNKNOWN",
        "Content-Type": "application/json"
    }
    response = client.post(
        "/huntflow/webhook/applicant",
        content=payload,
        headers=headers
    )
    assert response.status_code == 400
    result = response.json()
    assert "Неизвестное событие" in result.get("error", "")
