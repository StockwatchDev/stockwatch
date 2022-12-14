# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
from stockwatch import __version__


def test_version() -> None:
    assert __version__ == "0.1.0"
