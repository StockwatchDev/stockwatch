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

    def __add__(self, other: Amount) -> Amount:
        "Return an amount self.value + other.value"
        assert self.curr == other.curr
        return replace(self, value_exact=self.value + other.value)

    def __sub__(self, other: Amount) -> Amount:
        "Return an amount self.value + other.value"
        assert self.curr == other.curr
        return replace(self, value_exact=self.value - other.value)

    def __neg__(self) -> Amount:
        "Return an amount with negated self.value"
        return replace(self, value_exact=-self.value_exact)

    def __mul__(self, factor: float) -> Amount:
        "Return an amount self.value_exact * factor"
        return replace(self, value_exact=(self.value_exact * factor))
