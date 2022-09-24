"""Module for storing configuration."""
from pathlib import Path


def get_configfile_path() -> Path:
    """Return the path for the config directory"""
    # For now, we store the config file in the package
    return Path(__file__).parent
