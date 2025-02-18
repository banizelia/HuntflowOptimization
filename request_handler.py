import hashlib
import hmac
import os

from dotenv import load_dotenv
from flask import jsonify

from handler import handle_applicant

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError("Ошибка: SECRET_KEY не найден в переменных окружения!")

def handle_request(request):
    # signature_header = request.headers.get('X-Huntflow-Signature')
    # if not signature_header:
    #     return jsonify({"error": "Отсутствует заголовок X-Huntflow-Signature"}), 401
    #
    # computed_signature = hmac.new(
    #     key=SECRET_KEY.encode('utf-8'),
    #     msg=request.data,
    #     digestmod=hashlib.sha256
    # ).hexdigest()
    #
    # if not hmac.compare_digest(computed_signature, signature_header):
    #     return jsonify({"error": "Неверная подпись"}), 401


    event_type = request.headers.get('x-huntflow-event')

    if event_type == 'APPLICANT':
        data = request.get_json()
        handle_applicant(data)

    return '', 200