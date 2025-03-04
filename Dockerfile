FROM python:3.12-slim

WORKDIR /app

COPY . /app

ENV PYTHONPATH=/app

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 7707

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "7707"]