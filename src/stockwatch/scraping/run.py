#!/usr/bin/env python3
""" Main scraping functionality."""
import argparse
import os
from datetime import date, timedelta
from pathlib import Path

import requests

STOCKWATCH_ENV_VAR = "STOCKWATCH_PATH"


def obtain_portfolio(account: int, session_id: str, end_date: date) -> str:
    """
    Obtain the portfolio of the account at a certain date.

    A succesfull login has to be done previously, which should give a session_id
    which can be used to obtain data safely.
    """
    url = "https://trader.degiro.nl/reporting/secure/v3/positionReport/csv"
    args = {
        "sessionId": session_id,
        "country": "NL",
        "lang": "nl",
        "intAccount": account,
        "toDate": end_date.strftime("%d/%m/%Y"),
    }

    res = requests.get(url, params=args)

    if res.ok:
        return str(res.text)

    raise RuntimeError(f"Got an unexpected response: {res.reason}")


def loop_dates(
    account: int, session_id: str, start_date: date, end_date: date, portfolio_dir: Path
) -> None:
    """
    Loop over the days between start_date and end_date, and obtain the portfolio.

    All the files are placed in the porfolio_dir/portfolio directory with the
    yymmdd_porfolio.csv filename.
    """

    while start_date < end_date:
        if start_date.weekday() == 5 or start_date.weekday() == 6:
            # Let's skip the weekend days.
            start_date += timedelta(days=1)
            continue

        file_name = start_date.strftime("%y%m%d") + "_portfolio.csv"
        file_path = portfolio_dir.joinpath(file_name)

        if file_path.is_file():
            print(
                f"Skipping portfolio date {start_date} "
                f"as the file {file_path} already exists"
            )

        print(f"Obtaining portfolio for date: {start_date}")
        data = obtain_portfolio(account, session_id, start_date)
        with open(file_path, "w+") as f:
            f.write(data)

        start_date += timedelta(days=1)


def _get_stockwatch_dir(suggested_dir: Path | None) -> Path:
    if not suggested_dir or not suggested_dir.is_dir():
        # Let's try to read from the environment variables.
        env_path = os.environ.get(STOCKWATCH_ENV_VAR, "")
        if env_path:
            suggested_dir = Path(env_path)

    if suggested_dir is None or not suggested_dir.is_dir():
        raise ValueError("No STOCKWATCH_DIR found")

    return suggested_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "account",
        type=int,
        help="The account identifier",
    )
    parser.add_argument(
        "session_id",
        type=str,
        help="A valid session ID",
    )
    parser.add_argument(
        "-s",
        "--start-date",
        type=date.fromisoformat,
        default=date(2020, 1, 1),
        help="The start date from which to obtain the portfolio in ISO style (YYYY-MM-DD)",
    )
    parser.add_argument(
        "-e",
        "--end-date",
        type=date.fromisoformat,
        default=date.today(),
        help="The end date from which to obtain the portfolio in ISO style (YYYY-MM-DD)",
    )
    parser.add_argument(
        "dir",
        nargs="?",
        default=None,
        type=Path,
        help="Directory where the portfolio files are installed, if not defined the "
        f"environment variable '{STOCKWATCH_ENV_VAR}' is used",
    )

    args = parser.parse_args()

    stockwatch_dir = _get_stockwatch_dir(args.dir)
    portfolio_dir = stockwatch_dir.joinpath("portfolio")
    os.makedirs(portfolio_dir, exist_ok=True)

    loop_dates(
        args.account, args.session_id, args.start_date, args.end_date, portfolio_dir
    )
