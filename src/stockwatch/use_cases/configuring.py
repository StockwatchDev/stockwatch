"""Module for defining configuration."""
from dataclasses import dataclass
from pathlib import Path

from stockwatch.config import get_configfile_path
from stockwatch.use_cases.configuring_base import ConfigBase, ConfigSectionBase


@dataclass(frozen=True)
class DeGiroServerConfig(ConfigSectionBase):
    """Config for degiro_server"""

    # pylint: disable=too-many-instance-attributes

    country: str
    lang: str
    ga_ext: str
    login_url: str
    client_url: str
    portfolio_url: str
    account_url: str
    user_agent: str


@dataclass(frozen=True)
class Config(ConfigBase):
    """Config sections for stockwatch"""

    degiro_server: DeGiroServerConfig

    @staticmethod
    def get_configfile_path() -> Path:
        """Return the fully qualified path for the configfile"""
        return get_configfile_path() / "stockwatch.toml"
