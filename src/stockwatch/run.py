#!/usr/bin/env python3
"""
Simple main script to show the figures without an active dash application.

Functions:
    main(folder: Path) -> int
"""
from pathlib import Path

from . import analysis, dashboard


def main(folder: Path) -> int:
    """The main function to run the stockwatcher."""

    share_portfolios = analysis.create_share_portfolios(folder=folder, rename=False)
    print(
        "All consistent?",
        all(
            share_portfolio.is_date_consistent() for share_portfolio in share_portfolios
        ),
    )
    analysis.process_transactions(
        share_portfolios=share_portfolios, folder=folder, rename=False
    )
    fig1 = analysis.analyse_trend(share_portfolios, totals=True)
    fig2 = analysis.analyse_trend(share_portfolios)
    fig1.show()
    fig2.show()
    return 0


def dash(folder: Path) -> int:
    dashboard.run_blocking(folder)
    return 0
