import os
from pathlib import Path

from src.env_loader import load_dotenv_exports


def test_load_dotenv_exports_sets_environment_variables(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        'export OPENROUTER_API_KEY="test-key"\nOPENROUTER_MODEL="test/model"\n# comment\n',
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)

    loaded = load_dotenv_exports(env_path)

    assert loaded == ["OPENROUTER_API_KEY", "OPENROUTER_MODEL"]
    assert os.environ["OPENROUTER_API_KEY"] == "test-key"
    assert os.environ["OPENROUTER_MODEL"] == "test/model"
