# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import pytest
from stockwatch.entities.currencies import (
    Amount,
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
