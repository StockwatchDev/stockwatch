# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
from pathlib import Path
import pytest
import stockwatch.use_cases.configuring as cfg


@pytest.fixture
def test_config(monkeypatch) -> cfg.Config:
    # here do monkeypatching of get_configfile_path and _get_stored_config

    def mock_get_configfile_path() -> Path:
        return Path("/abc")

    def mock_get_stored_config() -> dict[str, dict[str, str]]:
        return {
            "degiro_server": {
                "country": "NL",
                "lang": "nl",
                "ga_ext": "/totp",
                "login_url": "https://trader.degiro.nl/login/secure/login",
                "client_url": "https://trader.degiro.nl/pa/secure/client",
                "portfolio_url": "https://trader.degiro.nl/reporting/secure/v3/positionReport/csv",
                "account_url": "https://trader.degiro.nl/reporting/secure/v3/cashAccountReport/csv",
            }
        }

    monkeypatch.setattr(cfg, "get_configfile_path", mock_get_configfile_path)
    monkeypatch.setattr(cfg.Config, "_get_stored_config", mock_get_stored_config)
    return cfg.Config.get()


def test_get_config_path(test_config) -> None:
    assert test_config.get_configfile_path().parts[-1] == "stockwatch.toml"
