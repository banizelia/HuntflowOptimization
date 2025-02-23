from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / "config" / ".env"
load_dotenv(dotenv_path=env_path)

from flasgger import Swagger
from flask import Flask, request
from src.service.request_handler import handle_request

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/huntflow/webhook/applicant', methods=['POST'])
def new_action():
    """
    Обработка POST запроса с авторизацией по секретному ключу.
    ---
    tags:
      - API
    consumes:
      - application/json
    parameters:
      - in: header
        name: X-Huntflow-Delivery
        type: string
        required: false
        description: Уникальный идентификатор вебхука.
      - in: header
        name: X-Huntflow-Event
        type: string
        required: false
        description: Тип события.
      - in: header
        name: X-Huntflow-Signature
        type: string
        required: false
        description: SHA256 HMAC подпись тела вебхука, сгенерированная с помощью секретного ключа.
      - in: body
        name: body
        required: false
        description: JSON объект с данными для обработки.
        schema:
          type: object
          example:
            key: value
    responses:
      200:
        description: POST запрос успешно обработан.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "POST запрос успешно обработан"
            data:
              type: object
      400:
        description: Отсутствуют данные или неверный формат.
      401:
        description: Ошибка авторизации.
    """

    return handle_request(request)

if __name__ == '__main__':
    app.run()