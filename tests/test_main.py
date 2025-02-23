import json
import os
import hmac
import hashlib

def test_no_data(client):
    response = client.post('/huntflow/webhook/applicant', data='null', content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert "Отсутствуют данные" in data.get("error", "")

def test_missing_signature(client):
    payload = {"key": "value"}
    response = client.post(
        '/huntflow/webhook/applicant',
        json=payload
    )
    assert response.status_code == 401
    data = response.get_json()
    assert "Отсутствует заголовок X-Huntflow-Signature" in data.get("error", "")

def test_invalid_signature(client):
    payload = {"key": "value"}
    json_data = json.dumps(payload).encode('utf-8')
    headers = {
        "X-Huntflow-Signature": "invalid_signature",
        "x-huntflow-event": "APPLICANT"
    }
    response = client.post(
        '/huntflow/webhook/applicant',
        data=json_data,
        headers=headers,
        content_type='application/json'
    )
    assert response.status_code == 401
    data = response.get_json()
    assert "Неверная подпись" in data.get("error", "")

def test_valid_request(client):
    payload = {
        "meta": {"webhook_action": "STATUS"},
        "key": "value"
    }

    json_str = json.dumps(payload, separators=(',', ':'))
    json_data = json_str.encode('utf-8')
    secret = os.getenv("SECRET_KEY")

    valid_signature = hmac.new(
        secret.encode('utf-8'),
        json_data,
        digestmod=hashlib.sha256
    ).hexdigest()
    headers = {
        "X-Huntflow-Signature": valid_signature,
        "x-huntflow-event": "APPLICANT"
    }
    response = client.post(
        '/huntflow/webhook/applicant',
        data=json_data,
        headers=headers,
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") == "Данные обработаны"