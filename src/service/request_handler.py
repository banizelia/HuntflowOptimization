import hashlib
import hmac
import os
from fastapi import Request
from fastapi.responses import JSONResponse
from src.service.applicant_handler import handle_applicant

async def handle_request(request: Request):
    signature_header = request.headers.get('X-Huntflow-Signature')
    if not signature_header:
        return JSONResponse(content={"error": "Отсутствует заголовок X-Huntflow-Signature"}, status_code=401)

    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise ValueError("Ошибка: SECRET_KEY не найден в переменных окружения!")

    body_bytes = await request.body()
    computed_signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=body_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, signature_header):
        return JSONResponse(content={"error": "Неверная подпись"}, status_code=401)

    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Отсутствуют данные или неверный формат"}, status_code=400)

    event_type = request.headers.get('x-huntflow-event')
    if event_type == 'PING':
        return JSONResponse(content="Ping received", status_code=200)
    elif event_type == 'APPLICANT':
        return await handle_applicant(data)
    else:
        return JSONResponse(content={"error": "Неизвестное событие"}, status_code=400)
