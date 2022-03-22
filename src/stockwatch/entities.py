from dataclasses import dataclass
from datetime import date
from enum import Enum, auto


class ShareTransactionKind(Enum):
    BUY = auto()
    SELL = auto()
    DIVIDEND = auto()


@dataclass(frozen=False)
class ShareTransaction:
    """
    For representing a stock shares transaction at a certain date

    Attributes
    ----------
    kind              : the kind of transaction
    isin              : the ISIN code / Symbol string used to identify a share
    curr              : the currency shorthand in which the transaction is done, e.g. EUR
    nr                : the number of items in the transaction
    price             : the price per item, in curr
    transaction_date  : the date for which the value of the share position is registered
    """

    kind: ShareTransactionKind
    isin: str
    curr: str
    nr: int
    price: float
    transaction_date: date


@dataclass(frozen=False)
class SharePosition:
    """
    For representing a stock shares position at a certain date

    Attributes
    ----------
    name            : the name of the share
    isin            : the ISIN code / Symbol string used to identify a share
    curr            : the currency shorthand in which the stock is traded, e.g. EUR
    investment      : the amount in EUR spent in purchasing the shares
    nr              : the number of shares
    price           : the current price of the shares, in curr
    value           : the current value of the shares, in EUR
    realized        : the realized result in EUR (including trading costs)
    position_date   : the date for which the value of the share position is registered
    """

    name: str
    isin: str
    curr: str
    investment: float
    nr: int
    price: float
    value: float
    realized: float
    position_date: date


@dataclass(frozen=True)
class SharePortfolio:
    """
    For representing a stock shares portfolio (i.e. multiple positions) at a certain date

    Attributes
    ----------
    share_positions : the collection of share positions
    portfolio_date           : the date of the registered share positions
    """

    share_positions: tuple[SharePosition, ...]
    portfolio_date: date

    @property
    def total_value(self) -> float:
        """The total value of this portfolio"""
        return round(sum([share_pos.value for share_pos in self.share_positions]), 2)

    @property
    def total_investment(self) -> float:
        """The total iinvestment of this portfolio"""
        return round(
            sum([share_pos.investment for share_pos in self.share_positions]), 2
        )

    def contains(self, an_isin: str) -> bool:
        """Return True if self has a share position with ISIN an_isin"""
        return an_isin in [share_pos.isin for share_pos in self.share_positions]

    def get_position(self, the_isin: str) -> SharePosition | None:
        """Return the share position with ISIN the_isin or None if not present"""
        for share_pos in self.share_positions:
            if share_pos.isin == the_isin:
                return share_pos
        return None

    def value_of(self, the_isin: str) -> float:
        """Return the value in EUR of the share position with ISIN the_isin"""
        return round(
            sum(
                [
                    share_pos.value if share_pos.isin == the_isin else 0.0
                    for share_pos in self.share_positions
                ]
            ),
            2,
        )

    def investment_of(self, the_isin: str) -> float:
        """Return the investment in EUR of the share position with ISIN the_isin"""
        return round(
            sum(
                [
                    share_pos.investment if share_pos.isin == the_isin else 0.0
                    for share_pos in self.share_positions
                ]
            ),
            2,
        )

    def realized_return_of(self, the_isin: str) -> float:
        """Return the realized return in EUR of the share position with ISIN the_isin"""
        return round(
            sum(
                [
                    share.realized if share.isin == the_isin else 0.0
                    for share in self.share_positions
                ]
            ),
            2,
        )

    def all_isins(self) -> tuple[str, ...]:
        """Return the ISIN codes of the share positions"""
        return tuple(share_pos.isin for share_pos in self.share_positions)

    def all_isins_and_names(self) -> dict[str, str]:
        """Return the ISIN codes and names of the share positions"""
        return {share_pos.isin: share_pos.name for share_pos in self.share_positions}

    def is_date_consistent(self) -> bool:
        """Return True if the share positions dates all match self.portfolio_date"""
        return all(
            share_pos.position_date == self.portfolio_date
            for share_pos in self.share_positions
        )


