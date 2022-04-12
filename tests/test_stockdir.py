# type: ignore[no-untyped-def]
"""Test the stockdir use cases."""

from datetime import date
from pathlib import Path

import pytest

from stockwatch.use_cases import stockdir


def test_get_stockdir(monkeypatch) -> None:
    """Test getting the stockdir."""
    cmd_dir = Path("example/path/from/cmdline")
    env_dir = "example/path/in/env"

    # If we give no input, and no environment variable
    # we get nothing back.
    with pytest.raises(RuntimeError):
        new_dir = stockdir.get_stockdir(None)

    # We can set an environment variable
    monkeypatch.setenv("STOCKWATCH_PATH", env_dir)
    new_dir = stockdir.get_stockdir(None)
    assert new_dir == Path(env_dir)

    # We can also give it as an input variable.
    new_dir = stockdir.get_stockdir(cmd_dir)
    assert new_dir == cmd_dir


def test_get_last_date(monkeypatch) -> None:
    """Test getting the last date."""
    dates = [
        date(2000, 2, 1),
        date(2010, 1, 1),
        date(2000, 10, 10),
        date(2009, 12, 30),
    ]
    max_date = max(i for i in dates)

    monkeypatch.setattr(
        Path,
        "glob",
        lambda _, __: [Path(d.strftime("%y%m%d") + "_test.csv") for d in dates],
    )

    test = Path("some/path/whatever")
    assert stockdir.get_last_date(test) == max_date
