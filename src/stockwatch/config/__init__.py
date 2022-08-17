"""Module for handling configuration."""
import pathlib

import tomli as tomllib  # import tomllib in Python 3.11

path = pathlib.Path(__file__).parent / "stockwatch.toml"
with path.open(mode="rb") as fp:
    stockwatch_config = tomllib.load(fp)
