"""Dataclasses for share transactions"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime
from enum import Enum, auto
from .currencies import Amount
from .shares import IsinStr


ZERO_MARGIN: float = 0.05


class ShareTransactionKind(Enum):
    """Enum with the type of possible transactions."""

    BUY = auto()
    SELL = auto()
    DIVIDEND = auto()


@dataclass(frozen=False, order=True)
class CurrencyExchange:
    """For representing an exchange at a certain date.

    Attributes
    ----------
    exchange_datetime     : the date for which the exchange is registered
    exchange_rate         : the rate of exchange applied in the transaction
    amount_from           : the amount before the exchange, i.e., in a currency other than EUR (usually negative)
    exchange_rate_exact   : the rate of exchange that is exactly value_to / -value_from (no init)
    amount_to             : the amount after the exchange, in EUR (no init)
    amount_trans          : the amount that was traced back to transactions, in the same currency as amount_from (no init)
    """

    exchange_datetime: datetime
    exchange_rate: float
    amount_from: Amount
    exchange_rate_exact: float = field(init=False)
    amount_to: Amount = field(init=False)
    amount_trans: Amount = field(init=False)

    def __post_init__(self) -> None:
        assert self.exchange_rate > 0.0
        assert self.amount_from.value != 0.0
        self.amount_to = Amount(-self.amount_from.value_exact / self.exchange_rate)
        self.exchange_rate_exact = -self.amount_from.value / self.amount_to.value
        self.amount_trans = replace(self.amount_from, value_exact=0.0)

    @property
    def exchange_date(self) -> date:
        "Exchange date"
        return self.exchange_datetime.date()

    @property
    def amount_trans_remaining(self) -> Amount:
        "The part of -value_from that has not yet been traced to a transaction"
        return -self.amount_from - self.amount_trans

    def has_been_traced_fully(self) -> bool:
        "Return True if the amount traced to transactions equals the value_to"
        # we'll allow for a little margin
        return abs(self.amount_trans_remaining.value) < ZERO_MARGIN

    def can_take_exchange_amount(self, the_amount: Amount) -> bool:
        "Return True if the_value fits in value_trans_remaining"
        if self.has_been_traced_fully():
            return False
        # the_amount must have the same sign as amount_trans_remaining
        if the_amount.value * self.amount_trans_remaining.value < 0.0:
            return False
        if the_amount.value < 0.0:
            # we'll allow for a (positive) little margin
            return (self.amount_trans_remaining - the_amount).value < ZERO_MARGIN
        # we'll allow for a (negative) little margin
        return (self.amount_trans_remaining - the_amount).value > -ZERO_MARGIN

    def take_exchange(self, amount: Amount) -> Amount:
        "Apply the exchange to amount, return the amount in EUR"
        assert self.can_take_exchange_amount(amount)
        self.amount_trans += amount
        return Amount(
            value_exact=amount.value_exact / self.exchange_rate_exact, curr="EUR"
        )


@dataclass(frozen=True, order=True)
class ShareTransaction:
    """For representing a stock shares transaction at a certain date.

    Attributes
    ----------
    transaction_datetime  : the date for which the value of the share position is registered
    isin                  : the ISIN code / Symbol string used to identify a share
    curr                  : the currency shorthand in which the transaction is done, e.g. EUR
    nr_stocks             : the number of items in the transaction
    price                 : the price per item, in curr
    kind                  : the kind of transaction
    value_in_eur          : the value of the transaction in EUR
    """

    transaction_datetime: datetime
    isin: IsinStr
    curr: str
    nr_stocks: float
    price: float
    kind: ShareTransactionKind
    value_in_eur: float

    @property
    def transaction_date(self) -> date:
        "Transaction date"
        return self.transaction_datetime.date()
