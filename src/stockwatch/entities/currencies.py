"""This module contains currency dataclasses.

This package has a clean architecture. Hence, this module should not depend on any
other module and only import Python stuff.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace


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

    def __truediv__(self, divisor: float) -> Amount:
        "Return an amount self.value_exact * (1.0/divisor)"
        return replace(self, value_exact=(self.value_exact * (1.0 / divisor)))
