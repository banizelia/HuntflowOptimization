import pytest

from src.model.base_api_client import BaseAPIClient


# Фиктивная реализация метода parse, возвращающая переданные параметры для проверки.
class DummyCompletions:
    def parse(self, model, messages, response_format=None):
        return {
            "model": model,
            "messages": messages,
            "response_format": response_format,
        }


class DummyChat:
    def __init__(self):
        self.completions = DummyCompletions()


class DummyBeta:
    def __init__(self):
        self.chat = DummyChat()


# Фиктивный клиент OpenAI, который эмулирует нужную структуру (атрибут beta с методом parse).
class DummyOpenAI:
    def __init__(self, api_key, base_url=None):
        self.api_key = api_key
        self.base_url = base_url
        self.beta = DummyBeta()


# Проверяем, что при наличии переменной токена и отсутствии базового URL клиент создаётся корректно.
def test_get_client_without_base_url(monkeypatch):
    monkeypatch.setenv("DUMMY_TOKEN", "dummy_token")
    # Подменяем OpenAI в модуле src.model.base_api_client на нашу фиктивную реализацию.
    monkeypatch.setattr("src.model.base_api_client.OpenAI", DummyOpenAI)

    client_instance = BaseAPIClient(token_env="DUMMY_TOKEN", service_name="TestService")
    client = client_instance.get_client()

    assert client is not None
    assert client.api_key == "dummy_token"
    assert client.base_url is None


# Проверяем создание клиента при наличии и токена, и базового URL.
def test_get_client_with_base_url(monkeypatch):
    monkeypatch.setenv("DUMMY_TOKEN", "dummy_token")
    monkeypatch.setenv("DUMMY_BASE_URL", "http://example.com")
    monkeypatch.setattr("src.model.base_api_client.OpenAI", DummyOpenAI)

    client_instance = BaseAPIClient(
        token_env="DUMMY_TOKEN",
        service_name="TestService",
        base_url_env="DUMMY_BASE_URL"
    )
    client = client_instance.get_client()

    assert client is not None
    assert client.api_key == "dummy_token"
    assert client.base_url == "http://example.com"


# Проверяем работу метода ask без передачи response_format.
def test_ask_without_response_format(monkeypatch):
    monkeypatch.setenv("DUMMY_TOKEN", "dummy_token")
    monkeypatch.setattr("src.model.base_api_client.OpenAI", DummyOpenAI)

    client_instance = BaseAPIClient(token_env="DUMMY_TOKEN", service_name="TestService")

    system_prompt = "System prompt"
    user_prompt = "User prompt"
    model = "dummy-model"

    result = client_instance.ask(system_prompt, user_prompt, model)

    expected_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    assert result["model"] == model
    assert result["messages"] == expected_messages
    assert result["response_format"] is None


# Проверяем работу метода ask с передачей response_format.
def test_ask_with_response_format(monkeypatch):
    monkeypatch.setenv("DUMMY_TOKEN", "dummy_token")
    monkeypatch.setattr("src.model.base_api_client.OpenAI", DummyOpenAI)

    client_instance = BaseAPIClient(token_env="DUMMY_TOKEN", service_name="TestService")

    system_prompt = "System prompt"
    user_prompt = "User prompt"
    model = "dummy-model"
    response_format = "dummy-format"

    result = client_instance.ask(system_prompt, user_prompt, model, response_format=response_format)

    assert result["response_format"] == response_format


# Проверяем, что если переменная токена отсутствует, то get_client возвращает None,
# а вызов ask приводит к выбрасыванию исключения.
def test_ask_raises_error_when_token_missing(monkeypatch):
    monkeypatch.delenv("MISSING_TOKEN", raising=False)

    client_instance = BaseAPIClient(token_env="MISSING_TOKEN", service_name="TestService")
    client = client_instance.get_client()
    assert client is None

    with pytest.raises(ValueError) as exc_info:
        client_instance.ask("System", "User", "dummy-model")
    assert "не инициализирован" in str(exc_info.value)
