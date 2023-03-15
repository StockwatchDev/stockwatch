"""Adapters for mapping entities and use cases to data formats required by frameworks that are used.

This package has a clean architecture. Hence, this module should only depend on the
entities and the use_cases module (apart from plain Python). It should specifically not
depend on external frameworks and also not contain any business- or application logic.
"""
from dataclasses import dataclass, field
from datetime import date

from .entities.shares import SharePortfolio
from .entities.transactions import IsinStr


@dataclass(frozen=True)
class ReturnsData:
    """A list of investments and returns at a number of dates."""

    dates: list[date] = field(default_factory=list)
    investments: list[float] = field(default_factory=list)
    totals: list[float] = field(default_factory=list)
    realized_returns: list[float] = field(default_factory=list)
    unrealized_returns: list[float] = field(default_factory=list)
    returns: list[float] = field(default_factory=list)

    @classmethod
    def from_portfolios(
        cls, share_portfolios: tuple[SharePortfolio, ...]
    ) -> "ReturnsData":
        """Create an instance that holds the data of share_portfolios"""
        sorted_portfolios = sorted(share_portfolios)
        the_dates: list[date] = []
        the_investments: list[float] = []
        the_totals: list[float] = []
        the_realized_returns: list[float] = []
        the_unrealized_returns: list[float] = []
        the_returns: list[float] = []
        for portfolio in sorted_portfolios:
            the_dates.append(portfolio.portfolio_date)
            the_investments.append(portfolio.investment.value)
            the_totals.append(portfolio.value.value)
            the_realized_returns.append(portfolio.realized.value)
            the_unrealized_returns.append(portfolio.unrealized.value)
            the_returns.append(portfolio.total_return.value)
        return cls(
            dates=the_dates,
            investments=the_investments,
            totals=the_totals,
            realized_returns=the_realized_returns,
            unrealized_returns=the_unrealized_returns,
            returns=the_returns,
        )


@dataclass(frozen=True)
class PositionsData:
    """A list of stock positions at a number of dates."""

    dates: list[date] = field(default_factory=list)
    isins_and_names: list[tuple[IsinStr, str]] = field(default_factory=list)
    isins_and_values: dict[IsinStr, list[float]] = field(default_factory=dict)

    @classmethod
    def from_portfolios(
        cls, share_portfolios: tuple[SharePortfolio, ...]
    ) -> "PositionsData":
        """Create an instance that holds the data of share_portfolios"""
        sorted_portfolios = sorted(share_portfolios)
        the_dates: list[date] = []
        the_isins_and_names: list[tuple[IsinStr, str]] = []
        the_isins_and_values: dict[IsinStr, list[float]] = {}
        # first collect all dates and all isins and their names
        all_isins_and_names = {}
        for portfolio in sorted_portfolios:
            the_dates.append(portfolio.portfolio_date)
            all_isins_and_names.update(portfolio.all_isins_and_names())
        # now make a list of isin-name tuples
        # sort the isins for increasing value at final date,
        # the result will be that all zero values are at the horizontal axis
        final_date_portfolio = share_portfolios[-1]
        the_isins_and_names.extend(
            sorted(
                all_isins_and_names.items(),
                key=lambda x: final_date_portfolio.get_position(x[0]).value.value,
            )
        )
        for isin, _ in the_isins_and_names:
            # vertical axis to be the value of each position in the portfolio
            values = [
                share_pf.get_position(isin).value.value
                for share_pf in sorted_portfolios
            ]
            the_isins_and_values[isin] = values
        return cls(
            dates=the_dates,
            isins_and_names=the_isins_and_names,
            isins_and_values=the_isins_and_values,
        )