def closest_portfolio_after_date(
    share_portfolios: tuple[SharePortfolio, ...], date: date
) -> SharePortfolio | None:
    """Return the share portfolio on or closest after date or None if no portfolio matches that"""
    portfolios_after_date = [
        spf for spf in share_portfolios if spf.portfolio_date >= date
    ]
    if len(portfolios_after_date) > 0:
        sorted_portfolios = sorted(
            portfolios_after_date, key=lambda x: x.portfolio_date
        )
        return sorted_portfolios[0]
    else:
        return None


def closest_portfolio_before_date(
    share_portfolios: tuple[SharePortfolio, ...], date: date
) -> SharePortfolio | None:
    """Return the share portfolio closest before date or None if no portfolio matches that"""
    portfolios_before_date = [
        spf for spf in share_portfolios if spf.portfolio_date < date
    ]
    if len(portfolios_before_date) > 0:
        sorted_portfolios = sorted(
            portfolios_before_date, key=lambda x: x.portfolio_date
        )
        return sorted_portfolios[-1]
    else:
        return None


def _add_investment_realization(
    investment: float,
    realization: float,
    transaction_date: date,
    isin: str,
    portfolios: tuple[SharePortfolio, ...],
) -> None:
    """Add a realization and/or investment amount to each portfolio dated later than transaction_date"""
    portfolios_to_modify = [
        spf for spf in portfolios if spf.portfolio_date > transaction_date
    ]
    for spf in portfolios_to_modify:
        pos = spf.get_position(isin)
        if pos:
            pos.investment = round(pos.investment + investment, 2)
            pos.realized = round(pos.realized + realization, 2)


def process_buy_transaction(
    transaction: ShareTransaction, portfolios: tuple[SharePortfolio, ...]
) -> None:
    assert (
        transaction.kind == ShareTransactionKind.BUY
    ), f"Buy transaction expected, got {transaction.kind.name}"

    investment = transaction.nr * transaction.price
    realization = 0.0
    _add_investment_realization(
        investment=investment,
        realization=realization,
        transaction_date=transaction.transaction_date,
        isin=transaction.isin,
        portfolios=portfolios,
    )


def process_sell_transaction(
    transaction: ShareTransaction, portfolios: tuple[SharePortfolio, ...]
) -> None:
    assert (
        transaction.kind == ShareTransactionKind.SELL
    ), f"Sell transaction expected, got {transaction.kind.name}"

    first_changed_portfolio = closest_portfolio_after_date(
        portfolios, transaction.transaction_date
    )
    if not first_changed_portfolio:
        print(
            "Cannot process sell transaction, no portfolio present after transaction date"
        )
        return

    next_pos = first_changed_portfolio.get_position(transaction.isin)
    last_unchanged_portfolio = closest_portfolio_before_date(
        portfolios, transaction.transaction_date
    )
    if not last_unchanged_portfolio:
        print(
            "Cannot process sell transaction, no portfolio present before transaction date"
        )
        return

    current_pos = last_unchanged_portfolio.get_position(transaction.isin)
    if not current_pos:
        print(
            "Cannot process sell transaction, position not present in last portfolio before transaction date"
        )
        return

    buy_price = current_pos.investment / current_pos.nr
    investment = round(-transaction.nr * buy_price, 2)
    realization = round(transaction.nr * (transaction.price - buy_price), 2)
    if not next_pos:
        # the portfolio on the next date does not have this share because we sell all
        # so let's create a position with the realization
        next_pos = SharePosition(
            name=current_pos.name,
            isin=current_pos.isin,
            curr=current_pos.curr,
            investment=0.0,
            nr=0,
            price=1.0,
            value=0.0,
            realized=realization,
            position_date=first_changed_portfolio.portfolio_date,
        )
        print(
            f"ISIN {transaction.isin} has been sold, total realization: {next_pos.realized}\n"
        )
    _add_investment_realization(
        investment=investment,
        realization=realization,
        transaction_date=transaction.transaction_date,
        isin=transaction.isin,
        portfolios=portfolios,
    )


def process_dividend_transaction(
    transaction: ShareTransaction, portfolios: tuple[SharePortfolio, ...]
) -> None:
    assert (
        transaction.kind == ShareTransactionKind.DIVIDEND
    ), f"Dividend transaction expected, got {transaction.kind.name}"

    realization = round(transaction.nr * transaction.price, 2)
    _add_investment_realization(
        investment=0.0,
        realization=realization,
        transaction_date=transaction.transaction_date,
        isin=transaction.isin,
        portfolios=portfolios,
    )
