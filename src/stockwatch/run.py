#!/usr/bin/env python3
"""
Simple main script to show the figures without an active dash application.

Functions:
    main(folder: Path) -> int
"""
from pathlib import Path

from .use_cases import process_portfolios, process_transactions
from .analysis import plot_returns, plot_positions
from .dashboard import run_blocking


def main(folder: Path) -> int:
    """The main function to run the stockwatcher."""

    share_portfolios = process_portfolios(folder=folder, rename=False)
    print(
        "All consistent?",
        all(
            share_portfolio.is_date_consistent() for share_portfolio in share_portfolios
        ),
    )
    process_transactions(share_portfolios=share_portfolios, folder=folder, rename=False)
    fig1 = plot_returns(share_portfolios)
    fig2 = plot_positions(share_portfolios)
    fig1.show()
    fig2.show()
    return 0


def dash(folder: Path) -> int:
    run_blocking(folder)
    return 0
