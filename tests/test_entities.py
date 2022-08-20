# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
from datetime import date, timedelta
from dataclasses import replace
import pytest
from stockwatch.entities import (
    EMPTY_POSITION_NAME,
    SharePosition,
    SharePortfolio,
    ShareTransactionKind,
    ShareTransaction,
    earliest_portfolio_date,
    latest_portfolio_date,
    closest_portfolio_after_date,
    closest_portfolio_before_date,
    get_all_isins,
    apply_transactions,
)


@pytest.fixture
def example_sell_transaction_1() -> ShareTransaction:
    return ShareTransaction(
        kind=ShareTransactionKind.SELL,
        isin="NL0010408704",
        curr="EUR",
        nr_stocks=36.0,
        price=28.79,
        transaction_date=date.today() - timedelta(days=9),
    )


@pytest.fixture
def example_sell_transaction_2() -> ShareTransaction:
    return ShareTransaction(
        kind=ShareTransactionKind.SELL,
        isin="IE00B3RBWM25",
        curr="EUR",
        nr_stocks=2.0,
        price=105.25,
        transaction_date=date.today() - timedelta(days=12),
    )


@pytest.fixture
def example_buy_transaction() -> ShareTransaction:
    return ShareTransaction(
        kind=ShareTransactionKind.BUY,
        isin="IE00B441G979",
        curr="EUR",
        nr_stocks=16.0,
        price=64.375,
        transaction_date=date.today() - timedelta(days=7),
    )


@pytest.fixture
def example_dividend_transaction() -> ShareTransaction:
    return ShareTransaction(
        kind=ShareTransactionKind.DIVIDEND,
        isin="IE00B3RBWM25",
        curr="EUR",
        nr_stocks=1.0,
        price=13.13,
        transaction_date=date.today() - timedelta(days=7),
    )


@pytest.fixture
def example_position_1() -> SharePosition:
    return SharePosition(
        date.today(),
        1190.72,
        "iShares MSCI World EUR Hedged UCITS ETF",
        "IE00B441G979",
        "EUR",
        1030.00,
        16,
        74.42,
        -10.50,
    )


@pytest.fixture
def example_position_2() -> SharePosition:
    return SharePosition(
        date.today(),
        1060.00,
        "Vanguard FTSE All-World UCITS ETF USD Dis",
        "IE00B3RBWM25",
        "EUR",
        970.00,
        10,
        106.00,
        23.66,
    )


@pytest.fixture
def example_position_3() -> SharePosition:
    return SharePosition(
        date.today() - timedelta(days=21),
        1035,
        "VanhEck Sustainable World Equal Weight UCITS ETF",
        "NL0010408704",
        "EUR",
        1000.08,
        36,
        28.75,
        86.50,
    )


@pytest.fixture
def example_portfolio_1() -> SharePortfolio:
    sp1 = SharePosition(
        date.today(),
        1190.72,
        "iShares MSCI World EUR Hedged UCITS ETF",
        "IE00B441G979",
        "EUR",
        1030.00,
        16,
        74.42,
        -10.50,
    )
    sp2 = SharePosition(
        date.today(),
        1060.00,
        "Vanguard FTSE All-World UCITS ETF USD Dis",
        "IE00B3RBWM25",
        "EUR",
        970.00,
        10,
        106.00,
        23.66,
    )
    return SharePortfolio(date.today(), {sp1.isin: sp1, sp2.isin: sp2})


@pytest.fixture
def example_portfolio_2() -> SharePortfolio:
    sp1 = SharePosition(
        date.today() - timedelta(days=21),
        1035,
        "VanEck Sustainable World Equal Weight UCITS ETF",
        "NL0010408704",
        "EUR",
        1000.08,
        36,
        28.75,
        86.50,
    )
    sp2 = SharePosition(
        date.today() - timedelta(days=21),
        1250.76,
        "Vanguard FTSE All-World UCITS ETF USD Dis",
        "IE00B3RBWM25",
        "EUR",
        970.00,
        12,
        104.23,
        23.66,
    )
    return SharePortfolio(
        date.today() - timedelta(days=21), {sp1.isin: sp1, sp2.isin: sp2}
    )


