from datetime import date
from .entities import *


def returns_plotdata(
    share_portfolios: tuple[SharePortfolio, ...]
) -> tuple[list[date], list[float], list[float], list[float]]:
    # make sure the portfolios are sorted by date:
    sorted_portfolios = sorted(share_portfolios, key=lambda x: x.portfolio_date)

    # horizontal axis to be the date
    dates = [share_pf.portfolio_date for share_pf in sorted_portfolios]

    investments = []
    returns = []
    totals = []
    for share_pf in sorted_portfolios:
        investments.append(share_pf.total_investment)
        totals.append(share_pf.total_value)
        returns.append(share_pf.total_value - share_pf.total_investment)

    return dates, investments, totals, returns


def positions_plotdata(
    share_portfolios: tuple[SharePortfolio, ...]
) -> tuple[list[date], list[tuple[str, str]], dict[str, list[float]]]:

    # make sure the portfolios are sorted by date:
    sorted_portfolios = sorted(share_portfolios, key=lambda x: x.portfolio_date)
    # horizontal axis to be the date
    dates = [share_pf.portfolio_date for share_pf in sorted_portfolios]

    sorted_isins_and_names_list = []
    # first collect all position names / isins
    all_isins_and_names = {}
    for share_portfolio in share_portfolios:
        all_isins_and_names.update(share_portfolio.all_isins_and_names())
    # sort for increasing value at final date,
    # such that all zero values are at the horizontal axis
    sorted_isins_and_names_list = sorted(
        all_isins_and_names.items(),
        key=lambda x: share_portfolios[-1].value_of(x[0]),
    )

    values_dict = {}
    for (isin, _) in sorted_isins_and_names_list:
        # vertical axis to be the value of each position in the portfolio
        values = [share_pf.value_of(isin) for share_pf in sorted_portfolios]
        values_dict[isin] = values
    return dates, sorted_isins_and_names_list, values_dict
