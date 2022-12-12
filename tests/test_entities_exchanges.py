# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
from datetime import date, datetime, timedelta
import pytest
from stockwatch.entities.currencies import (
    Amount,
)
from stockwatch.entities.transactions import (
    CurrencyExchange,
)


@pytest.fixture
def example_exchange_1() -> CurrencyExchange:
    return CurrencyExchange(
        exchange_datetime=datetime.now() - timedelta(days=7),
        rate=1.1095,
        amount_from=Amount(-80.24, "USD"),
    )


@pytest.fixture
def example_exchange_2() -> CurrencyExchange:
    return CurrencyExchange(
        exchange_datetime=datetime.now() - timedelta(days=7),
        rate=1.1095,
        amount_from=Amount(80.24, "USD"),
    )


def test_exchange_date(
    example_exchange_1: CurrencyExchange,
) -> None:
    assert example_exchange_1.exchange_date == date.today() - timedelta(days=7)


def test_exchange_1(
    example_exchange_1: CurrencyExchange,
) -> None:
    assert not example_exchange_1.has_been_traced_fully()
    assert not example_exchange_1.can_take_exchange(Amount(25.24, "EUR"))
    assert example_exchange_1.can_take_exchange(Amount(25.24, "USD"))
    prt1 = example_exchange_1.take_exchange(Amount(25.24, "USD"))
    assert prt1.curr == "EUR"
    assert not example_exchange_1.can_take_exchange(Amount(80.24, "USD"))
    assert example_exchange_1.can_take_exchange(Amount(55.0, "USD"))
    prt2 = example_exchange_1.take_exchange(Amount(55.0, "USD"))
    assert (prt1 + prt2).value == 72.32
    assert example_exchange_1.has_been_traced_fully()
    assert not example_exchange_1.can_take_exchange(Amount(0.01, "USD"))


def test_exchange_2(
    example_exchange_2: CurrencyExchange,
) -> None:
    assert not example_exchange_2.can_take_exchange(Amount(25.24, "USD"))
    assert example_exchange_2.can_take_exchange(Amount(-55.0, "USD"))
