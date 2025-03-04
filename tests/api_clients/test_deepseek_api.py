from src.api_clients.deepseek_api import ask_deepseek, deepseek_client


# Фиктивные классы для эмуляции возвращаемой структуры
class DummyMessage:
    def __init__(self, content):
        self.content = content


class DummyChoice:
    def __init__(self, message):
        self.message = message


class DummyCompletion:
    def __init__(self, content):
        # Формируем список с единственным элементом, содержащим message с нужным содержимым.
        self.choices = [DummyChoice(DummyMessage(content))]


# Функция-замена для deepseek_client.ask, возвращающая фиктивный объект DummyCompletion.
def dummy_ask(system_prompt, user_prompt, model):
    # Можно добавить проверки входных параметров, если требуется.
    return DummyCompletion("expected answer")


# Тест для функции ask_deepseek с явным указанием модели
def test_ask_deepseek(monkeypatch):
    # Подменяем метод ask у deepseek_client на нашу фиктивную реализацию.
    monkeypatch.setattr(deepseek_client, "ask", dummy_ask)

    system_prompt = "Test system prompt"
    user_prompt = "Test user prompt"
    model = "dummy-model"

    answer = ask_deepseek(system_prompt, user_prompt, model)
    assert answer == "expected answer"


# Тест для функции ask_deepseek с использованием значения по умолчанию для model
def test_ask_deepseek_default_model(monkeypatch):
    # Подменяем метод ask у deepseek_client на фиктивный, возвращающий другой текст.
    monkeypatch.setattr(deepseek_client, "ask", lambda sp, up, m: DummyCompletion("default answer"))

    answer = ask_deepseek("System prompt", "User prompt")
    assert answer == "default answer"
