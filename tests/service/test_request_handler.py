import os
os.environ.setdefault("CHATGPT_API_TOKEN", "dummy_api_key")
os.environ.setdefault("OPENAI_API_KEY", "dummy_api_key")
os.environ.setdefault("SECRET_KEY", "dummy_secret_key")

import json
import hmac
import hashlib
import pytest
from flask import Flask
from src.service.request_handler import handle_request

@pytest.fixture(autouse=True)
def app_context():
    app = Flask(__name__)
    with app.app_context():
        yield

class DummyRequest:
    def __init__(self, data, headers):
        self.data = data
        self.headers = headers

    def get_json(self):
        try:
            return json.loads(self.data.decode('utf-8'))
        except Exception:
            return None

def test_handle_request_no_data():
    response, status = handle_request(None)
    resp_json = response.get_json()
    assert status == 400
    assert resp_json.get("error") == "Отсутствуют данные"

def test_handle_request_missing_signature():
    payload = {"key": "value"}
    data_bytes = json.dumps(payload).encode('utf-8')
    headers = {
        "x-huntflow-event": "APPLICANT"  # Заголовок X-Huntflow-Signature отсутствует
    }
    dummy_req = DummyRequest(data_bytes, headers)
    response, status = handle_request(dummy_req)
    resp_json = response.get_json()
    assert status == 401
    assert resp_json.get("error") == "Отсутствует заголовок X-Huntflow-Signature"

def test_handle_request_invalid_signature():
    payload = {"key": "value"}
    data_bytes = json.dumps(payload).encode('utf-8')
    headers = {
        "X-Huntflow-Signature": "invalid_signature",
        "x-huntflow-event": "APPLICANT"
    }
    dummy_req = DummyRequest(data_bytes, headers)
    response, status = handle_request(dummy_req)
    resp_json = response.get_json()
    assert status == 401
    assert resp_json.get("error") == "Неверная подпись"

def test_handle_request_valid(monkeypatch):
    test_secret = "testsecret"
    monkeypatch.setenv("SECRET_KEY", test_secret)

    payload = {"key": "value"}
    data_bytes = json.dumps(payload).encode('utf-8')
    valid_signature = hmac.new(test_secret.encode('utf-8'), data_bytes, hashlib.sha256).hexdigest()
    headers = {
        "X-Huntflow-Signature": valid_signature,
        "x-huntflow-event": "APPLICANT"
    }
    dummy_req = DummyRequest(data_bytes, headers)

    called_data = []
    def dummy_handle_applicant(data):
        called_data.append(data)
    monkeypatch.setattr("src.service.request_handler.handle_applicant", dummy_handle_applicant)

    response, status = handle_request(dummy_req)
    resp_json = response.get_json()

    assert called_data[0] == payload
    assert resp_json.get("success") == "Данные обработаны"
    assert status == 200

def test_handle_request_non_applicant_event(monkeypatch):
    test_secret = "testsecret"
    monkeypatch.setenv("SECRET_KEY", test_secret)

    payload = {"key": "value"}
    data_bytes = json.dumps(payload).encode('utf-8')
    valid_signature = hmac.new(test_secret.encode('utf-8'), data_bytes, hashlib.sha256).hexdigest()
    headers = {
        "X-Huntflow-Signature": valid_signature,
        "x-huntflow-event": "OTHER"
    }
    dummy_req = DummyRequest(data_bytes, headers)

    called = False
    def dummy_handle_applicant(data):
        nonlocal called
        called = True
    monkeypatch.setattr("src.service.request_handler.handle_applicant", dummy_handle_applicant)

    response, status = handle_request(dummy_req)
    resp_json = response.get_json()

    assert not called
    assert resp_json.get("success") == "Данные обработаны"
    assert status == 200
