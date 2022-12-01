"""This module contains currency dataclasses.

This package has a clean architecture. Hence, this module should not depend on any
other module and only import Python stuff.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace


@dataclass(frozen=True, order=False)
class AmountInCurrency(ABC):
    """Abstract base class for dataclasses representing an amount in a certain currency.

    Attributes
    ----------
    value_exact           : the unrounded value
    value                 : the value rounded to 2 decimals
    curr                  : the currency
    """

    value_exact: float = field(default=0.0)
    value: float = field(init=False)
    curr: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", round(self.value_exact, 2))
        self._set_currency()

    @abstractmethod
    def _set_currency(self) -> None:
        "Set the currency field"

    def __add__(self, other: AmountInCurrency) -> AmountInCurrency:
        "Return an amount self.value + other.value"
        assert self.curr == other.curr
        return replace(self, value_exact=self.value + other.value)

    def __sub__(self, other: AmountInCurrency) -> AmountInCurrency:
        "Return an amount self.value + other.value"
        assert self.curr == other.curr
        return replace(self, value_exact=self.value - other.value)

    def __neg__(self) -> AmountInCurrency:
        "Return an amount with negated self.value"
        return replace(self, value_exact=-self.value)

    def __mul__(self, factor: float) -> AmountInCurrency:
        "Return an amount self.value * factor"
        return replace(self, value_exact=(self.value * factor))


@dataclass(frozen=True, order=False)
class AmountInEUR(AmountInCurrency):
    """For representing an amount in EUR.

    Attributes
    ----------
    value_exact           : the unrounded value
    value                 : the value rounded to 2 decimals
    curr                  : the currency
    """

    def _set_currency(self) -> None:
        "Set the currency field"
        # because frozen=True, we need to use __setattr__ here:
        object.__setattr__(self, "curr", "EUR")


@dataclass(frozen=True, order=False)
class AmountInUSD(AmountInCurrency):
    """For representing an amount in USD.

    Attributes
    ----------
    value_exact           : the unrounded value
    value                 : the value rounded to 2 decimals
    curr                  : the currency
    """

    def _set_currency(self) -> None:
        "Set the currency field"
        # because frozen=True, we need to use __setattr__ here:
        object.__setattr__(self, "curr", "USD")
