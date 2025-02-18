import logging

logger = logging.getLogger(__name__)


def format_date(date_dict: dict) -> str:
    """
    Форматирует дату из словаря с полями year, month, day и precision.
    Если точность указана как 'year', выводится только год,
    если 'month' – год и месяц, если 'day' – полная дата.
    Если входные данные отсутствуют – возвращается "Не указана".
    """
    if not date_dict:
        return "Не указана"
    year = date_dict.get('year')
    month = date_dict.get('month')
    day = date_dict.get('day')
    precision = date_dict.get('precision', 'day')
    if not year:
        return "Не указана"
    if precision == 'year':
        return str(year)
    elif precision == 'month':
        return f"{year}-{month:02d}" if month else str(year)
    elif precision == 'day':
        if month and day:
            return f"{year}-{month:02d}-{day:02d}"
        else:
            return str(year)
    else:
        return str(year)


def format_experience(exp_list: list) -> str:
    """
    Форматирует список опытов работы из единого формата.
    Ожидается, что каждый опыт содержит:
      - date_from и date_to (словарь с датой)
      - company
      - position
      - description
    """
    result = ""
    for exp in exp_list:
        start = format_date(exp.get('date_from', {}))
        end = format_date(exp.get('date_to', {}))
        company = exp.get('company', 'Не указана')
        position = exp.get('position', 'Не указана')
        description = (exp.get('description') or '').strip()

        result += f"{start} — {end}\n"
        result += f"Компания: {company}\n"
        result += f"Должность: {position}\n"
        result += f"Описание:\n{description}\n\n"
    return result


def format_education(education: dict) -> str:
    """
    Форматирует раздел образования из единого формата.
    В данном примере берется список высших учебных заведений (ключ "higher").
    Каждый элемент содержит:
      - name (название ВУЗа)
      - faculty (факультет)
      - date_from и date_to (даты начала и окончания)
    Если требуется – можно добавить и другие типы образования.
    """
    result = ""
    higher = education.get('higher', [])
    for edu in higher:
        name = edu.get('name', '')
        faculty = edu.get('faculty', '')
        start = format_date(edu.get('date_from', {}))
        end = format_date(edu.get('date_to', {}))
        result += f"{name} ({faculty}, {start} - {end})\n"
    return result


def format_resume(resume: dict) -> str:
    """
    Форматирует резюме, используя данные из единого формата, содержащегося
    в поле 'resume' ответа API.

    Извлекаются такие разделы:
      — Личная информация (ФИО)
      — Позиция
      — Местоположение (из поля area)
      — Релокация
      — Навыки
      — Опыт работы
      — Образование
    """
    unified = resume.get('resume', {})
    logger.debug("Форматирование резюме в unified формате: %s", unified)

    position = unified.get('position', '')

    # Зарплатные ожидания
    wanted_salary = unified.get('wanted_salary', {})

    salary_amount = wanted_salary.get('amount', '')
    salary_currency = wanted_salary.get('currency', '')

    # Местоположение (из раздела area)
    area = unified.get('area', {})
    country = ""
    city = ""
    address = ""
    if area:
        if isinstance(area.get('country'), dict):
            country = area.get('country', {}).get('name', '')
        else:
            country = area.get('country', '')
        if isinstance(area.get('city'), dict):
            city = area.get('city', {}).get('name', '')
        else:
            city = area.get('city', '')
        address = area.get('address', '')

    # Релокация
    relocation = unified.get('relocation', {})
    if relocation:
        relocation_type = relocation.get('type', {}).get('name', 'Не указано')
        relocation_areas = relocation.get('area', [])
        if relocation_areas:
            destinations = []
            for area_item in relocation_areas:
                a_country = ""
                a_city = ""
                a_address = ""
                if isinstance(area_item.get('country'), dict):
                    a_country = area_item.get('country', {}).get('name', '')
                else:
                    a_country = area_item.get('country', '')
                if isinstance(area_item.get('city'), dict):
                    a_city = area_item.get('city', {}).get('name', '')
                else:
                    a_city = area_item.get('city', '')
                a_address = area_item.get('address', '')
                details = ", ".join(filter(None, [a_city, a_country, a_address]))
                if details:
                    destinations.append(details)
            relocation_destinations = "; ".join(destinations) if destinations else "Не указано"
        else:
            relocation_destinations = "Не указано"
    else:
        relocation_type = "Не указано"
        relocation_destinations = "Не указано"

    # Навыки (skill_set — список строк)
    skills = unified.get('skill_set', [])

    # Опыт работы
    exp_list = unified.get('experience', [])
    experience_str = format_experience(exp_list)

    # Образование (берем раздел higher)
    education = unified.get('education', {})
    education_str = format_education(education)

    formatted_resume = f"""
Позиция: {position}
Зарплатные ожидание: {salary_amount} + {salary_currency}

Местоположение: {city}, {country}, {address}
Готовность к переезду: {relocation_type}
Куда готов переехать: {relocation_destinations}

Навыки:
{", ".join(skills)}

Опыт работы:
{experience_str}

Образование:
{education_str}
"""
    logger.debug("Отформатированное резюме (Unified): %s", formatted_resume)
    return formatted_resume