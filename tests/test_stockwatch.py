# pylint: disable=C0114
# pylint: disable=C0116
from stockwatch import __version__


def test_version() -> None:
    assert __version__ == "0.1.0"
