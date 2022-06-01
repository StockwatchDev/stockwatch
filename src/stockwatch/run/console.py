"""Run module for starting the stockwatch application in the console."""

from pathlib import Path

from stockwatch import use_cases, analysis, entities


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
        isins=entities.get_all_isins(share_portfolios), folder=folder
    )
    entities.apply_transactions(transactions, share_portfolios)
    fig1 = analysis.plot_returns(share_portfolios)
    fig2 = analysis.plot_positions(share_portfolios)

    fig1.show()
    fig2.show()
    return 0
