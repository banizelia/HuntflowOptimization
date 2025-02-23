import logging
from pathlib import Path

from dotenv import set_key


def update_env_file(key: str, value: str) -> None:
    """
    Обновляет или добавляет ключ `key` в .env (лежит рядом в той же папке config).
    """
    # Путь к .env внутри папки config:
    env_path = Path(__file__).resolve().parent / ".env"

    # Проверяем наличие .env
    if not env_path.exists():
        logging.error(f".env файл не найден по пути {env_path}")
        return

    # set_key — функция из python-dotenv, которая сама корректно редактирует .env.
    set_key(str(env_path), key, value)

    logging.info(f".env файл успешно обновлён: {key}={value}")
