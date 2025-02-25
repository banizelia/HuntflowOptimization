FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 7707

CMD ["python", "src/app.py"]