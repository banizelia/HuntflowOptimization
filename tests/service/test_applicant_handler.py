from src.service.applicant_handler import handle_applicant


def test_handle_applicant_wrong_webhook_action(monkeypatch, caplog):
    data = {
        "meta": {"webhook_action": "OTHER_ACTION"},
        "event": {}
    }

    evaluate_called = False

    def dummy_evaluate_candidate(candidate_id, vacancy_id):
        nonlocal evaluate_called
        evaluate_called = True
        return None

    monkeypatch.setattr("src.service.applicant_handler.evaluate_candidate", dummy_evaluate_candidate)

    handle_applicant(data)
    assert "Обработка только для 'STATUS'" in caplog.text
    assert not evaluate_called


def test_handle_applicant_wrong_status(monkeypatch, caplog):
    data = {
        "meta": {"webhook_action": "STATUS"},
        "event": {
            "applicant_log": {"status": {"name": "Не Отклики"}}
        }
    }

    evaluate_called = False

    def dummy_evaluate_candidate(candidate_id, vacancy_id):
        nonlocal evaluate_called
        evaluate_called = True
        return None

    monkeypatch.setattr("src.service.applicant_handler.evaluate_candidate", dummy_evaluate_candidate)
    handle_applicant(data)
    assert "не соответствует 'Отклики'" in caplog.text
    assert not evaluate_called


def test_handle_applicant_missing_candidate_id(monkeypatch, caplog):
    data = {
        "meta": {"webhook_action": "STATUS"},
        "event": {
            "applicant_log": {
                "status": {"name": "Отклики"},
                "vacancy": {"id": 1}
            },
            "applicant": {}  # Нет candidate id
        }
    }
    handle_applicant(data)
    assert "ID кандидата не найден" in caplog.text


def test_handle_applicant_missing_vacancy_id(monkeypatch, caplog):
    data = {
        "meta": {"webhook_action": "STATUS"},
        "event": {
            "applicant_log": {
                "status": {"name": "Отклики"},
                "vacancy": {}  # Нет vacancy id
            },
            "applicant": {"id": 123}
        }
    }
    handle_applicant(data)
    assert "ID вакансии не найден" in caplog.text


def test_handle_applicant_success(monkeypatch):
    class DummyTargetStage:
        def __init__(self, value):
            self.value = value

    class DummyEvaluationAnswer:
        def __init__(self, target_stage, comment):
            self.target_stage = DummyTargetStage(target_stage)
            self.comment = comment

    dummy_answer = DummyEvaluationAnswer("приоритет", "dummy comment")
