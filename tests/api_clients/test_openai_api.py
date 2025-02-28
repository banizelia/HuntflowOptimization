import logging

import pytest

from src.api_clients.openai_api import get_client, ask_gpt
from src.model.candidate_evaluation_answer import CandidateEvaluationAnswer
from src.model.target_stage import TargetStage


# Определяем вспомогательные классы для имитации ответа от OpenAI

class DummyMessage:
    def __init__(self, parsed):
        self.parsed = parsed

class DummyChoice:
    def __init__(self, parsed):
        self.message = DummyMessage(parsed)

class DummyCompletion:
    def __init__(self, choices):
        self.choices = choices


class DummyOpenAI:
    def __init__(self, api_key):
        self.api_key = api_key
        # Для поддержки цепочки вызовов: client.beta.chat.completions.parse(...)
        self.beta = self
        self.chat = self
        self.completions = self

    def parse(self, model, messages, response_format):
        # По умолчанию возвращаем фиктивный ответ,
        # но тесты могут переопределить эту функцию
        dummy_answer = CandidateEvaluationAnswer(
            target_stage=TargetStage.NEW,
            comment="Default dummy answer"
        )
        return DummyCompletion([DummyChoice(dummy_answer)])


# Фикстура для сброса глобального клиента перед каждым тестом
@pytest.fixture(autouse=True)
def reset_client(monkeypatch):
    from src.api_clients import openai_api
    openai_api._client = None


def test_get_client_with_token(monkeypatch, caplog):
    test_token = "test_token"
    monkeypatch.setenv("CHATGPT_API_TOKEN", test_token)
    monkeypatch.setattr("src.api_clients.openai_api.OpenAI", DummyOpenAI)

    with caplog.at_level(logging.INFO):
        client_instance = get_client()
        assert client_instance.api_key == test_token

    # Проверяем, что при повторном вызове возвращается тот же объект (кеширование)
    client_instance2 = get_client()
    assert client_instance is client_instance2

    # Проверяем, что в логах присутствуют сообщения об успешном создании клиента
    assert "Клиент OpenAI успешно создан" in caplog.text


def test_get_client_no_token(monkeypatch, caplog):
    # Удаляем переменную окружения, чтобы смоделировать отсутствие токена
    monkeypatch.delenv("CHATGPT_API_TOKEN", raising=False)
    monkeypatch.setattr("src.api_clients.openai_api.OpenAI", DummyOpenAI)

    with caplog.at_level(logging.ERROR):
        client_instance = get_client()

        # Проверяем, что клиент действительно не был создан (возвращается None)
        assert client_instance is None

    # Проверяем, что в логах появилось сообщение об отсутствии токена
    assert "API токен для ChatGPT не найден!" in caplog.text
    # Лог "Клиент OpenAI успешно создан" не должен появляться
    assert "Клиент OpenAI успешно создан" not in caplog.text


def test_ask_gpt(monkeypatch):
    vacancy_description = "Test vacancy description"
    candidate_resume = "Test candidate resume"

    # Создаем фиктивный ответ, который должен вернуть ask_gpt
    dummy_answer = CandidateEvaluationAnswer(
        target_stage=TargetStage.NEW,
        comment="Good candidate"
    )

    # Определяем фиктивную функцию parse, которая вернет наш dummy_answer
    def dummy_parse(model, messages, response_format):
        # Можно дополнительно проверить, что параметры (model, messages) сформированы корректно
        return DummyCompletion([DummyChoice(dummy_answer)])

    # Создаем фиктивного клиента с переопределенной функцией parse
    dummy_client = DummyOpenAI(api_key="dummy")
    dummy_client.beta.chat.completions.parse = dummy_parse

    # Подменяем функцию get_client, чтобы она возвращала нашего dummy_client
    monkeypatch.setattr("src.api_clients.openai_api.get_client", lambda: dummy_client)

    result = ask_gpt(vacancy_description, candidate_resume)
    assert isinstance(result, CandidateEvaluationAnswer)
    assert result.target_stage == TargetStage.NEW
    assert result.comment == "Good candidate"
