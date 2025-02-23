import logging
import re

logger = logging.getLogger(__name__)


def clean_html(raw_html: str) -> str:
    """
    Удаляет HTML-тэги из строки.
    """
    logger.debug("Очистка HTML от тэгов. Исходный HTML: %s", raw_html)
    clean_re = re.compile('<.*?>')
    result = re.sub(clean_re, '', raw_html).strip()
    logger.debug("Результат очистки HTML: %s", result)
    return result
