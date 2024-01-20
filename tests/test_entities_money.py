# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
from datetime import date, datetime, timedelta

import pytest

from stockwatch.entities.money import Amount, CurrencyExchange


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


@pytest.fixture
def example_amount_1() -> Amount:
    return Amount(3.3333333333)


@pytest.fixture
def example_amount_2() -> Amount:
    return Amount(6.6666666666)


@pytest.fixture
def example_amount_3() -> Amount:
    return Amount(3.3333333333, "USD")


def test_amount_comparison(
    example_amount_1: Amount, example_amount_2: Amount, example_amount_3: Amount
) -> None:
    assert example_amount_1 == Amount(3.3333333333)
    assert example_amount_1 != example_amount_2
    assert example_amount_1 != example_amount_3
    assert example_amount_1 < example_amount_2
    assert example_amount_1 <= example_amount_2
    assert example_amount_2 > example_amount_1
    assert example_amount_2 >= example_amount_1
    with pytest.raises(NotImplementedError):
        example_amount_1 == 0.0  # pylint: disable=pointless-statement
    with pytest.raises(NotImplementedError):
        example_amount_1 < example_amount_3  # pylint: disable=pointless-statement
    with pytest.raises(NotImplementedError):
        example_amount_1 <= example_amount_3  # pylint: disable=pointless-statement
    with pytest.raises(NotImplementedError):
        example_amount_1 > example_amount_3  # pylint: disable=pointless-statement
    with pytest.raises(NotImplementedError):
        example_amount_1 >= example_amount_3  # pylint: disable=pointless-statement


def test_amount_operators(
    example_amount_1: Amount,
    example_amount_2: Amount,
    example_amount_3: Amount,
) -> None:
    assert example_amount_1 == +example_amount_1
    assert 2.0 * example_amount_1 == example_amount_2
    assert example_amount_1 * 2 == example_amount_2
    assert example_amount_2 / 2 == example_amount_1
    assert example_amount_1 + example_amount_2 == Amount(10.0)
    assert example_amount_1 - example_amount_2 == -example_amount_1
    with pytest.raises(AssertionError):
        example_amount_1 + example_amount_3  # pylint: disable=pointless-statement
        example_amount_1 - example_amount_3  # pylint: disable=pointless-statement


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
