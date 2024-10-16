"""Use cases related to the STOCKDIR folder."""

import argparse
import copy
import os
from datetime import date, datetime
from pathlib import Path

_STOCKWATCH_ENV_VAR = "STOCKWATCH_PATH"
_FILE_DATE_FORMAT = "%y%m%d"

_STOCKDIR_PATH = Path(".")


def add_stockdir_argument(parser: argparse.ArgumentParser) -> None:
    """Add the stockdir argument to the commandline parser."""
    parser.add_argument(
        "dir",
        nargs="?",
        default=None,
        type=Path,
        help="Directory where the portfolio files are installed, if not defined the "
        f"environment variable '{_STOCKWATCH_ENV_VAR}' is used",
    )


def set_stockdir(cmdline: Path | None) -> None:
    """Get the stockdir given a (optional) commandline argument."""
    global _STOCKDIR_PATH  # pylint: disable=global-statement

    if cmdline:
        _STOCKDIR_PATH = cmdline
    else:
        # Let's try to get the environment variable
        if not (folder_str := os.environ.get(_STOCKWATCH_ENV_VAR, None)):
            raise RuntimeError(
                f"Please define the {_STOCKWATCH_ENV_VAR} environment variable to specify "
                f"where the stockdata can be saved."
            )
        _STOCKDIR_PATH = Path(folder_str)


def get_stockdir() -> Path:
    """Get the configured stockdir."""
    return copy.copy(_STOCKDIR_PATH)


def get_first_date(folder: Path) -> date | None:
    """Get the first date of the csv files in the folder

    This assumes that all the csv files have the filename
    format yymmdd_FILENAME.csv (e.g. 210115_example.csv
    for a file from 15-Jan-2021)
    """
    if files := sorted(folder.glob("*.csv")):
        return datetime.strptime(files[0].name[:6], _FILE_DATE_FORMAT).date()
    return None


def check_portfolio_exists(portfolio_date: date) -> bool:
    """Check if a portfolio at the specified data already exists."""
    return _get_portfolio_file(portfolio_date).exists()


def portfolio_to_file(data: str, portfolio_date: date) -> None:
    """Write the portfolio data of a certain date to file."""
    filepath = _get_portfolio_file(portfolio_date)

    filepath.parent.mkdir(exist_ok=True, parents=True)
    with open(filepath, "w+", encoding="UTF-8") as portfolio_file:
        portfolio_file.write(data)


def account_report_to_file(data: str) -> None:
    """Write the account report to file."""
    filepath = get_account_report_file()

    filepath.parent.mkdir(exist_ok=True, parents=True)
    with open(filepath, "w+", encoding="UTF-8") as report_file:
        report_file.write(data)


def get_indices_folder() -> Path:
    """Get the indices folder."""
    return _STOCKDIR_PATH / "indices"


def get_portfolio_folder() -> Path:
    """Get the portfolio folder."""
    return _STOCKDIR_PATH / "portfolio"


def _get_portfolio_file(portfolio_date: date) -> Path:
    filename = portfolio_date.strftime("%y%m%d") + "_portfolio.csv"
    return get_portfolio_folder() / filename


def get_account_report_file() -> Path:
    """Get the account report file path."""
    return _STOCKDIR_PATH / "account" / "report.csv"
