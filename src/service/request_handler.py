import hashlib
import hmac
import os
from flask import jsonify
from src.service.applicant_handler import handle_applicant

def handle_request(request):
    if request is None or request.get_json() is None:
        return jsonify({"error": "Отсутствуют данные"}), 400

    signature_header = request.headers.get('X-Huntflow-Signature')
    if not signature_header:
        return jsonify({"error": "Отсутствует заголовок X-Huntflow-Signature"}), 401

    secret_key = os.getenv('SECRET_KEY')

    if not secret_key:
        raise ValueError("Ошибка: SECRET_KEY не найден в переменных окружения!")

    computed_signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=request.data,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, signature_header):
        return jsonify({"error": "Неверная подпись"}), 401

    event_type = request.headers.get('x-huntflow-event')

    data = request.get_json()

    if event_type == 'PING':
        return 'Ping received', 200
    elif event_type == 'APPLICANT':
        handle_applicant(data)
        return jsonify({"success": "Данные обработаны"}), 200
    else:
        return jsonify({"error": "Неизвестное событие"}), 400