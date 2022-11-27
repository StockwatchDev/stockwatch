# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
from datetime import date, datetime, timedelta
import pytest
from stockwatch.entities import (
    CurrencyExchange,
)


@pytest.fixture
def example_exchange_1() -> CurrencyExchange:
    return CurrencyExchange(
        exchange_datetime=datetime.now() - timedelta(days=7),
        exchange_rate=1.1095,
        value_from=-80.24,
        curr_from="USD",
    )


@pytest.fixture
def example_exchange_2() -> CurrencyExchange:
    return CurrencyExchange(
        exchange_datetime=datetime.now() - timedelta(days=7),
        exchange_rate=1.1095,
        value_from=80.24,
        curr_from="USD",
    )


def test_exchange_date(
    example_exchange_1: CurrencyExchange,
) -> None:
    assert example_exchange_1.exchange_date == date.today() - timedelta(days=7)


def test_exchange_1(
    example_exchange_1: CurrencyExchange,
) -> None:
    assert not example_exchange_1.has_been_traced_fully()
    assert example_exchange_1.can_take_exchange_value(25.24)
    prt1 = example_exchange_1.take_exchange(25.24)
    assert not example_exchange_1.can_take_exchange_value(80.24)
    assert example_exchange_1.can_take_exchange_value(55.0)
    prt2 = example_exchange_1.take_exchange(55.00)
    assert prt1 + prt2 == 72.32
    assert example_exchange_1.has_been_traced_fully()
    assert not example_exchange_1.can_take_exchange_value(0.01)


def test_exchange_2(
    example_exchange_2: CurrencyExchange,
) -> None:
    assert not example_exchange_2.can_take_exchange_value(25.24)
    assert example_exchange_2.can_take_exchange_value(-55.0)
