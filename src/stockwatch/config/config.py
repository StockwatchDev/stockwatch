"""Module for handling configuration."""
import sys
from abc import ABC
from dataclasses import dataclass, fields
from typing import Any


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

    DeGiroServer: DeGiroServerConfig  # pylint: disable=invalid-name


class DataClassUnpack:  # pylint: disable=too-few-public-methods
    """Helper class: initialize dataclasses from dicts that are filtered for known fields"""

    @classmethod
    def instantiate(
        cls, section_name: str, arg_dict: dict[str, Any]
    ) -> ConfigBase | None:
        """Return an instance of section with section_name, properly initialized"""
        if not (
            class_to_instantiate := getattr(
                sys.modules[__name__], f"{section_name}Config"
            )
        ):
            print(f"No Config class known for section named {section_name}")
            return None
        field_set = {f.name for f in fields(class_to_instantiate) if f.init}
        filtered_arg_dict = {k: v for k, v in arg_dict.items() if k in field_set}
        return class_to_instantiate(**filtered_arg_dict)  # type: ignore
