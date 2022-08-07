"""This module contains the business logic for holding a stock portfolio.

This package has a clean architecture. Hence, this module should not depend on any
other module and only import Python stuff.
"""
from dataclasses import dataclass, field, replace
from datetime import date
from enum import Enum, auto


class ShareTransactionKind(Enum):
    """Enum with the type of possible transactions."""

    BUY = auto()
    SELL = auto()
    DIVIDEND = auto()


@dataclass(frozen=False)
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

    kind: ShareTransactionKind
    isin: str
    curr: str
    nr_stocks: float
    price: float
    transaction_date: date


@dataclass(frozen=True, order=True)
class SharePosition:  # pylint: disable=too-many-instance-attributes
    """For representing a stock shares position at a certain date.

    Attributes
    ----------
    name            : the name of the share
    isin            : the ISIN code / Symbol string used to identify a share
    curr            : the currency shorthand in which the stock is traded, e.g. EUR
    investment      : the amount in EUR spent in purchasing the shares
    nr_stocks       : the number of shares
    price           : the current price of the shares, in curr
    value           : the current value of the shares, in EUR
    realized        : the realized result in EUR (including trading costs)
    position_date   : the date for which the value of the share position is registered
    """

    sort_index1: date = field(init=False, repr=False)
    sort_index2: float = field(init=False, repr=False)
    name: str
    isin: str
    curr: str
    investment: float
    nr_stocks: float
    price: float
    value: float
    realized: float
    position_date: date

    def __post_init__(self) -> None:
        # because frozen=True, we need to use __setattr__ here:
        object.__setattr__(self, "sort_index1", self.position_date)
        object.__setattr__(self, "sort_index2", self.value)


@dataclass(frozen=False, order=True)
class SharePortfolio:
    """For representing a stock shares portfolio (i.e. multiple positions) at a certain date.

    Attributes
    ----------
    share_positions         : the collection of share positions
    portfolio_date          : the date of the registered share positions
    """

    sort_index1: date = field(init=False, repr=False)
    sort_index2: float = field(init=False, repr=False)
    share_positions: dict[str, SharePosition]
    portfolio_date: date

    def __post_init__(self) -> None:
        self.sort_index1 = self.portfolio_date
        self.sort_index2 = self.total_value

    @property
    def total_value(self) -> float:
        """Return the total value of this portfolio."""
        return round(
            sum(share_pos.value for share_pos in self.share_positions.values()), 2
        )

    @property
    def total_investment(self) -> float:
        """Return the total investment of this portfolio."""
        return round(
            sum(share_pos.investment for share_pos in self.share_positions.values()), 2
        )

    @property
    def total_realized_return(self) -> float:
        """Return the total realized return of this portfolio."""
        return round(
            sum(share_pos.realized for share_pos in self.share_positions.values()), 2
        )

    def contains(self, an_isin: str) -> bool:
        """Return True if self has a share position with ISIN an_isin."""
        return an_isin in self.share_positions

    def get_position(self, the_isin: str) -> SharePosition | None:
        """Return the share position with ISIN the_isin or None if not present."""
        return self.share_positions.get(the_isin, None)

    def value_of(self, the_isin: str) -> float:
        """Return the value in EUR of the share position with ISIN the_isin."""
        return round(
            self.share_positions[the_isin].value
            if the_isin in self.share_positions
            else 0.0,
            2,
        )

    def investment_of(self, the_isin: str) -> float:
        """Return the investment in EUR of the share position with ISIN the_isin."""
        return round(
            self.share_positions[the_isin].investment
            if the_isin in self.share_positions
            else 0.0,
            2,
        )

    def realized_return_of(self, the_isin: str) -> float:
        """Return the realized return in EUR of the share position with ISIN the_isin."""
        return round(
            self.share_positions[the_isin].realized
            if the_isin in self.share_positions
            else 0.0,
            2,
        )

    def all_isins(self) -> tuple[str, ...]:
        """Return the ISIN codes of the share positions."""
        return tuple(self.share_positions.keys())

    def all_isins_and_names(self) -> dict[str, str]:
        """Return the ISIN codes and names of the share positions."""
        return {
            isin: share_pos.name for isin, share_pos in self.share_positions.items()
        }

    def is_date_consistent(self) -> bool:
        """Return True if the share positions dates all match self.portfolio_date."""
        return all(
            share_pos.position_date == self.portfolio_date
            for share_pos in self.share_positions.values()
        )

    def add_investment_realization(
        self,
        investment: float,
        realization: float,
        isin: str,
    ) -> None:
        """Add a realization and/or investment to the sharepos with the specified isin."""
        if pos := self.get_position(isin):
            new_investment = round(pos.investment + investment, 2)
            new_realization = round(pos.realized + realization, 2)
            self.share_positions[isin] = replace(
                pos, investment=new_investment, realized=new_realization
            )


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


