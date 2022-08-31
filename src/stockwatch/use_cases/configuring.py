"""Module for defining configuration."""
from dataclasses import dataclass
from pathlib import Path

from stockwatch.use_cases.configuring_base import ConfigBase, ConfigSectionBase
from stockwatch.config import get_configfile_path


@dataclass(frozen=True)
class DeGiroServerConfig(ConfigSectionBase):
    """Config for degiro_server"""

    country: str
    lang: str
    ga_ext: str
    login_url: str
    clientnr_url: str
    portfolio_url: str
    account_url: str


@dataclass(frozen=True)
class Config(ConfigBase):
    """Config sections for stockwatch"""

    degiro_server: DeGiroServerConfig

    @staticmethod
    def get_configfile_path() -> Path:
        """Return the fully qualified path for the configfile"""
        return get_configfile_path() / "stockwatch.toml"


def get_config() -> Config:
    """Return the config singleton"""
    return Config.get_instance()


print(get_config().degiro_server.clientnr_url)
