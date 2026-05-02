from pathlib import Path


def read_required_config() -> str:
    config_path = Path(__file__).with_name("required_config.toml")
    try:
        return config_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError("required config file not found: required_config.toml") from exc


def test_required_config_exists() -> None:
    assert read_required_config()