def _add_investment_realization(
    investment: float,
    realization: float,
    transaction_date: date,
    isin: str,
    portfolios: tuple[SharePortfolio, ...],
) -> None:
    """Add a realization and/or investment amount to each portfolio dated
    after the transaction_date.
    """
    portfolios_to_modify = [
        spf for spf in portfolios if spf.portfolio_date > transaction_date
    ]
    for spf in portfolios_to_modify:
        spf.add_investment_realization(investment, realization, isin)


def apply_transactions(
    transactions: tuple[ShareTransaction, ...], portfolios: tuple[SharePortfolio, ...]
) -> None:
    """Process transactions to add the investment and realization of the portfolios."""
    for transaction in transactions:
        match transaction.kind:
            case ShareTransactionKind.BUY:
                _process_buy_transaction(transaction, portfolios)
            case ShareTransactionKind.SELL:
                _process_sell_transaction(transaction, portfolios)
            case ShareTransactionKind.DIVIDEND:
                _process_dividend_transaction(transaction, portfolios)
            case _:
                print(f"Cannot process unknown transaction kind {transaction.kind}")


def get_all_isins(portfolios: tuple[SharePortfolio, ...]) -> set[str]:
    """Get all the ISIN's present in the portfolios."""
    ret_val: set[str] = set()
    for porto in portfolios:
        ret_val.update(porto.all_isins())
    return ret_val


def _process_buy_transaction(
    transaction: ShareTransaction, portfolios: tuple[SharePortfolio, ...]
) -> None:
    assert (
        transaction.kind == ShareTransactionKind.BUY
    ), f"Buy transaction expected, got {transaction.kind.name}"

    investment = transaction.nr_stocks * transaction.price
    realization = 0.0
    _add_investment_realization(
        investment=investment,
        realization=realization,
        transaction_date=transaction.transaction_date,
        isin=transaction.isin,
        portfolios=portfolios,
    )


def _process_sell_transaction(
    transaction: ShareTransaction, portfolios: tuple[SharePortfolio, ...]
) -> None:
    assert (
        transaction.kind == ShareTransactionKind.SELL
    ), f"Sell transaction expected, got {transaction.kind.name}"

    current_portfolio = closest_portfolio_before_date(
        portfolios, transaction.transaction_date
    )
    if not current_portfolio:
        print(
            "Cannot process sell transaction, no portfolio present before transaction date"
        )
        return

    if not (current_pos := current_portfolio.get_position(transaction.isin)):
        print(
            "Cannot process sell transaction, position not present in last portfolio before"
            f" the transaction date: {transaction.transaction_date}"
        )
        return

    if not (
        next_portfolio := closest_portfolio_after_date(
            portfolios, transaction.transaction_date
        )
    ):
        print(
            "Cannot process sell transaction, no portfolio present after transaction date"
        )
        return

    buy_price = current_pos.investment / current_pos.nr_stocks
    realization = round(transaction.nr_stocks * (transaction.price - buy_price), 2)
    if next_portfolio.get_position(transaction.isin):
        investment = round(-transaction.nr_stocks * buy_price, 2)
        _add_investment_realization(
            investment=investment,
            realization=realization,
            transaction_date=transaction.transaction_date,
            isin=transaction.isin,
            portfolios=portfolios,
        )
    else:
        # the portfolio on the next date does not have this share because we sell all
        # so let's create a position with the realization
        realization_pos = SharePosition(
            name=current_pos.name,
            isin=current_pos.isin,
            curr=current_pos.curr,
            investment=0.0,
            nr_stocks=0,
            price=1.0,
            value=0.0,
            realized=round(current_pos.realized + realization, 2),
            position_date=next_portfolio.portfolio_date,
        )
        next_portfolio.share_positions[current_pos.isin] = realization_pos
        print(
            f"ISIN {transaction.isin} has been sold, total realization: "
            f"{realization_pos.realized}\n"
        )


def _process_dividend_transaction(
    transaction: ShareTransaction, portfolios: tuple[SharePortfolio, ...]
) -> None:
    assert (
        transaction.kind == ShareTransactionKind.DIVIDEND
    ), f"Dividend transaction expected, got {transaction.kind.name}"

    realization = round(transaction.nr_stocks * transaction.price, 2)
    _add_investment_realization(
        investment=0.0,
        realization=realization,
        transaction_date=transaction.transaction_date,
        isin=transaction.isin,
        portfolios=portfolios,
    )
