"""Dataclasses for share transactions"""
from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True, order=True)
class ShareTransaction:
    """For representing a stock shares transaction at a certain date.

    Attributes
    ----------
    transaction_datetime  : the date for which the value of the share position is registered
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
    kind: ShareTransactionKind
    amount: Amount

    @property
    def transaction_date(self) -> date:
        "Transaction date"
        return self.transaction_datetime.date()
