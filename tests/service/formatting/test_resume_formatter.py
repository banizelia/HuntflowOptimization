import pytest

from src.service.formatting.resume_formatter import format_date, format_education, format_experience, format_resume


# Тесты для format_date
def test_format_date_empty():
    # Если передан пустой словарь – возвращаем "Не указана"
    assert format_date({}) == "Не указана"

def test_format_date_no_year():
    # Если год отсутствует – возвращаем "Не указана"
    data = {"month": 1, "day": 1, "precision": "day"}
    assert format_date(data) == "Не указана"

def test_format_date_year_precision():
    data = {"year": 2023, "precision": "year"}
    assert format_date(data) == "2023"

def test_format_date_month_precision_with_month():
    data = {"year": 2023, "month": 5, "precision": "month"}
    assert format_date(data) == "2023-05"

def test_format_date_month_precision_without_month():
    data = {"year": 2023, "precision": "month"}
    assert format_date(data) == "2023"

def test_format_date_day_precision_with_full_date():
    data = {"year": 2023, "month": 5, "day": 15, "precision": "day"}
    assert format_date(data) == "2023-05-15"

def test_format_date_day_precision_missing_day():
    data = {"year": 2023, "month": 5, "precision": "day"}
    # Если отсутствует day, возвращаем год
    assert format_date(data) == "2023"

def test_format_date_unknown_precision():
    data = {"year": 2023, "precision": "unknown"}
    assert format_date(data) == "2023"


# Тест для format_experience
def test_format_experience():
    exp_list = [
        {
            "date_from": {"year": 2020, "month": 1, "day": 1, "precision": "day"},
            "date_to": {"year": 2021, "month": 12, "day": 31, "precision": "day"},
            "company": "Company A",
            "position": "Developer",
            "description": "Worked on project X."
        },
        {
            "date_from": {"year": 2018, "precision": "year"},
            "date_to": {"year": 2019, "precision": "year"},
            "company": "Company B",
            "position": "Intern",
            "description": "Internship experience."
        }
    ]
    expected = (
        "2020-01-01 — 2021-12-31\n"
        "Компания: Company A\n"
        "Должность: Developer\n"
        "Описание:\nWorked on project X.\n\n"
        "2018 — 2019\n"
        "Компания: Company B\n"
        "Должность: Intern\n"
        "Описание:\nInternship experience.\n\n"
    )
    assert format_experience(exp_list) == expected


# Тест для format_education
def test_format_education():
    education = {
        "higher": [
            {
                "name": "University A",
                "faculty": "Engineering",
                "date_from": {"year": 2010, "precision": "year"},
                "date_to": {"year": 2014, "precision": "year"}
            },
            {
                "name": "University B",
                "faculty": "Science",
                "date_from": {"year": 2015, "month": 9, "precision": "month"},
                "date_to": {"year": 2019, "month": 6, "precision": "month"}
            }
        ]
    }
    expected = (
        "University A (Engineering, 2010 - 2014)\n"
        "University B (Science, 2015-09 - 2019-06)\n"
    )
    assert format_education(education) == expected


# Тест для format_resume
def test_format_resume():
    unified = {
        "position": "Software Engineer",
        "wanted_salary": {"amount": "150000", "currency": "RUB"},
        "skill_set": ["Python", "Django"],
        "experience": [
            {
                "date_from": {"year": 2018, "month": 2, "day": 1, "precision": "day"},
                "date_to": {"year": 2020, "month": 5, "day": 31, "precision": "day"},
                "company": "TechCorp",
                "position": "Developer",
                "description": "Developed backend systems."
            }
        ],
        "education": {
            "higher": [
                {
                    "name": "MIT",
                    "faculty": "Computer Science",
                    "date_from": {"year": 2014, "precision": "year"},
                    "date_to": {"year": 2018, "precision": "year"}
                }
            ]
        }
    }
    result = format_resume(unified)
    # Проверяем наличие основных частей резюме
    assert "Позиция: Software Engineer" in result
    assert "150000" in result
    assert "RUB" in result
    assert "Python, Django" in result
    assert "TechCorp" in result
    assert "Developer" in result
    assert "MIT" in result
    assert "Computer Science" in result

def test_format_resume_none():
    # Если входные данные отсутствуют, функция должна вернуть пустую строку
    assert format_resume(None) == ""