def test_position_order(
    example_position_1: SharePortfolio,
    example_position_2: SharePortfolio,
    example_position_3: SharePortfolio,
) -> None:
    assert example_position_1 > example_position_2
    assert example_position_3 < example_position_2


def test_value(example_portfolio_1: SharePortfolio) -> None:
    assert example_portfolio_1.get_position("IE00B441G979").value == 1190.72
    # assert example_portfolio_1.total_value == 2250.72


def test_investment(example_portfolio_1: SharePortfolio) -> None:
    assert example_portfolio_1.get_position("IE00B441G979").investment == 1030.00
    assert example_portfolio_1.total_investment == 2000.00


def test_contains_get_position(example_portfolio_1: SharePortfolio) -> None:
    non_existing_isin = "IE00B02KXL92"
    assert not example_portfolio_1.contains(non_existing_isin)
    assert (
        example_portfolio_1.get_position(non_existing_isin).name == EMPTY_POSITION_NAME
    )
    assert example_portfolio_1.get_position("IE00B441G979").isin == "IE00B441G979"


def test_realized_return(example_portfolio_1: SharePortfolio) -> None:
    non_existing_isin = "IE00B02KXL92"
    assert example_portfolio_1.get_position(non_existing_isin).realized == 0.0
    assert example_portfolio_1.get_position("IE00B441G979").realized == -10.50
    assert example_portfolio_1.total_realized_return == 13.16


def test_unrealized_return(example_portfolio_1: SharePortfolio) -> None:
    non_existing_isin = "IE00B02KXL92"
    assert example_portfolio_1.get_position(non_existing_isin).unrealized == 0.0
    assert example_portfolio_1.get_position("IE00B441G979").unrealized == 160.72
    assert example_portfolio_1.total_unrealized_return == 250.72


def test_total_return(example_portfolio_1: SharePortfolio) -> None:
    non_existing_isin = "IE00B02KXL92"
    assert example_portfolio_1.get_position(non_existing_isin).total_return == 0.0
    assert (
        example_portfolio_1.get_position("IE00B441G979").total_return == 160.72 - 10.50
    )
    assert example_portfolio_1.total_return == 250.72 + 13.16


def test_isins_names(example_portfolio_1: SharePortfolio) -> None:
    all_isins = example_portfolio_1.all_isins()
    all_isins_and_names = example_portfolio_1.all_isins_and_names()
    assert len(all_isins) == 2
    assert len(all_isins_and_names) == 2
    assert "IE00B441G979" in all_isins
    assert "IE00B3RBWM25" in all_isins
    assert (
        all_isins_and_names["IE00B441G979"] == "iShares MSCI World EUR Hedged UCITS ETF"
    )


def test_is_date_consistent(example_portfolio_1: SharePortfolio) -> None:
    assert example_portfolio_1.is_date_consistent()


def test_portfolio_order(
    example_portfolio_1: SharePortfolio, example_portfolio_2: SharePortfolio
) -> None:
    assert example_portfolio_2 < example_portfolio_1


def test_earliest_latest_date(
    example_portfolio_1: SharePortfolio, example_portfolio_2: SharePortfolio
) -> None:
    portfolios = (example_portfolio_2, example_portfolio_1)
    assert earliest_portfolio_date(portfolios) == example_portfolio_2.portfolio_date
    assert latest_portfolio_date(portfolios) == example_portfolio_1.portfolio_date


