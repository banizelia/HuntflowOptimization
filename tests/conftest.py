import pytest

from src.app import app as flask_app


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("HUNTFLOW_BASE_URL", "http://localhost:8000")
    monkeypatch.setenv("HUNTFLOW_API_TOKEN", "test_api_token")
    monkeypatch.setenv("HUNTFLOW_REFRESH_TOKEN", "test_refresh_token")
    monkeypatch.setenv("HUNTFLOW_ACCOUNT_ID", "12345")
    monkeypatch.setenv("CHATGPT_API_TOKEN", "test_chatgpt_token")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_test_token")
    monkeypatch.setenv("HUNTFLOW_FROM_STAGE", "Отклики")
    yield


@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "DEBUG": True,
    })
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()
