import logging
import pytest
from src.config.logging_config import setup_logging

def test_setup_logging_configures_root_logger():
    setup_logging()
    root_logger = logging.getLogger()

    assert root_logger.level == logging.INFO, "Уровень логгера должен быть INFO"

    stream_handlers = [handler for handler in root_logger.handlers if isinstance(handler, logging.StreamHandler)]
    assert stream_handlers, "В корневом логгере не найдено StreamHandler"

    expected_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    for handler in stream_handlers:
        if handler.formatter:
            assert handler.formatter._fmt == expected_format, "Формат логирования не соответствует ожидаемому"
            break
    else:
        pytest.fail("Ни один из обработчиков не имеет настроенного форматтера")