def test_closest_portfolio(
    example_portfolio_1: SharePortfolio, example_portfolio_2: SharePortfolio
) -> None:
    portfolios = (example_portfolio_2, example_portfolio_1)
    earliest_date = earliest_portfolio_date(portfolios)
    latest_date = latest_portfolio_date(portfolios)
    assert (
        closest_portfolio_after_date(portfolios, latest_date + timedelta(days=1))
        is None
    )
    assert (
        closest_portfolio_after_date(portfolios, latest_date - timedelta(days=1))
        == example_portfolio_1
    )
    assert (
        closest_portfolio_before_date(portfolios, latest_date + timedelta(days=1))
        == example_portfolio_1
    )
    assert (
        closest_portfolio_before_date(portfolios, earliest_date + timedelta(days=1))
        == example_portfolio_2
    )
    assert (
        closest_portfolio_before_date(portfolios, earliest_date - timedelta(days=1))
        is None
    )


def test_get_all_isins(
    example_portfolio_1: SharePortfolio, example_portfolio_2: SharePortfolio
) -> None:
    portfolios = (example_portfolio_2, example_portfolio_1)
    all_isins = get_all_isins(portfolios)
    assert len(all_isins) == 3
    assert "NL0010408704" in all_isins
    assert "IE00B441G979" in all_isins
    assert "IE00B3RBWM25" in all_isins


def test_sell_and_buy_transaction(
    example_portfolio_1: SharePortfolio,
    example_portfolio_2: SharePortfolio,
    example_sell_transaction_1: ShareTransaction,
    example_sell_transaction_2: ShareTransaction,
    example_buy_transaction: ShareTransaction,
) -> None:
    portfolios = (example_portfolio_2, example_portfolio_1)
    transactions = (
        example_sell_transaction_1,
        example_sell_transaction_2,
        example_buy_transaction,
    )
    apply_transactions(transactions, portfolios)
    assert portfolios[1].get_position(example_sell_transaction_1.isin).investment == 0.0
    assert (
        portfolios[1].get_position(example_sell_transaction_1.isin).realized == 122.86
    )
    assert portfolios[1].get_position(example_buy_transaction.isin).investment == 2060.0
    assert (
        portfolios[1].get_position(example_sell_transaction_2.isin).investment == 808.33
    )
    assert portfolios[1].get_position(example_sell_transaction_2.isin).realized == 72.49

    # and test the degenerate cases, that they do not raise an exception
    example_sell_transaction_1 = replace(
        example_sell_transaction_1, transaction_date=date.today() - timedelta(days=50)
    )
    apply_transactions(
        (example_sell_transaction_1,), portfolios
    )  # no portfolio present before transaction date
    example_sell_transaction_1 = replace(
        example_sell_transaction_1,
        isin="IE00B441G979",
        transaction_date=date.today() - timedelta(days=9),
    )
    apply_transactions(
        (example_sell_transaction_1,), portfolios
    )  # position not present in last portfolio
    example_buy_transaction = replace(
        example_buy_transaction, transaction_date=date.today() + timedelta(days=50)
    )
    apply_transactions(
        (example_buy_transaction,), portfolios
    )  # no portfolio present after transaction date
    example_buy_transaction = replace(
        example_buy_transaction,
        isin="IE00B02KXL92",
        transaction_date=date.today() - timedelta(days=3),
    )
    apply_transactions(
        (example_buy_transaction,), portfolios
    )  # no position present after transaction date


def test_dividend_transaction(
    example_portfolio_1: SharePortfolio,
    example_portfolio_2: SharePortfolio,
    example_dividend_transaction: ShareTransaction,
) -> None:
    portfolios = (example_portfolio_2, example_portfolio_1)
    transactions = (example_dividend_transaction,)
    apply_transactions(transactions, portfolios)
    assert (
        portfolios[1].get_position(example_dividend_transaction.isin).investment
        == 970.0
    )
    assert (
        portfolios[1].get_position(example_dividend_transaction.isin).realized == 36.79
    )

    # and test the degenerate cases, that they do not raise an exception
    example_dividend_transaction = replace(
        example_dividend_transaction, transaction_date=date.today() - timedelta(days=50)
    )
    apply_transactions((example_dividend_transaction,), portfolios)
    example_dividend_transaction = replace(
        example_dividend_transaction,
        isin="IE00B02KXL92",
        transaction_date=date.today() - timedelta(days=9),
    )
    apply_transactions((example_dividend_transaction,), portfolios)
