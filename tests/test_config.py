# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import pytest
from stockwatch.use_cases.configuring import Config
from stockwatch.config import get_configfile_path as config_get_configfile_path


@pytest.fixture
def test_config() -> Config:
    # here do monkeypatching of get_configfile_path and _get_stored_config
    return Config.get()


def test_get_config_path(test_config) -> None:
    assert test_config.get_configfile_path().parts[-1] == "stockwatch.toml"
