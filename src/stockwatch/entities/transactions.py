"""Dataclasses for share transactions"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum, auto
from typing import NewType

from .money import Amount

IsinStr = NewType("IsinStr", str)


class ShareTransactionKind(Enum):
    """Enum with the type of possible transactions."""

    BUY = auto()
    SELL = auto()
    DIVIDEND = auto()
    EXPENSES = auto()


@dataclass(frozen=True, order=True)
class ShareTransaction:
    """For representing a stock shares transaction at a certain date.

    Attributes
    ----------
    transaction_datetime  : the date and time for which the value of the share position is registered
    isin                  : the ISIN code / Symbol string used to identify a share
    nr_stocks             : the number of items in the transaction
    price                 : the price per item, in the currency in which the transaction is done, e.g. USD
    kind                  : the kind of transaction
    amount                : the value of the transaction in EUR
    """

    transaction_datetime: datetime
    isin: IsinStr
    nr_stocks: float
    price: Amount
    kind: ShareTransactionKind = field(compare=False)
    amount: Amount

    @property
    def transaction_date(self) -> date:
        "Transaction date"
        return self.transaction_datetime.date()


@dataclass(frozen=True, order=True)
class CashSettlement:
    """For representing a cash settlement of a stock share delisting at a certain date.

    Attributes
    ----------
    settlement_datetime   : the date  and time for which the value of the share position is registered
    isin                  : the ISIN code / Symbol string used to identify a share
    amount                : the value of the transaction
    """

    settlement_datetime: datetime
    isin: IsinStr
    amount: Amount

    @property
    def settlement_date(self) -> date:
        "Transaction date"
        return self.settlement_datetime.date()
