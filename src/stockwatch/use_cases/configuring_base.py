"""Module for handling configuration."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, TypeVar

import tomli as tomllib  # import tomllib in Python 3.11

TConfig = TypeVar("TConfig", bound="ConfigBase")  # pylint: disable=invalid-name
TConfigSection = TypeVar(  # pylint: disable=invalid-name
    "TConfigSection", bound="ConfigSectionBase"
)


_ALL_CONFIGS: dict[int, Any] = {}


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
    def get(cls: type[TConfig]) -> TConfig:
        """Access method for the singleton."""

        if (_the_config_or_none := _ALL_CONFIGS.get(id(cls))) is None:
            # no config has been made yet, so let's instantiate one
            # and keep it in the global store
            _the_config = cls._create_instance()
            _ALL_CONFIGS[id(cls)] = _the_config
        else:
            _the_config = _the_config_or_none
        return _the_config

    @classmethod
    def _create_instance(cls: type[TConfig]) -> TConfig:
        """Instantiate the Config."""

        # get whatever is stored in the config file
        config_stored = cls._get_stored_config()
        # filter out fields that are both stored and an attribute of the Config
        _config_fields = {
            fld for fld in fields(cls) if fld.init and fld.name in config_stored.keys()
        }
        # instantiate the sections and keep them in a dict
        # actually sections: dict[str, TConfigSection]
        # but MyPy doesn't swallow that
        sections: dict[str, Any] = {
            fld.name: cls._instantiate_section_config(fld.name, config_stored[fld.name])
            for fld in _config_fields
        }

        # instantiate the Config with the sections
        return cls(**sections)

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
    ) -> TConfigSection:
        """Return an instance of section_to_instantiate, properly initialized"""
        # pre-condition: section_to_instantiate is an initializable field of cls
        # hence, we are sure that list comprehension below returns a list of length 1
        classes_to_instantiate = [
            f.type for f in fields(cls) if f.init and f.name == section_to_instantiate
        ]
        assert len(classes_to_instantiate) == 1
        field_set = {f.name for f in fields(classes_to_instantiate[0]) if f.init}
        filtered_arg_dict = {k: v for k, v in arg_dict.items() if k in field_set}
        return classes_to_instantiate[0](**filtered_arg_dict)  # type: ignore
