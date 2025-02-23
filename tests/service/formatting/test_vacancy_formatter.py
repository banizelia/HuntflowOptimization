from src.service.formatting.vacancy_formatter import format_vacancy


def test_format_vacancy_minimal():
    vacancy = {}
    expected = (
        "Вакансия: Не указана должность\n"
        "Ограничения по зп: Не указана\n"
        "Описание вакансии:\n"
        "\n\n"
        "Требования:\n"
        "\n\n"
        "Условия работы:\n"
        "\n"
    )
    result = format_vacancy(vacancy)
    assert result == expected


def test_format_vacancy_with_html():
    vacancy = {
        "position": "Software Developer",
        "money": "120000 RUB",
        "body": "<p>Develop and maintain applications.</p>",
        "requirements": "<ul><li>Python</li><li>Flask</li></ul>",
        "conditions": "<div>Full-time, Remote</div>"
    }
    expected = (
        "Вакансия: Software Developer\n"
        "Ограничения по зп: 120000 RUB\n"
        "Описание вакансии:\n"
        "Develop and maintain applications.\n\n"
        "Требования:\n"
        "PythonFlask\n\n"
        "Условия работы:\n"
        "Full-time, Remote\n"
    )
    result = format_vacancy(vacancy)
    assert result == expected


def test_format_vacancy_missing_fields():
    vacancy = {
        "position": "QA Engineer",
        "body": "<p>Testing software</p>"
    }
    expected = (
        "Вакансия: QA Engineer\n"
        "Ограничения по зп: Не указана\n"
        "Описание вакансии:\n"
        "Testing software\n\n"
        "Требования:\n"
        "\n\n"
        "Условия работы:\n"
        "\n"
    )
    result = format_vacancy(vacancy)
    assert result == expected
