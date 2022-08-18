"""Module for handling configuration."""
import sys
from abc import ABC
from dataclasses import dataclass, fields, field
from typing import Any, ClassVar

from stockwatch.config import get_stored_config


@dataclass(frozen=True)
class ConfigBase(ABC):
    """Base class for all Config classes"""


@dataclass(frozen=True)
class DeGiroServerConfig(ConfigBase):
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

    # pylint: disable=invalid-name

    _instance: ClassVar["Config"] = field(init=False, repr=False)
    DeGiroServer: DeGiroServerConfig

    @staticmethod
    def get_instance() -> "Config":
        """Static access method."""
        try:
            return Config._instance
        except AttributeError as _:
            stockwatch_config_stored = get_stored_config()
            _config_fields = {
                f
                for f in fields(Config)
                if f.init and f.name in stockwatch_config_stored.keys()
            }
            sections: dict[str, Any] = {}
            for f in _config_fields:
                section_name = f.name
                section = instantiate_config(
                    section_name, stockwatch_config_stored[section_name]
                )
                sections[section_name] = section

            Config(**sections)
            return Config._instance

    def __post_init__(self) -> None:
        """Virtually private constructor."""
        Config._instance = self


def instantiate_config(
    classname_to_instantiate: str, arg_dict: dict[str, Any]
) -> ConfigBase | None:
    """Return an instance of classname_to_instantiate, properly initialized"""
    if not (
        class_to_instantiate := getattr(
            sys.modules[__name__], f"{classname_to_instantiate}Config"
        )
    ):
        print(f"No Config class known for section named {classname_to_instantiate}")
        return None
    field_set = {f.name for f in fields(class_to_instantiate) if f.init}
    filtered_arg_dict = {k: v for k, v in arg_dict.items() if k in field_set}
    return class_to_instantiate(**filtered_arg_dict)  # type: ignore


def get_config() -> Config:
    """Return the config singleton"""
    return Config.get_instance()
