#!/usr/bin/env python3
"""
Read csv files with stock portfolio data from De Giro and visualize in the browser.

Classes:

    SharePosition
    SharePortfolio

Functions:

    create_share_portfolios(folder: Path,
                            rename: bool = True) -> tuple[SharePortfolio, ...]
    analyse_trend(share_portfolios: tuple[SharePortfolio], totals: bool = False) -> None
    main(folder: Path) -> int
"""
import argparse
import os
import sys
from pathlib import Path
from typing import Optional

import dashboard
from analysis import analyse_trend, create_share_portfolios, process_transactions

STOCKWATCH_ENV_VAR = "STOCKWATCH_PATH"


def main(folder: Path) -> int:
    """The main function to run the stockwatcher."""

    share_portfolios = create_share_portfolios(folder=folder, rename=False)
    print(
        "All consistent?",
        all(
            share_portfolio.is_date_consistent() for share_portfolio in share_portfolios
        ),
    )
    process_transactions(share_portfolios=share_portfolios, folder=folder, rename=False)
    fig1 = analyse_trend(share_portfolios, totals=True)
    fig2 = analyse_trend(share_portfolios)
    fig1.show()
    fig2.show()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dir",
        nargs="?",
        default=None,
        type=Path,
        help="Directory where the portfolio files are installed",
    )
    parser.add_argument(
        "-d",
        "--dash",
        default=False,
        action="store_true",
        help="Run with the new dash app, instead of plotly figures",
    )

    args = parser.parse_args()
    folder: Optional[Path] = args.dir

    if not folder or not folder.is_dir():
        # Let's try to read from the environment variables.
        env_path = os.environ.get(STOCKWATCH_ENV_VAR, "")
        if env_path:
            folder = Path(env_path)

    if not folder or not folder.is_dir():
        parser.error(
            f"Folder: '{folder}' does not exist, please pass as commandline argument, or define the"
            f" '{STOCKWATCH_ENV_VAR}' environment variable."
        )

    print(f"Parsing the porfolio files in directory: '{folder}'")
    if args.dash:
        dashboard.run_blocking(folder)
    else:
        sys.exit(main(folder))
