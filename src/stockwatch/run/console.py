"""Run module for starting the stockwatch application in the console."""
from stockwatch import analysis, use_cases


def run() -> int:
    """The main function to run the stockwatcher."""
    share_portfolios, _ = use_cases.get_portfolios_index_positions()
    print(
        "All consistent?",
        all(
            share_portfolio.is_date_consistent() for share_portfolio in share_portfolios
        ),
    )

    fig1 = analysis.plot_returns(share_portfolios)
    fig2 = analysis.plot_positions(share_portfolios)

    fig1.show()
    fig2.show()
    return 0
