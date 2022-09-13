"""Adapters for mapping entities and use cases to data formats required by frameworks that are used.

This package has a clean architecture. Hence, this module should only depend on the
entities and the use_cases module (apart from plain Python). It should specifically not
depend on external frameworks and also not contain any business- or application logic.
"""
from dataclasses import dataclass, field
from datetime import date

from .entities import IsinStr, SharePortfolio


@dataclass(frozen=True)
class ReturnsData:
    """A list of investments and returns at a number of dates."""

    dates: list[date] = field(default_factory=list)
    investments: list[float] = field(default_factory=list)
    totals: list[float] = field(default_factory=list)
    realized_returns: list[float] = field(default_factory=list)
    unrealized_returns: list[float] = field(default_factory=list)
    returns: list[float] = field(default_factory=list)


@dataclass(frozen=True)
class PositionsData:
    """A list of stock positions at a number of dates."""

    dates: list[date] = field(default_factory=list)
    isins_and_names: list[tuple[IsinStr, str]] = field(default_factory=list)
    isins_and_values: dict[IsinStr, list[float]] = field(default_factory=dict)


def returns_plotdata(share_portfolios: tuple[SharePortfolio, ...]) -> ReturnsData:
    """Get the ReturnsData of a list of portfolios."""
    # make sure the portfolios are sorted by date:
    sorted_portfolios = sorted(share_portfolios)

    returns_data = ReturnsData()
    # horizontal axis to be the date
    returns_data.dates.extend(
        [share_pf.portfolio_date for share_pf in sorted_portfolios]
    )

    returns_data.investments.extend(
        [share_pf.total_investment for share_pf in sorted_portfolios]
    )
    returns_data.totals.extend([share_pf.total_value for share_pf in sorted_portfolios])
    returns_data.realized_returns.extend(
        [share_pf.total_realized_return for share_pf in sorted_portfolios]
    )
    returns_data.unrealized_returns.extend(
        [share_pf.total_unrealized_return for share_pf in sorted_portfolios]
    )
    returns_data.returns.extend(
        [share_pf.total_return for share_pf in sorted_portfolios]
    )

    return returns_data


def positions_plotdata(share_portfolios: tuple[SharePortfolio, ...]) -> PositionsData:
    """Get the PositionsData of a list of portfolios."""

    positions_data = PositionsData()
    # make sure the portfolios are sorted by date:
    sorted_portfolios = sorted(share_portfolios)
    # horizontal axis to be the date
    positions_data.dates.extend(
        [share_pf.portfolio_date for share_pf in sorted_portfolios]
    )

    # first collect all position names / isins
    all_isins_and_names = {}
    for share_portfolio in share_portfolios:
        all_isins_and_names.update(share_portfolio.all_isins_and_names())
    # sort for increasing value at final date,
    # such that all zero values are at the horizontal axis
    positions_data.isins_and_names.extend(
        sorted(
            all_isins_and_names.items(),
            key=lambda x: share_portfolios[-1].get_position(x[0]).value,
        )
    )

    for (isin, _) in positions_data.isins_and_names:
        # vertical axis to be the value of each position in the portfolio
        values = [share_pf.get_position(isin).value for share_pf in sorted_portfolios]
        positions_data.isins_and_values[isin] = values
    return positions_data
