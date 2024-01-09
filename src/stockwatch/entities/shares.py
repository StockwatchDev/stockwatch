"""Dataclasses for holding a share portfolio"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date

from .money import Amount
from .transactions import IsinStr, ShareTransaction, ShareTransactionKind

UNKNOWN_POSITION_NAME: str = "Name Unknown"


@dataclass(frozen=True, order=True)
class SharePosition:  # pylint: disable=too-many-instance-attributes
    """For representing a stock shares position at a certain date.

    Attributes
    ----------
    position_date   : the date for which the value of the share position is registered
    value           : the current value of the shares, in EUR
    isin            : the ISIN code / Symbol string used to identify a share
    name            : the name of the share
    investment      : the amount in EUR spent in purchasing the shares
    nr_stocks       : the number of shares
    price           : the current price of the shares in the currency in which the stock is traded, e.g. USD
    realized        : the realized return in EUR (including trading costs, ex tax)
    unrealized      : the unrealized return in EUR, i.e., value - investment (no init)
    total_return    : the sum of realized and unrealized return in EUR (no init)
    """

    position_date: date
    value: Amount
    isin: IsinStr
    name: str
    investment: Amount
    nr_stocks: float
    price: Amount
    realized: Amount
    unrealized: Amount = field(init=False)
    total_return: Amount = field(init=False)

    @classmethod
    def empty_position(
        cls,
        position_date: date,
        isin: IsinStr,
        name: str = UNKNOWN_POSITION_NAME,
        realized: Amount = Amount(0.0),
    ) -> SharePosition:
        """Return an empty position dated the_date with isin the_isin"""
        return SharePosition(
            position_date=position_date,
            value=Amount(0.0),
            isin=isin,
            name=name,
            investment=Amount(0.0),
            nr_stocks=0.0,
            price=Amount(1.0),
            realized=realized,
        )

    def __post_init__(self) -> None:
        # because frozen=True, we need to use __setattr__ here:
        object.__setattr__(self, "unrealized", self.value - self.investment)
        object.__setattr__(self, "total_return", self.realized + self.unrealized)


# next line placed here because of SharePosition
PortfoliosDictionary = dict[date, dict[IsinStr, SharePosition]]


@dataclass(frozen=True, order=True)
class SharePortfolio:
    """For representing a stock shares portfolio (i.e. multiple positions) at a certain date.

    Attributes
    ----------
    portfolio_date  : the date for which the value of the share portfolio is registered
    value           : the current value of the portfolio, in EUR
    investment      : the amount in EUR spent in purchasing the portfolio
    realized        : the realized return in EUR (including trading costs, ex tax)
    unrealized      : the unrealized return in EUR, i.e., value - investment
    total_return    : the sum of realized and unrealized return
    share_positions : the collection of share positions
    """

    portfolio_date: date = field(init=False)
    value: Amount = field(init=False)
    investment: Amount = field(init=False)
    realized: Amount = field(init=False)
    unrealized: Amount = field(init=False)
    total_return: Amount = field(init=False)
    share_positions: tuple[SharePosition, ...]

    def __post_init__(self) -> None:
        the_date: date
        if self.share_positions:
            the_date = self.share_positions[0].position_date
        else:
            the_date = date.today()
            print("No share positions added, this is useless and will not work.")
        # because frozen=True, we need to use __setattr__ here:
        object.__setattr__(self, "portfolio_date", the_date)
        for attribute in (
            "value",
            "investment",
            "realized",
            "unrealized",
            "total_return",
        ):
            object.__setattr__(
                self,
                attribute,
                sum(
                    (
                        getattr(share_pos, attribute)
                        for share_pos in self.share_positions
                    ),
                    Amount(0.0),
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


def to_portfolios(
    spf_dict: PortfoliosDictionary,
) -> tuple[SharePortfolio, ...]:
    """Return a tuple of SharePortfolios that represent spf_dict"""
    sps_list = [
        # sps_dict.values() is a list of SharePositions
        # sort them to have a defined order
        # sorting order is defined by SharePosition attribute order
        # first by date (equal for all in the list), then by value
        SharePortfolio(tuple(sorted(sps_dict.values())))
        for _, sps_dict in spf_dict.items()
    ]
    return tuple(sorted(sps_list))


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


def _get_transaction_result(
    transaction: ShareTransaction, prev_pos: SharePosition | None
) -> tuple[Amount, Amount]:
    investment = Amount(0.0)
    realization = Amount(0.0)
    match transaction.kind:
        case ShareTransactionKind.BUY:
            investment = transaction.amount
        case ShareTransactionKind.SELL:
            if not prev_pos:
                print(
                    f"Cannot process sell transaction dated {transaction.transaction_date}, no position found to determine buy price"
                )
            elif prev_pos.nr_stocks == 0:
                print(
                    f"Cannot process sell transaction dated {transaction.transaction_date}, no stocks present to determine buy price"
                )
            else:
                buy_price = prev_pos.investment / prev_pos.nr_stocks
                investment = -transaction.nr_stocks * buy_price
                # we cannot use transaction.price, because that can be in non-EUR currency
                sell_price = transaction.amount / transaction.nr_stocks
                realization = transaction.nr_stocks * (sell_price - buy_price)
        case ShareTransactionKind.DIVIDEND | ShareTransactionKind.EXPENSES:
            realization = transaction.amount

    return investment, realization


def apply_transactions(
    transactions: tuple[ShareTransaction, ...],
    portfolios: PortfoliosDictionary,
) -> None:
    """Process transactions to add the investment and realization of the portfolios."""
    sorted_portfolios = sorted(list(portfolios.items()), key=lambda x: x[0])
    sorted_transactions = sorted(list(transactions))

    idx_of_first_pf_to_process = 0
    for transaction in sorted_transactions:
        # find the index of the first portfolio on or after the transaction date
        # as transactions are sorted for date,
        # we can start searching from idx_of_first_pf_to_process
        for idx, (port_date, portfolio) in enumerate(
            sorted_portfolios[idx_of_first_pf_to_process:]
        ):
            if port_date >= transaction.transaction_date:
                # the first portfolio on or after the transaction date is found
                # it is positioned idx positions later than idx_of_first_pf_to_process:
                idx_of_portfolio_after_transaction = idx_of_first_pf_to_process + idx
                break
        else:
            # No portfolio found after the transaction date
            # hence further processing not needed
            break

        # for the sell transaction we need to find the last position before the transaction
        prev_position: SharePosition | None = None
        if (
            transaction.kind == ShareTransactionKind.SELL
            and idx_of_portfolio_after_transaction > 0
        ):
            prev_position = sorted_portfolios[idx_of_portfolio_after_transaction - 1][
                1
            ].get(transaction.isin)

        investment, realization = _get_transaction_result(transaction, prev_position)

        for port_date, portfolio in sorted_portfolios[
            idx_of_portfolio_after_transaction:
        ]:
            if share_pos := portfolio.get(transaction.isin):
                portfolio[transaction.isin] = replace(
                    share_pos,
                    investment=share_pos.investment + investment,
                    realized=share_pos.realized + realization,
                )
        # prepare for the next round
        idx_of_first_pf_to_process = idx_of_portfolio_after_transaction
        idx_of_portfolio_after_transaction = -1


def get_all_isins(portfolios: tuple[SharePortfolio, ...]) -> set[IsinStr]:
    """Get all the ISIN's present in the portfolios."""
    ret_val: set[IsinStr] = set()
    for porto in portfolios:
        ret_val.update(porto.all_isins())
    return ret_val
