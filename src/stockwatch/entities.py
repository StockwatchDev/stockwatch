"""This module contains the business logic for holding a stock portfolio.

This package has a clean architecture. Hence, this module should not depend on any
other module and only import Python stuff.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date
from enum import IntEnum, auto
from typing import NewType

IsinStr = NewType("IsinStr", str)


UNKNOWN_POSITION_NAME = "Name Unknown"


class ShareTransactionKind(IntEnum):
    """Enum with the type of possible transactions."""

    BUY = auto()
    SELL = auto()
    DIVIDEND = auto()


@dataclass(frozen=True, order=True)
class ShareTransaction:
    """For representing a stock shares transaction at a certain date.

    Attributes
    ----------
    kind              : the kind of transaction
    isin              : the ISIN code / Symbol string used to identify a share
    curr              : the currency shorthand in which the transaction is done, e.g. EUR
    nr_stocks         : the number of items in the transaction
    price             : the price per item, in curr
    transaction_date  : the date for which the value of the share position is registered
    """

    transaction_date: date
    kind: ShareTransactionKind
    isin: IsinStr
    curr: str
    nr_stocks: float
    price: float


@dataclass(frozen=True, order=True)
class SharePosition:  # pylint: disable=too-many-instance-attributes
    """For representing a stock shares position at a certain date.

    Attributes
    ----------
    position_date   : the date for which the value of the share position is registered
    value           : the current value of the shares, in EUR
    name            : the name of the share
    isin            : the ISIN code / Symbol string used to identify a share
    curr            : the currency shorthand in which the stock is traded, e.g. EUR
    investment      : the amount in EUR spent in purchasing the shares
    nr_stocks       : the number of shares
    price           : the current price of the shares, in curr
    realized        : the realized result in EUR (including trading costs)
    """

    position_date: date
    value: float
    isin: IsinStr
    name: str
    curr: str
    investment: float
    nr_stocks: float
    price: float
    realized: float
    unrealized: float = field(init=False)
    total_return: float = field(init=False)

    @classmethod
    def empty_position(
        cls,
        position_date: date,
        isin: IsinStr,
        name: str = UNKNOWN_POSITION_NAME,
        realized: float = 0.0,
    ) -> SharePosition:
        """Return an empty position dated the_date with isin the_isin"""
        return SharePosition(
            position_date=position_date,
            value=0.0,
            isin=isin,
            name=name,
            curr="EUR",
            investment=0.0,
            nr_stocks=0.0,
            price=1.0,
            realized=realized,
        )

    def __post_init__(self) -> None:
        # because frozen=True, we need to use __setattr__ here:
        object.__setattr__(self, "unrealized", round(self.value - self.investment, 2))
        object.__setattr__(self, "total_return", self.realized + self.unrealized)


PortfoliosDictionary = dict[date, dict[IsinStr, SharePosition]]


@dataclass(frozen=True, order=True)
class SharePortfolio:
    """For representing a stock shares portfolio (i.e. multiple positions) at a certain date.

    Attributes
    ----------
    share_positions         : the collection of share positions; key is the share isin
    portfolio_date          : the date of the registered share positions
    """

    portfolio_date: date
    total_value: float = field(init=False)
    share_positions: tuple[SharePosition, ...]
    total_investment: float = field(init=False)
    total_unrealized_return: float = field(init=False)
    total_realized_return: float = field(init=False)
    total_return: float = field(init=False)

    def __post_init__(self) -> None:
        # because frozen=True, we need to use __setattr__ here:
        object.__setattr__(
            self,
            "total_value",
            round(sum(share_pos.value for share_pos in self.share_positions), 2),
        )
        object.__setattr__(
            self,
            "total_investment",
            round(
                sum(share_pos.investment for share_pos in self.share_positions),
                2,
            ),
        )
        object.__setattr__(
            self,
            "total_unrealized_return",
            round(
                sum(share_pos.unrealized for share_pos in self.share_positions),
                2,
            ),
        )
        object.__setattr__(
            self,
            "total_realized_return",
            round(
                sum(share_pos.realized for share_pos in self.share_positions),
                2,
            ),
        )
        object.__setattr__(
            self,
            "total_return",
            round(
                sum(share_pos.total_return for share_pos in self.share_positions),
                2,
            ),
        )
        assert self.is_date_consistent()

    def contains(self, an_isin: IsinStr) -> bool:
        """Return True if self has a share position with ISIN an_isin."""
        return an_isin in self.all_isins()

    def get_position(self, the_isin: IsinStr) -> SharePosition:
        """Return the share position with ISIN the_isin or an empty one with just the isin if not present."""
        if selected_positions := [
            the_pos for the_pos in self.share_positions if the_pos.isin == the_isin
        ]:
            return selected_positions[0]
        return SharePosition.empty_position(self.portfolio_date, the_isin)

    def all_isins(self) -> tuple[IsinStr, ...]:
        """Return the ISIN codes of the share positions."""
        return tuple(share_pos.isin for share_pos in self.share_positions)

    def all_isins_and_names(self) -> dict[IsinStr, str]:
        """Return the ISIN codes and names of the share positions."""
        return {share_pos.isin: share_pos.name for share_pos in self.share_positions}

    def is_date_consistent(self) -> bool:
        """Return True if the share positions dates all match self.portfolio_date."""
        return all(
            share_pos.position_date == self.portfolio_date
            for share_pos in self.share_positions
        )


def portfolios_dictionary_2_portfolios(
    spf_dict: PortfoliosDictionary,
) -> tuple[SharePortfolio, ...]:
    """Return a tuple of SharePortfolios that represent spf_dict"""
    spf_list = [
        SharePortfolio(spf_date, tuple(sorted(spf_dict.values())))
        for spf_date, spf_dict in spf_dict.items()
    ]
    return tuple(sorted(spf_list))


def earliest_portfolio_date(share_portfolios: tuple[SharePortfolio, ...]) -> date:
    """Return the earliest date found in share_portfolios."""
    return min(spf.portfolio_date for spf in share_portfolios)


def latest_portfolio_date(share_portfolios: tuple[SharePortfolio, ...]) -> date:
    """Return the latest date found in share_portfolios."""
    return max(spf.portfolio_date for spf in share_portfolios)


def closest_portfolio_after_date(
    share_portfolios: tuple[SharePortfolio, ...], start_date: date
) -> SharePortfolio | None:
    """Return the share portfolio on or closest after date or None if no portfolio matches that."""
    portfolios_after_date = [
        spf for spf in share_portfolios if spf.portfolio_date >= start_date
    ]
    if len(portfolios_after_date) > 0:
        sorted_portfolios = sorted(portfolios_after_date)
        return sorted_portfolios[0]
    return None


def closest_portfolio_before_date(
    share_portfolios: tuple[SharePortfolio, ...], end_date: date
) -> SharePortfolio | None:
    """Return the share portfolio closest before date or None if no portfolio matches that."""
    portfolios_before_date = [
        spf for spf in share_portfolios if spf.portfolio_date < end_date
    ]
    if len(portfolios_before_date) > 0:
        sorted_portfolios = sorted(portfolios_before_date)
        return sorted_portfolios[-1]
    return None


def apply_transactions(
    transactions: tuple[ShareTransaction, ...],
    portfolios: dict[date, dict[IsinStr, SharePosition]],
) -> dict[date, dict[IsinStr, SharePosition]]:
    """Process transactions to add the investment and realization of the portfolios."""
    if len(transactions) == 0:
        return portfolios
    sorted_portfolios = sorted(list(portfolios.items()), key=lambda x: x[0])
    sorted_transactions = sorted(list(transactions))
    trans_idx = 0
    transac = sorted_transactions[trans_idx]
    for pf_idx, date_portfol in enumerate(sorted_portfolios):
        if trans_idx >= len(transactions):
            # all transactions have been processed
            break
        while date_portfol[0] >= transac.transaction_date:
            match transac.kind:
                case ShareTransactionKind.BUY:
                    investment = round(transac.nr_stocks * transac.price, 2)
                    realization = 0.0
                case ShareTransactionKind.SELL:
                    investment = 0.0
                    realization = 0.0
                    if pf_idx == 0 or not (
                        (
                            prev_pos := sorted_portfolios[pf_idx - 1][1].get(
                                transac.isin, None
                            )
                        )
                        and (prev_pos.nr_stocks > 0.0)
                    ):
                        print(
                            "Cannot process sell transaction, no position found to determine buy price"
                        )
                    else:
                        buy_price = prev_pos.investment / prev_pos.nr_stocks
                        investment = round(-transac.nr_stocks * buy_price, 2)
                        realization = round(
                            transac.nr_stocks * (transac.price - buy_price), 2
                        )
                case ShareTransactionKind.DIVIDEND:
                    investment = 0.0
                    realization = round(transac.nr_stocks * transac.price, 2)
            for dt_spf in sorted_portfolios[pf_idx:]:
                shpf = dt_spf[1]
                if share_pos := shpf.get(transac.isin, None):
                    shpf[transac.isin] = replace(
                        share_pos,
                        investment=round(share_pos.investment + investment, 2),
                        realized=round(share_pos.realized + realization, 2),
                    )
            trans_idx += 1
            if trans_idx >= len(transactions):
                break
            transac = sorted_transactions[trans_idx]

    return portfolios


def get_all_isins(portfolios: tuple[SharePortfolio, ...]) -> set[IsinStr]:
    """Get all the ISIN's present in the portfolios."""
    ret_val: set[IsinStr] = set()
    for porto in portfolios:
        ret_val.update(porto.all_isins())
    return ret_val
