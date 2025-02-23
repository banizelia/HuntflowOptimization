from src.service.formatting.resume_formatter import format_resume


def test_format_resume_minimal():
    resume_data = {
        "resume": {
            "position": "Software Engineer",
            "wanted_salary": {"amount": "100000", "currency": "RUB"},
            "area": {"country": "Россия", "city": "Пермь", "address": "Улица Ленина"},
            "relocation": {},
            "skill_set": ["Python", "Flask"],
            "experience": [],
            "education": {}
        }
    }

    formatted = format_resume(resume_data)
    assert "Позиция: Software Engineer" in formatted
    assert "100000" in formatted
    assert "RUB" in formatted
    assert "Пермь" in formatted
    assert "Python, Flask" in formatted
    assert "Опыт работы:" in formatted
    assert "Образование:" in formatted


def test_format_resume_full():
    resume_data = {
        "resume": {
            "position": "Data Scientist",
            "wanted_salary": {"amount": "150000", "currency": "RUB"},
            "area": {
                "country": {"name": "Россия"},
                "city": {"name": "Москва"},
                "address": "ул. Тверская"
            },
            "relocation": {
                "type": {"name": "Готов к переезду"},
                "area": [
                    {
                        "country": {"name": "Россия"},
                        "city": {"name": "Санкт-Петербург"},
                        "address": "Невский проспект"
                    }
                ]
            },
            "skill_set": ["Python", "Machine Learning", "Statistics"],
            "experience": [
                {
                    "date_from": {"year": 2018, "month": 1, "day": 1, "precision": "day"},
                    "date_to": {"year": 2020, "month": 12, "day": 31, "precision": "day"},
                    "company": "Tech Corp",
                    "position": "Data Analyst",
                    "description": "Анализ данных и построение моделей."
                }
            ],
            "education": {
                "higher": [
                    {
                        "name": "МГУ",
                        "faculty": "Факультет ВМК",
                        "date_from": {"year": 2014, "month": 9, "day": 1, "precision": "day"},
                        "date_to": {"year": 2018, "month": 6, "day": 30, "precision": "day"}
                    }
                ]
            }
        }
    }

    formatted = format_resume(resume_data)
    assert "Позиция: Data Scientist" in formatted
    assert "150000" in formatted
    assert "RUB" in formatted
    assert "Москва" in formatted
    assert "Готов к переезду" in formatted
    assert "Санкт-Петербург" in formatted
    assert "Python, Machine Learning, Statistics" in formatted
    assert "Tech Corp" in formatted
    assert "Data Analyst" in formatted
    assert "2018-01-01" in formatted
    assert "2020-12-31" in formatted
    assert "МГУ (Факультет ВМК, 2014-09-01 - 2018-06-30)" in formatted
