"""Module for handling configuration."""
import pathlib
from dataclasses import fields
from typing import Any

import tomli as tomllib  # import tomllib in Python 3.11

from stockwatch.config.config import *

path = pathlib.Path(__file__).parent / "stockwatch.toml"
with path.open(mode="rb") as fp:
    stockwatch_config_stored = tomllib.load(fp)

sections: dict[str, Any] = {}
_config_fields = {
    f for f in fields(Config) if f.init and f.name in stockwatch_config_stored.keys()
}
for f in _config_fields:
    section_name = f.name
    section = DataClassUnpack.instantiate(
        section_name, stockwatch_config_stored[section_name]
    )
    sections[section_name] = section

stockwatch_config = Config(**sections)

print(stockwatch_config)
