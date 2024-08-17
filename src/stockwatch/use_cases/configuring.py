"""Module for defining configuration."""
from pathlib import Path

from application_settings import ConfigBase, ConfigSectionBase
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class DeGiroServerConfig(ConfigSectionBase):
    """Config for degiro_server"""

    # pylint: disable=too-many-instance-attributes

    country: str = "Netherlands"
    lang: str = "nl"
    ga_ext: str = "/totp"
    login_url: str = "https://trader.degiro.nl/login/secure/login"
    client_url: str = "https://trader.degiro.nl/pa/secure/client"
    portfolio_url: str = (
        "https://trader.degiro.nl/portfolio-reports/secure/v3/positionReport/csv"
    )
    account_url: str = (
        "https://trader.degiro.nl/portfolio-reports/secure/v3/cashAccountReport/csv"
    )
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"


@dataclass(frozen=True)
class StockwatchConfig(ConfigBase):
    """Config for stockwatch"""

    degiro_server: DeGiroServerConfig = DeGiroServerConfig()

    @classmethod
    def default_filepath(cls) -> Path | None:
        """
        Return the fully qualified default path for the config/settingsfile: e.g. ~/.example/config.toml.
        If you prefer to not have a default path then overwrite this method and return None.
        """
        # this effectively implies that we are not using config files... so be it for now
        # new version of application_config should resolve this
        return None
