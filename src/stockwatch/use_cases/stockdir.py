"""Use cases related to the STOCKDIR folder."""
import argparse
import os
from datetime import date, datetime
from pathlib import Path

_STOCKWATCH_ENV_VAR = "STOCKWATCH_PATH"
_FILE_DATE_FORMAT = "%y%m%d"


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


def get_stockdir(cmdline: Path | None) -> Path:
    """Get the stockdir given a (optional) commandline argument."""
    stockdir = cmdline
    if not (stockdir := cmdline):
        # Let's try to get the environment variable
        if not (folder_str := os.environ.get(_STOCKWATCH_ENV_VAR, None)):
            raise RuntimeError(
                f"Please define the {_STOCKWATCH_ENV_VAR} environment variable to specify "
                f"where the stockdata can be saved."
            )
        stockdir = Path(folder_str)

    stockdir.mkdir(exist_ok=True)
    return stockdir


def get_last_date(folder: Path) -> date:
    """Get the last date of the csv files in the folder

    This assumes that all the csv files have the filename
    format yymmdd_FILENAME.csv (e.g. 210115_example.csv
    for a file from 15-Jan-2021)
    """
    files = sorted(folder.glob("*.csv"))
    return datetime.strptime(files[-1].name[:6], _FILE_DATE_FORMAT).date()


def check_portfolio_exists(folder: Path, portfolio_date: date) -> bool:
    """Check if a portfolio at the specified data already exists."""
    return _get_portfolio_file(folder, portfolio_date).exists()


def portfolio_to_file(folder: Path, data: str, portfolio_date: date) -> None:
    """Write the portfolio data of a certain date to file."""
    filepath = _get_portfolio_file(folder, portfolio_date)
    with open(filepath, "w+", encoding="UTF-8") as portfolio_file:
        portfolio_file.write(data)


def _get_portfolio_file(folder: Path, portfolio_date: date) -> Path:
    filename = portfolio_date.strftime("%y%m%d") + "_portfolio.csv"
    return folder / "portfolio" / filename
