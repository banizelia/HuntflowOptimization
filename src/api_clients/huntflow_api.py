import logging
import os
from typing import Optional, List, Dict, Any

import requests

from src.config.env_updater import update_env_file

HUNTFLOW_BASE_URL = os.getenv('HUNTFLOW_BASE_URL')
HUNTFLOW_API_TOKEN = os.getenv('HUNTFLOW_API_TOKEN')
HUNTFLOW_REFRESH_TOKEN = os.getenv('HUNTFLOW_REFRESH_TOKEN')
HUNTFLOW_ACCOUNT_ID = os.getenv('HUNTFLOW_ACCOUNT_ID')

headers = {
    'Authorization': f'Bearer {HUNTFLOW_API_TOKEN}',
    'Content-Type': 'application/json'
}

session = requests.Session()
session.headers.update(headers)


def refresh_access_token() -> Optional[str]:
    refresh_url = f"{HUNTFLOW_BASE_URL}/token/refresh"
    payload = {"refresh_token": HUNTFLOW_REFRESH_TOKEN}
    try:
        response = session.post(
            refresh_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        data = response.json()
        new_access_token = data.get('access_token')
        new_refresh_token = data.get('refresh_token')

        if new_access_token and new_refresh_token:
            session.headers['Authorization'] = f'Bearer {new_access_token}'

            update_env_file('HUNTFLOW_API_TOKEN', new_access_token)
            update_env_file('HUNTFLOW_REFRESH_TOKEN', new_refresh_token)

            logging.info('Tokens successfully refreshed.')
            return new_access_token
        else:
            logging.error('Failed to obtain new tokens from the response.')
            return None
    except requests.RequestException as e:
        logging.error(f"Error refreshing tokens: {e}")
        return None


def send_request(method: str, url: str, **kwargs) -> requests.Response:
    """
    Универсальная функция отправки HTTP-запросов, которая при получении 401 с detail "token_expired"
    пытается обновить токен и повторить запрос.
    """
    response = session.request(method, url, **kwargs)
    if response.status_code == 401:
        try:
            error = response.json().get("errors", [{}])[0]
        except Exception:
            error = {}
        if error.get("detail") == "token_expired":
            logging.info("Token expired. Refreshing token...")
            if refresh_access_token():
                response = session.request(method, url, **kwargs)
    response.raise_for_status()
    return response


def create_applicant(applicant_data: Dict[str, Any]) -> Optional[int]:
    url = f"{HUNTFLOW_BASE_URL}/accounts/{HUNTFLOW_ACCOUNT_ID}/applicants"
    try:
        response = send_request("POST", url, json=applicant_data)
        result = response.json()
        applicant_id = result.get("id")
        logging.info(f"Applicant created with ID: {applicant_id}")
        return applicant_id
    except requests.RequestException as e:
        logging.error(f"Error creating applicant: {e}")
        return None


def get_status_id_by_name(status_name: str):
    statuses = get_statuses()
    status_info = next(
        (status for status in statuses if status.get("name", "").lower() == status_name.lower()),
        None
    )
    # todo: Если статус не найден, можно добавить обработку этой ситуации
    return status_info.get('id') if status_info else None


def get_vacancies(
        state: str = "OPEN",
        count: int = 50,
        page: int = 1,
        mine: bool = False
) -> List[Dict[str, Any]]:
    url = f"{HUNTFLOW_BASE_URL}/accounts/{HUNTFLOW_ACCOUNT_ID}/vacancies"
    params = {"state": state, "count": count, "page": page, "mine": mine}
    try:
        response = send_request("GET", url, params=params)
        return response.json().get('items', [])
    except requests.RequestException as e:
        logging.error(f"Error fetching vacancies: {e}")
        return []


def get_vacancy(vacancy_id):
    url = f"{HUNTFLOW_BASE_URL}/accounts/{HUNTFLOW_ACCOUNT_ID}/vacancies/{vacancy_id}"
    try:
        response = send_request("GET", url)
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching vacancy details: {e}")
        return None


def update_candidate_status(applicant_id: int, target_status_id: int, vacancy_id: int, comment: str) -> Optional[
    Dict[str, Any]]:
    params = {"status": target_status_id, "vacancy": vacancy_id, "comment": comment}
    url = f"{HUNTFLOW_BASE_URL}/accounts/{HUNTFLOW_ACCOUNT_ID}/applicants/{applicant_id}/vacancy"
    try:
        response = send_request("PUT", url, json=params)
        data = response.json()
        logging.info(f"Updated candidate {applicant_id} to status {target_status_id}.")
        return data
    except requests.RequestException as e:
        logging.error(f"Error updating candidate status: {e}")
        return None


def add_comment(applicant_id: int, vacancy_id: int, status_id: int, text: str) -> Optional[Dict[str, Any]]:
    params = {"vacancy": vacancy_id, "status": status_id, "comment": text}
    url = f"{HUNTFLOW_BASE_URL}/accounts/{HUNTFLOW_ACCOUNT_ID}/applicants/{applicant_id}/vacancy"
    try:
        response = send_request("PUT", url, json=params)
        data = response.json()
        logging.info(f"Added comment to candidate {applicant_id}.")
        return data
    except requests.RequestException as e:
        logging.error(f"Error adding comment: {e}")
        return None


def get_statuses(removed: bool = False) -> List[Dict[str, Any]]:
    url = f"{HUNTFLOW_BASE_URL}/accounts/{HUNTFLOW_ACCOUNT_ID}/vacancies/statuses"
    try:
        response = send_request("GET", url)
        statuses = response.json().get('items', [])
        if not removed:
            statuses = [status for status in statuses if status.get('removed') is None]
        return statuses
    except requests.RequestException as e:
        logging.error(f"Error fetching statuses: {e}")
        return []


def get_vacancy_desc(vacancy_id):
    url = f"{HUNTFLOW_BASE_URL}/accounts/{HUNTFLOW_ACCOUNT_ID}/vacancies/{vacancy_id}"
    try:
        response = send_request("GET", url)
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching vacancy description: {e}")
        return []


def get_resume(applicant_id, external_id):
    url = f"{HUNTFLOW_BASE_URL}/accounts/{HUNTFLOW_ACCOUNT_ID}/applicants/{applicant_id}/externals/{external_id}"
    try:
        response = send_request("GET", url)
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching resume: {e}")
        return []


def get_applicant(applicant_id):
    url = f"{HUNTFLOW_BASE_URL}/accounts/{HUNTFLOW_ACCOUNT_ID}/applicants/{applicant_id}"
    try:
        response = send_request("GET", url)
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching applicant: {e}")
        raise


def get_applicants(vacancy_id: int, status_id: int) -> List[Dict[str, Any]]:
    url = f"{HUNTFLOW_BASE_URL}/accounts/{HUNTFLOW_ACCOUNT_ID}/applicants"
    params = {'vacancy': vacancy_id, 'status': status_id, 'limit': 100, 'offset': 0}
    candidates = []
    while True:
        try:
            response = send_request("GET", url, params=params)
            data = response.json()
            candidates.extend(data.get('items', []))
            if not data.get('next'):
                break
            params['offset'] += params['limit']
        except requests.RequestException as e:
            logging.error(f"Error fetching applicants: {e}")
            break
    return candidates
