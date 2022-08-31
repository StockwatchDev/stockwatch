"""Module for handling configuration."""
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import Any, TypeVar

import tomli as tomllib  # import tomllib in Python 3.11


TConfig = TypeVar("TConfig", bound="ConfigBase")


_ALL_CONFIGS: dict[str, Any] = {}


@dataclass(frozen=True)
class ConfigSectionBase(ABC):
    """Base class for all ConfigSection classes"""


# The next line has a type: ignore because MyPy has a problem with @abstractmethod
# If you comment the line with @abstractmethod, you can do type checking
@dataclass(frozen=True)  # type: ignore
class ConfigBase(ABC):
    """Base class for main Config class"""

    @staticmethod
    @abstractmethod
    def get_configfile_path() -> Path:
        """Return the fully qualified path for the configfile"""

    @classmethod
    def get_instance(cls: type[TConfig]) -> TConfig:
        """Access method for the singleton."""
        _the_config_or_none = _ALL_CONFIGS.get(cls.__name__)
        if _the_config_or_none is None:
            stockwatch_config_stored = cls._get_stored_config()
            _config_fields = {
                fld
                for fld in fields(cls)
                if fld.init and fld.name in stockwatch_config_stored.keys()
            }
            sections: dict[str, Any] = {}
            for fld in _config_fields:
                section_name = fld.name
                section = cls._instantiate_section_config(
                    section_name, stockwatch_config_stored[section_name]
                )
                sections[section_name] = section

            _the_config = cls(**sections)
            _ALL_CONFIGS[cls.__name__] = _the_config
            print(f"Created: {_the_config}")
        else:
            _the_config = _the_config_or_none
        return _the_config

    @classmethod
    def _get_stored_config(cls) -> dict[str, Any]:
        """Get the config stored in the toml file"""
        config_stored: dict[str, Any] = {}
        path = cls.get_configfile_path()
        try:
            with path.open(mode="rb") as fptr:
                config_stored = tomllib.load(fptr)
        except FileNotFoundError:
            print(f"Error: configfile {path} not found.")
        return config_stored

    @classmethod
    def _instantiate_section_config(
        cls: type[TConfig], section_to_instantiate: str, arg_dict: dict[str, Any]
    ) -> ConfigSectionBase | None:
        """Return an instance of classname_to_instantiate, properly initialized"""
        section_dict = {f.name: f.type for f in fields(cls) if f.init}
        if not (class_to_instantiate := section_dict.get(section_to_instantiate)):
            print(f"No Config class known for section named '{section_to_instantiate}'")
            return None
        field_set = {f.name for f in fields(class_to_instantiate) if f.init}
        filtered_arg_dict = {k: v for k, v in arg_dict.items() if k in field_set}
        return class_to_instantiate(**filtered_arg_dict)  # type: ignore
