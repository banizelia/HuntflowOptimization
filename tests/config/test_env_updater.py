import logging

from src.config import env_updater


def test_update_env_file_success(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY1=old_value\n")
    monkeypatch.setattr(env_updater, "__file__", str(tmp_path / "fake_env_updater.py"))
    env_updater.update_and_reload_env("KEY1", "new_value")
    content = env_file.read_text()
    assert "KEY1='new_value'" in content


def test_update_env_file_file_not_exist(tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(env_updater, "__file__", str(tmp_path / "fake_env_updater.py"))
    env_file = tmp_path / ".env"
    if env_file.exists():
        env_file.unlink()
    with caplog.at_level(logging.ERROR):
        env_updater.update_and_reload_env("KEY2", "value2")
    assert ".env not found:" in caplog.text
