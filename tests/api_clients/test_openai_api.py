from src.api_clients.openai_api import ask_gpt, openai_client


# Фиктивные классы для эмуляции возвращаемой структуры
class DummyMessage:
    def __init__(self, parsed):
        self.parsed = parsed


class DummyChoice:
    def __init__(self, message):
        self.message = message


class DummyCompletion:
    def __init__(self, parsed):
        self.choices = [DummyChoice(DummyMessage(parsed))]


# Функция-замена, возвращающая сообщение, зависящее от параметра model.
def dummy_ask_echo(system_prompt, user_prompt, model, response_format=None):
    # Для наглядности возвращаем строку, зависящую от переданного model.
    return DummyCompletion("got: " + model)


# Тест: если модель не указана явно, должна использоваться модель по умолчанию ("gpt-4o")
def test_ask_gpt_default_model(monkeypatch):
    monkeypatch.setattr(openai_client, "ask", dummy_ask_echo)

    result = ask_gpt("System prompt", "User prompt", response_format=str)
    assert result == "got: gpt-4o"


# Тест: при явном указании модели функция возвращает ответ, зависящий от указанной модели.
def test_ask_gpt_custom_model(monkeypatch):
    monkeypatch.setattr(openai_client, "ask", dummy_ask_echo)

    result = ask_gpt("System prompt", "User prompt", response_format=int, model="custom-model")
    assert result == "got: custom-model"
