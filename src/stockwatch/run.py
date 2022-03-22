#!/usr/bin/env python3
"""
Simple main script to show the figures without an active dash application.

Functions:
    main(folder: Path) -> int
"""
from pathlib import Path

from . import use_cases, analysis, dashboard


def main(folder: Path) -> int:
    """The main function to run the stockwatcher."""

    share_portfolios = use_cases.process_portfolios(folder=folder, rename=False)
    print(
        "All consistent?",
        all(
            share_portfolio.is_date_consistent() for share_portfolio in share_portfolios
        ),
    )
    use_cases.process_transactions(
        share_portfolios=share_portfolios, folder=folder, rename=False
    )
    fig1 = analysis.plot_returns(share_portfolios)
    fig2 = analysis.plot_positions(share_portfolios)
    fig1.show()
    fig2.show()
    return 0


def dash(folder: Path) -> int:
    dashboard.run_blocking(folder)
    return 0
