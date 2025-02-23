import logging

from src.service.formatting.html_cleaner import clean_html

logger = logging.getLogger(__name__)


def format_vacancy(vacancy: dict) -> str:
    """
    Форматирует данные вакансии:
      — Извлекает позицию, ограничения по зарплате,
         описание, требования и условия работы.
      — Очищает HTML-теги из текстовых полей.
    """
    logger.debug("Форматирование вакансии: %s", vacancy)
    position = vacancy.get('position', 'Не указана должность')
    money = vacancy.get('money') or 'Не указана'

    body_html = vacancy.get('body', '')
    requirements_html = vacancy.get('requirements', '')
    conditions_html = vacancy.get('conditions', '')

    description = clean_html(body_html)
    requirements = clean_html(requirements_html)
    conditions = clean_html(conditions_html)

    formatted_description = (
        f"Вакансия: {position}\n"
        f"Ограничения по зп: {money}\n"
        "Описание вакансии:\n"
        f"{description}\n\n"
        "Требования:\n"
        f"{requirements}\n\n"
        "Условия работы:\n"
        f"{conditions}\n"
    )
    logger.debug("Отформатированное описание вакансии: %s", formatted_description)
    return formatted_description

