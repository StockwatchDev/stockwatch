"""Module for defining configuration."""
from dataclasses import dataclass

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
    def get_app_basename() -> str:
        """Return the string that describes the application base name"""
        return "stockwatch"
