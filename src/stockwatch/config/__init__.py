"""Module for handling configuration."""
import pathlib
from typing import Any

import tomli as tomllib  # import tomllib in Python 3.11


def get_stored_config() -> dict[str, Any]:
    """Get the config stored in the toml file"""
    # For now, we store the config file in the package
    path = pathlib.Path(__file__).parent / "stockwatch.toml"
    with path.open(mode="rb") as fptr:
        stockwatch_config_stored = tomllib.load(fptr)
    print(f"{stockwatch_config_stored=}")
    return stockwatch_config_stored
