import requests

from src.api_clients import huntflow_api


class DummyResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.RequestException("HTTP Error")


def test_refresh_access_token_success(monkeypatch):
    dummy_response = DummyResponse(200, {
        "access_token": "new_api_token",
        "refresh_token": "new_refresh_token"
    })
    monkeypatch.setattr(huntflow_api.session, "post", lambda url, json, headers: dummy_response)
    monkeypatch.setattr(huntflow_api, "update_and_reload_env", lambda key, value: None)

    token = huntflow_api.refresh_access_token()
    assert token == "new_api_token"
    assert huntflow_api.session.headers["Authorization"] == "Bearer new_api_token"


def test_refresh_access_token_failure(monkeypatch):
    def dummy_post(url, json, headers):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(huntflow_api.session, "post", dummy_post)
    token = huntflow_api.refresh_access_token()
    assert token is None


def test_create_applicant_success(monkeypatch):
    applicant_data = {"name": "John Doe"}
    dummy_response = DummyResponse(200, {"id": 123})

    monkeypatch.setattr(huntflow_api.session, "request", lambda method, url, **kwargs: dummy_response)
    applicant_id = huntflow_api.create_applicant(applicant_data)
    assert applicant_id == 123


def test_create_applicant_token_expired(monkeypatch):
    applicant_data = {"name": "John Doe"}
    dummy_response_401 = DummyResponse(401, {"errors": [{"detail": "token_expired"}]})
    dummy_response_success = DummyResponse(200, {"id": 456})
    call_count = {"count": 0}

    def dummy_request(method, url, **kwargs):
        if call_count["count"] == 0:
            call_count["count"] += 1
            return dummy_response_401
        else:
            return dummy_response_success

    monkeypatch.setattr(huntflow_api.session, "request", dummy_request)
    monkeypatch.setattr(huntflow_api, "refresh_access_token", lambda: "refreshed_token")
    applicant_id = huntflow_api.create_applicant(applicant_data)
    assert applicant_id == 456


def test_get_status_id_by_name(monkeypatch):
    statuses = [
        {"id": 1, "name": "отклики"},
        {"id": 2, "name": "приоритет"},
        {"id": 3, "name": "резерв"}
    ]
    monkeypatch.setattr(huntflow_api, "get_statuses", lambda: statuses)
    status_id = huntflow_api.get_status_id_by_name("Приоритет")
    assert status_id == 2

    status_id_none = huntflow_api.get_status_id_by_name("неизвестный")
    assert status_id_none is None


def test_send_request_success(monkeypatch):
    dummy_resp = DummyResponse(200, {"result": "ok"})
    monkeypatch.setattr(huntflow_api.session, "request", lambda method, url, **kwargs: dummy_resp)
    response = huntflow_api.send_request("GET", "http://example.com")
    assert response.json() == {"result": "ok"}


def test_send_request_token_expired(monkeypatch):
    dummy_resp_401 = DummyResponse(401, {"errors": [{"detail": "token_expired"}]})
    dummy_resp_success = DummyResponse(200, {"result": "ok"})
    call_count = {"count": 0}

    def dummy_request(method, url, **kwargs):
        if call_count["count"] == 0:
            call_count["count"] += 1
            return dummy_resp_401
        else:
            return dummy_resp_success

    monkeypatch.setattr(huntflow_api.session, "request", dummy_request)
    monkeypatch.setattr(huntflow_api, "refresh_access_token", lambda: "refreshed_token")
    response = huntflow_api.send_request("GET", "http://example.com")
    assert response.json() == {"result": "ok"}


def test_get_vacancies(monkeypatch):
    dummy_resp = DummyResponse(200, {
        "items": [
            {"id": 1, "title": "Vacancy 1"},
            {"id": 2, "title": "Vacancy 2"}
        ]
    })
    monkeypatch.setattr(huntflow_api, "send_request", lambda method, url, **kwargs: dummy_resp)
    vacancies = huntflow_api.get_vacancies()
    assert isinstance(vacancies, list)
    assert len(vacancies) == 2
    assert vacancies[0]["title"] == "Vacancy 1"


def test_get_vacancy(monkeypatch):
    dummy_data = {"id": 10, "title": "Vacancy Title"}
    dummy_resp = DummyResponse(200, dummy_data)
    monkeypatch.setattr(huntflow_api, "send_request", lambda method, url, **kwargs: dummy_resp)
    vacancy = huntflow_api.get_vacancy(10)
    assert vacancy == dummy_data


def test_update_candidate_status(monkeypatch):
    dummy_data = {"status": "updated"}
    dummy_resp = DummyResponse(200, dummy_data)
    monkeypatch.setattr(huntflow_api, "send_request", lambda method, url, **kwargs: dummy_resp)
    result = huntflow_api.update_applicant_status(1, 2, 3, "Test comment")
    assert result == dummy_data


def test_add_comment(monkeypatch):
    dummy_data = {"comment": "added"}
    dummy_resp = DummyResponse(200, dummy_data)
    monkeypatch.setattr(huntflow_api, "send_request", lambda method, url, **kwargs: dummy_resp)
    result = huntflow_api.add_comment(1, 2, 3, "Test comment")
    assert result == dummy_data


def test_get_statuses(monkeypatch):
    dummy_items = [
        {"id": 1, "name": "Status 1", "removed": None},
        {"id": 2, "name": "Status 2", "removed": "yes"}
    ]
    dummy_resp = DummyResponse(200, {"items": dummy_items})
    monkeypatch.setattr(huntflow_api, "send_request", lambda method, url, **kwargs: dummy_resp)
    statuses = huntflow_api.get_statuses()
    assert len(statuses) == 1
    assert statuses[0]["name"] == "Status 1"


def test_get_vacancy_desc(monkeypatch):
    dummy_data = {"id": 10, "description": "Vacancy description"}
    dummy_resp = DummyResponse(200, dummy_data)
    monkeypatch.setattr(huntflow_api, "send_request", lambda method, url, **kwargs: dummy_resp)
    desc = huntflow_api.get_vacancy_desc(10)
    assert desc == dummy_data


def test_get_resume(monkeypatch):
    dummy_data = {"resume": "data"}
    dummy_resp = DummyResponse(200, dummy_data)
    monkeypatch.setattr(huntflow_api, "send_request", lambda method, url, **kwargs: dummy_resp)
    resume = huntflow_api.get_resume(1, "external_1")
    assert resume == dummy_data


def test_get_applicant(monkeypatch):
    dummy_data = {"id": 1, "name": "Applicant Name"}
    dummy_resp = DummyResponse(200, dummy_data)
    monkeypatch.setattr(huntflow_api, "send_request", lambda method, url, **kwargs: dummy_resp)
    applicant = huntflow_api.get_applicant(1)
    assert applicant == dummy_data


def test_get_applicants(monkeypatch):
    first_page = {"items": [{"id": 1}, {"id": 2}], "next": True}
    second_page = {"items": [{"id": 3}], "next": None}
    call_count = {"count": 0}

    def dummy_request(method, url, **kwargs):
        if call_count["count"] == 0:
            call_count["count"] += 1
            return DummyResponse(200, first_page)
        else:
            return DummyResponse(200, second_page)

    monkeypatch.setattr(huntflow_api, "send_request",
                        lambda method, url, **kwargs: dummy_request(method, url, **kwargs))
    applicants = huntflow_api.get_applicants(1, 2)
    assert len(applicants) == 3
