# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import pytest
from pathlib import Path
import stockwatch.use_cases.configuring as cfg
import sys
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@pytest.fixture
def test_config(monkeypatch: pytest.MonkeyPatch) -> cfg.Config:
    # here do monkeypatching of get_app_basename and _get_stored_config

    def mock_get_configfile_path() -> Path:
        return Path(__file__)

    def mock_tomllib_load(
        fptr: Any,  # pylint: disable=unused-argument
    ) -> dict[str, dict[str, str]]:
        return {
            "degiro_server": {
                "country": "NL",
                "lang": "nl",
                "ga_ext": "/totp",
                "login_url": "https://trader.degiro.nl/login/secure/login",
                "client_url": "https://trader.degiro.nl/pa/secure/client",
                "portfolio_url": "https://trader.degiro.nl/reporting/secure/v3/positionReport/csv",
                "account_url": "https://trader.degiro.nl/reporting/secure/v3/cashAccountReport/csv",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",
                "unknown_field": "22",
            }
        }

    monkeypatch.setattr(cfg.Config, "get_configfile_path", mock_get_configfile_path)
    monkeypatch.setattr(tomllib, "load", mock_tomllib_load)
    return cfg.Config.get()


def test_get_config_path() -> None:
    assert cfg.Config.get_configfile_path().parts[-1] == "config.toml"
    assert cfg.Config.get_configfile_path().parts[-2] == ".stockwatch"


def test_get_stored_config() -> None:
    with pytest.raises(FileNotFoundError):
        cfg.Config.get()


def test_get(test_config: cfg.Config) -> None:
    assert test_config.degiro_server.lang == "nl"
