# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import pytest
from datetime import date, datetime, timedelta
from stockwatch.entities.money import (
    Amount,
)
from stockwatch.entities.transactions import (
    ShareTransactionKind,
    ShareTransaction,
)


@pytest.fixture
def example_sell_transaction_1() -> ShareTransaction:
    return ShareTransaction(
        transaction_datetime=datetime.today() - timedelta(days=9),
        isin="NL0010408704",
        nr_stocks=36.0,
        price=Amount(28.79),
        kind=ShareTransactionKind.SELL,
        amount=Amount(36.0 * 28.79),
    )


def test_transaction_date(
    example_sell_transaction_1: ShareTransaction,
) -> None:
    assert example_sell_transaction_1.transaction_date == date.today() - timedelta(
        days=9
    )
