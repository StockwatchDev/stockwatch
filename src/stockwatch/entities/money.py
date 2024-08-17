"""This module contains currency dataclasses.

This package has a clean architecture. Hence, this module should not depend on any
other module and only import Python stuff.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime

ZERO_MARGIN: float = 0.05


@dataclass(frozen=True, order=False)
class Amount:
    """For dataclasses representing an amount in a certain currency.

    Attributes
    ----------
    value_exact           : the unrounded value
    curr                  : the currency
    value                 : the value rounded to 2 decimals
    """

    value_exact: float = field(default=0.0)
    curr: str = field(default="EUR")
    value: float = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", round(self.value_exact, 2))

    def __lt__(self, other: object) -> bool:
        "Raise error if currencies do not match; return true if self.value < other.value (i.e., the rounded values)"
        if (not isinstance(other, Amount)) or (self.curr != other.curr):
            raise NotImplementedError
        return self.value.__lt__(other.value)

    def __le__(self, other: object) -> bool:
        "Raise error if currencies do not match; return true if self.value <= other.value (i.e., the rounded values)"
        if (not isinstance(other, Amount)) or (self.curr != other.curr):
            raise NotImplementedError
        return self.value.__le__(other.value)

    def __eq__(self, other: object) -> bool:
        "Return true if currencies match and self.value equals other.value (i.e., the rounded values)"
        if not isinstance(other, Amount):
            raise NotImplementedError
        return self.curr == other.curr and self.value == other.value

    def __ge__(self, other: object) -> bool:
        "Raise error if currencies do not match; return true if self.value >= other.value (i.e., the rounded values)"
        if (not isinstance(other, Amount)) or (self.curr != other.curr):
            raise NotImplementedError
        return self.value.__ge__(other.value)

    def __gt__(self, other: object) -> bool:
        "Raise error if currencies do not match; return true if self.value > other.value (i.e., the rounded values)"
        if (not isinstance(other, Amount)) or (self.curr != other.curr):
            raise NotImplementedError
        return self.value.__ge__(other.value)

    def __add__(self, other: Amount) -> Amount:
        "Return an amount self.value + other.value"
        assert self.curr == other.curr, f"cannot add {self} to {other}"
        return replace(self, value_exact=self.value_exact + other.value_exact)

    def __sub__(self, other: Amount) -> Amount:
        "Return an amount self.value - other.value"
        assert self.curr == other.curr, f"cannot subtract {self} from {other}"
        return replace(self, value_exact=self.value_exact - other.value_exact)

    def __neg__(self) -> Amount:
        "Return an amount with negated self.value"
        return replace(self, value_exact=-self.value_exact)

    def __pos__(self) -> Amount:
        "Return an amount with self.value"
        return self

    def __mul__(self, factor: float) -> Amount:
        "Return an amount self.value_exact * factor"
        return replace(self, value_exact=(self.value_exact * factor))

    def __rmul__(self, factor: float) -> Amount:
        "Return an amount self.value_exact * factor"
        return replace(self, value_exact=(self.value_exact * factor))

    def __truediv__(self, divisor: float | int | Amount) -> Amount:
        "Return an amount self.value_exact * (1.0/divisor)"
        if isinstance(divisor, (float, int)):
            return replace(self, value_exact=(self.value_exact * (1.0 / divisor)))
        assert isinstance(divisor, Amount)
        assert self.curr == divisor.curr, f"cannot divide {self} by {divisor}"
        return replace(self, value_exact=(self.value_exact / divisor.value_exact))


@dataclass(frozen=False, order=True)
class CurrencyExchange:
    """For representing an exchange at a certain date.

    Attributes
    ----------
    exchange_datetime     : the date and time for which the exchange is registered
    rate                  : the rate of exchange applied in the transaction
    amount_from           : the amount before the exchange, i.e., in a currency other than EUR (usually negative)
    rate_exact            : the rate of exchange that is exactly value_to / -value_from (no init)
    amount_to             : the amount after the exchange, in EUR (no init)
    amount_trans          : the amount that was traced back to transactions, in the same currency as amount_from (no init)
    """

    exchange_datetime: datetime
    rate: float
    amount_from: Amount
    rate_exact: float = field(init=False)
    amount_to: Amount = field(init=False)
    amount_trans: Amount = field(init=False)

    def __post_init__(self) -> None:
        assert self.rate > 0.0
        assert self.amount_from.value != 0.0
        self.amount_to = Amount(-self.amount_from.value_exact / self.rate)
        self.rate_exact = -self.amount_from.value / self.amount_to.value
        self.amount_trans = replace(self.amount_from, value_exact=0.0)

    @property
    def exchange_date(self) -> date:
        "Exchange date"
        return self.exchange_datetime.date()

    @property
    def amount_trans_remaining(self) -> Amount:
        "The part of -amount_from that has not yet been traced to a transaction"
        return -self.amount_from - self.amount_trans

    def has_been_traced_fully(self) -> bool:
        "Return True if the amount traced to transactions equals the value_to"
        # we'll allow for a little margin
        return abs(self.amount_trans_remaining.value) < ZERO_MARGIN

    def can_take_exchange(self, the_amount: Amount) -> bool:
        "Return True if the_value fits in value_trans_remaining"
        if self.amount_from.curr != the_amount.curr:
            return False
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
        assert self.can_take_exchange(amount)
        self.amount_trans = self.amount_trans + amount
        return Amount(value_exact=amount.value_exact / self.rate_exact, curr="EUR")
