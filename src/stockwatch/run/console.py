"""Run module for starting the stockwatch application in the console."""

from pathlib import Path

from .. import use_cases
from ..analysis import plot_positions, plot_returns
from ..entities import apply_transactions, get_all_isins


def run(folder: Path) -> int:
    """The main function to run the stockwatcher."""

    share_portfolios = use_cases.process_portfolios(folder=folder)
    print(
        "All consistent?",
        all(
            share_portfolio.is_date_consistent() for share_portfolio in share_portfolios
        ),
    )
    transactions = use_cases.process_transactions(
        isins=get_all_isins(share_portfolios), folder=folder
    )
    apply_transactions(transactions, share_portfolios)
    fig1 = plot_returns(share_portfolios)
    fig2 = plot_positions(share_portfolios)

    fig1.show()
    fig2.show()
    return 0
