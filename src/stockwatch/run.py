#!/usr/bin/env python3
"""Simple main script to show the figures without an active dash application.

Functions:
    main(folder: Path) -> int
"""
from pathlib import Path

from .analysis import plot_positions, plot_returns
from .app.dashboard import run_blocking
from .entities import apply_transactions, get_all_isins
from .use_cases import process_portfolios, process_transactions


def main(folder: Path) -> int:
    """The main function to run the stockwatcher."""

    share_portfolios = process_portfolios(folder=folder)
    print(
        "All consistent?",
        all(
            share_portfolio.is_date_consistent() for share_portfolio in share_portfolios
        ),
    )
    transactions = process_transactions(
        isins=get_all_isins(share_portfolios), folder=folder
    )
    apply_transactions(transactions, share_portfolios)
    fig1 = plot_returns(share_portfolios)
    fig2 = plot_positions(share_portfolios)

    fig1.show()
    fig2.show()
    return 0


def dash(folder: Path) -> int:
    """Run the visualization using the Dash web interface."""
    run_blocking(folder)
    return 0
