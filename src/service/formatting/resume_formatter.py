import logging

logger = logging.getLogger()

def format_date(date_dict: dict) -> str:
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
    result = ""
    higher = education.get('higher', [])
    for edu in higher:
        name = edu.get('name', '')
        faculty = edu.get('faculty', '')
        start = format_date(edu.get('date_from', {}))
        end = format_date(edu.get('date_to', {}))
        result += f"{name} ({faculty}, {start} - {end})\n"
    return result


def format_resume(unified_resume: dict) -> str:
    if unified_resume is None:
        return ""

    position = unified_resume.get('position', '')

    # Зарплатные ожидания
    wanted_salary = unified_resume.get('wanted_salary', {})

    salary_amount = wanted_salary.get('amount', '')
    salary_currency = wanted_salary.get('currency', '')

    # Навыки (skill_set — список строк)
    skills = unified_resume.get('skill_set', [])

    # Опыт работы
    exp_list = unified_resume.get('experience', [])
    experience_str = format_experience(exp_list)

    # Образование (берем раздел higher)
    education = unified_resume.get('education', {})
    education_str = format_education(education)

    formatted_resume = f"""
        Позиция: {position}
        Зарплатные ожидание: {salary_amount} + {salary_currency}

        Навыки: {", ".join(skills)}

        Опыт работы: 
        {experience_str}

        Образование:
        {education_str}
    """

    logger.debug("Отформатированное резюме (Unified): %s", formatted_resume)
    return formatted_resume
