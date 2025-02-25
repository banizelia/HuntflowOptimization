import logging
import os
from dotenv import load_dotenv, set_key
from pathlib import Path


def update_and_reload_env(key: str, new_value: str):
    env_path = Path(__file__).resolve().parent / ".env"

    if not env_path.exists():
        logging.error(f".env not found: {env_path}")
        return

    set_key(str(env_path), key, new_value)

    load_dotenv(dotenv_path=env_path)

    updated_value = os.getenv(key)

    return updated_value