# pylint: disable=redefined-outer-name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
from datetime import date, datetime, timedelta
from dataclasses import replace
import pytest
from stockwatch.entities2.currencies import (
    Amount,
)
from stockwatch.entities2.shares import (
    UNKNOWN_POSITION_NAME,
    SharePosition,
    SharePortfolio,
    earliest_portfolio_date,
    latest_portfolio_date,
    closest_portfolio_after_date,
    closest_portfolio_before_date,
    get_all_isins,
    apply_transactions,
    PortfoliosDictionary,
    to_portfolios,
)
from stockwatch.entities2.transactions import (
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


@pytest.fixture
def example_sell_transaction_2() -> ShareTransaction:
    return ShareTransaction(
        transaction_datetime=datetime.today() - timedelta(days=12),
        isin="IE00B3RBWM25",
        nr_stocks=2.0,
        price=Amount(105.25),
        kind=ShareTransactionKind.SELL,
        amount=Amount(2.0 * 105.25),
    )


@pytest.fixture
def example_buy_transaction() -> ShareTransaction:
    return ShareTransaction(
        transaction_datetime=datetime.today() - timedelta(days=7),
        isin="IE00B441G979",
        nr_stocks=16.0,
        price=Amount(64.375),
        kind=ShareTransactionKind.BUY,
        amount=Amount(16.0 * 64.375),
    )


@pytest.fixture
def example_dividend_transaction() -> ShareTransaction:
    return ShareTransaction(
        transaction_datetime=datetime.today() - timedelta(days=7),
        isin="IE00B3RBWM25",
        nr_stocks=1.0,
        price=Amount(13.13),
        kind=ShareTransactionKind.DIVIDEND,
        amount=Amount(1.0 * 13.13),
    )


@pytest.fixture
def example_position_1() -> SharePosition:
    return SharePosition(
        datetime.today().date(),
        Amount(1190.72),
        "IE00B441G979",
        "iShares MSCI World EUR Hedged UCITS ETF",
        Amount(1030.00),
        16,
        Amount(74.42),
        Amount(-10.50),
    )


@pytest.fixture
def example_position_2() -> SharePosition:
    return SharePosition(
        datetime.today().date(),
        Amount(1060.00),
        "IE00B3RBWM25",
        "Vanguard FTSE All-World UCITS ETF USD Dis",
        Amount(970.00),
        10,
        Amount(106.00),
        Amount(23.66),
    )


@pytest.fixture
def example_position_3() -> SharePosition:
    return SharePosition(
        (datetime.today() - timedelta(days=21)).date(),
        Amount(1035),
        "NL0010408704",
        "VanEck Sustainable World Equal Weight UCITS ETF",
        Amount(1000.08),
        36,
        Amount(28.75),
        Amount(86.50),
    )


@pytest.fixture
def example_pfdict_today() -> PortfoliosDictionary:
    sp1 = SharePosition(
        date.today(),
        Amount(0.0),
        "NL0010408704",
        "VanEck Sustainable World Equal Weight UCITS ETF",
        Amount(1000.08),
        0,
        Amount(1.0),
        Amount(86.50),
    )
    sp2 = SharePosition(
        date.today(),
        Amount(1190.72),
        "IE00B441G979",
        "iShares MSCI World EUR Hedged UCITS ETF",
        Amount(1030.00),
        16,
        Amount(74.42),
        Amount(-10.50),
    )
    sp3 = SharePosition(
        date.today(),
        Amount(1060.00),
        "IE00B3RBWM25",
        "Vanguard FTSE All-World UCITS ETF USD Dis",
        Amount(970.00),
        10,
        Amount(106.00),
        Amount(23.66),
    )
    return {date.today(): {sp1.isin: sp1, sp2.isin: sp2, sp3.isin: sp3}}


@pytest.fixture
def example_pfdict_3w_ago() -> PortfoliosDictionary:
    the_date = date.today() - timedelta(days=21)
    sp1 = SharePosition(
        the_date,
        Amount(1035.0),
        "NL0010408704",
        "VanEck Sustainable World Equal Weight UCITS ETF",
        Amount(1000.08),
        36,
        Amount(28.75),
        Amount(86.50),
    )
    sp2 = SharePosition(
        the_date,
        Amount(0.0),
        "IE00B441G979",
        "iShares MSCI World EUR Hedged UCITS ETF",
        Amount(0.0),
        0,
        Amount(1.0),
        Amount(-10.50),
    )
    sp3 = SharePosition(
        the_date,
        Amount(1250.76),
        "IE00B3RBWM25",
        "Vanguard FTSE All-World UCITS ETF USD Dis",
        Amount(970.00),
        12,
        Amount(106.00),
        Amount(23.66),
    )
    return {the_date: {sp1.isin: sp1, sp2.isin: sp2, sp3.isin: sp3}}


def test_position_order(
    example_position_1: SharePortfolio,
    example_position_2: SharePortfolio,
    example_position_3: SharePortfolio,
) -> None:
    assert example_position_1 > example_position_2
    assert example_position_3 < example_position_2


def test_value(example_pfdict_3w_ago: PortfoliosDictionary) -> None:
    spf = to_portfolios(example_pfdict_3w_ago)[0]
    assert spf.get_position("NL0010408704").value == 1035.0
    assert spf.value == 2285.76


def test_investment(example_pfdict_3w_ago: PortfoliosDictionary) -> None:
    spf = to_portfolios(example_pfdict_3w_ago)[0]
    assert spf.get_position("NL0010408704").investment == 1000.08
    assert spf.investment == 1970.08


def test_contains_get_position(example_pfdict_3w_ago: PortfoliosDictionary) -> None:
    spf = to_portfolios(example_pfdict_3w_ago)[0]
    non_existing_isin = "IE00B02KXL92"
    assert not spf.contains(non_existing_isin)
    assert spf.get_position(non_existing_isin).name == UNKNOWN_POSITION_NAME
    assert spf.get_position("IE00B441G979").isin == "IE00B441G979"


def test_realized_return(example_pfdict_3w_ago: PortfoliosDictionary) -> None:
    spf = to_portfolios(example_pfdict_3w_ago)[0]
    non_existing_isin = "IE00B02KXL92"
    assert spf.get_position(non_existing_isin).realized == 0.0
    assert spf.get_position("IE00B441G979").realized == -10.50
    assert spf.realized == 99.66


def test_unrealized_return(example_pfdict_3w_ago: PortfoliosDictionary) -> None:
    spf = to_portfolios(example_pfdict_3w_ago)[0]
    non_existing_isin = "IE00B02KXL92"
    assert spf.get_position(non_existing_isin).unrealized == 0.0
    assert spf.get_position("IE00B3RBWM25").unrealized == 280.76
    assert spf.unrealized == 315.68


def test_total_return(example_pfdict_3w_ago: PortfoliosDictionary) -> None:
    spf = to_portfolios(example_pfdict_3w_ago)[0]
    non_existing_isin = "IE00B02KXL92"
    assert spf.get_position(non_existing_isin).total_return == 0.0
    assert spf.get_position("IE00B3RBWM25").total_return == 304.42
    assert spf.total_return == 415.34


def test_isins_names(example_pfdict_3w_ago: PortfoliosDictionary) -> None:
    spf = to_portfolios(example_pfdict_3w_ago)[0]
    all_isins = spf.all_isins()
    all_isins_and_names = spf.all_isins_and_names()
    assert len(all_isins) == 3
    assert len(all_isins_and_names) == 3
    assert "IE00B441G979" in all_isins
    assert "IE00B3RBWM25" in all_isins
    assert (
        all_isins_and_names["IE00B441G979"] == "iShares MSCI World EUR Hedged UCITS ETF"
    )


def test_is_date_consistent(example_pfdict_3w_ago: PortfoliosDictionary) -> None:
    spf = to_portfolios(example_pfdict_3w_ago)[0]
    assert spf.is_date_consistent()


def test_portfolio_order(
    example_pfdict_3w_ago: PortfoliosDictionary,
    example_pfdict_today: PortfoliosDictionary,
) -> None:
    spf_3w = to_portfolios(example_pfdict_3w_ago)[0]
    spf_td = to_portfolios(example_pfdict_today)[0]
    assert spf_3w < spf_td


def test_earliest_latest_date(
    example_pfdict_3w_ago: PortfoliosDictionary,
    example_pfdict_today: PortfoliosDictionary,
) -> None:
    spfs = to_portfolios(example_pfdict_3w_ago | example_pfdict_today)
    assert earliest_portfolio_date(spfs) in example_pfdict_3w_ago
    assert latest_portfolio_date(spfs) in example_pfdict_today


def test_closest_portfolio(
    example_pfdict_3w_ago: PortfoliosDictionary,
    example_pfdict_today: PortfoliosDictionary,
) -> None:
    combined_pf_dict = example_pfdict_3w_ago | example_pfdict_today
    spfs = to_portfolios(combined_pf_dict)
    earliest_date = min(combined_pf_dict.keys())
    latest_date = max(combined_pf_dict.keys())
    assert closest_portfolio_after_date(spfs, latest_date + timedelta(days=1)) is None
    assert (
        closest_portfolio_after_date(spfs, latest_date - timedelta(days=1)) == spfs[1]
    )
    assert (
        closest_portfolio_before_date(spfs, latest_date + timedelta(days=1)) == spfs[1]
    )
    assert (
        closest_portfolio_before_date(spfs, earliest_date + timedelta(days=1))
        == spfs[0]
    )
    assert (
        closest_portfolio_before_date(spfs, earliest_date - timedelta(days=1)) is None
    )


def test_get_all_isins(
    example_pfdict_3w_ago: PortfoliosDictionary,
    example_pfdict_today: PortfoliosDictionary,
) -> None:
    spfs = to_portfolios(example_pfdict_3w_ago | example_pfdict_today)
    all_isins = get_all_isins(spfs)
    assert len(all_isins) == 3
    assert "NL0010408704" in all_isins
    assert "IE00B441G979" in all_isins
    assert "IE00B3RBWM25" in all_isins


def test_sell_and_buy_transaction(
    example_pfdict_today: PortfoliosDictionary,
    example_pfdict_3w_ago: PortfoliosDictionary,
    example_sell_transaction_1: ShareTransaction,
    example_sell_transaction_2: ShareTransaction,
    example_buy_transaction: ShareTransaction,
) -> None:
    portfolios = example_pfdict_3w_ago | example_pfdict_today
    transactions = (
        example_sell_transaction_1,
        example_sell_transaction_2,
        example_buy_transaction,
    )
    date_after = list(example_pfdict_today.keys())[0]
    isin_sell_1 = example_sell_transaction_1.isin
    isin_sell_2 = example_sell_transaction_2.isin
    isin_buy = example_buy_transaction.isin
    apply_transactions(transactions, portfolios)
    assert portfolios[date_after][isin_sell_1].investment == 0.0
    assert portfolios[date_after][isin_sell_1].realized == 122.86
    assert portfolios[date_after][isin_buy].investment == 2060.0
    assert portfolios[date_after][isin_sell_2].investment == 808.33
    assert portfolios[date_after][isin_sell_2].realized == 72.49

    # and test the degenerate cases, that they do not raise an exception
    example_sell_transaction_1 = replace(
        example_sell_transaction_1,
        transaction_datetime=datetime.today() - timedelta(days=50),
    )
    apply_transactions(
        (example_sell_transaction_1,), portfolios
    )  # no portfolio present before transaction date
    example_sell_transaction_1 = replace(
        example_sell_transaction_1,
        isin="IE00B441G979",
        transaction_datetime=datetime.today() - timedelta(days=9),
    )
    apply_transactions(
        (example_sell_transaction_1,), portfolios
    )  # position not present in last portfolio
    example_buy_transaction = replace(
        example_buy_transaction,
        transaction_datetime=datetime.today() + timedelta(days=50),
    )
    apply_transactions(
        (example_buy_transaction,), portfolios
    )  # no portfolio present after transaction date
    example_buy_transaction = replace(
        example_buy_transaction,
        isin="IE00B02KXL92",
        transaction_datetime=datetime.today() - timedelta(days=3),
    )
    apply_transactions(
        (example_buy_transaction,), portfolios
    )  # no position present after transaction date
    apply_transactions((), portfolios)  # empty transactions tuple


def test_double_buy_transaction(
    example_pfdict_today: SharePortfolio,
    example_pfdict_3w_ago: SharePortfolio,
    example_buy_transaction: ShareTransaction,
) -> None:
    portfolios = example_pfdict_3w_ago | example_pfdict_today
    example_buy_transaction_half_1 = replace(example_buy_transaction, nr_stocks=8.0)
    example_buy_transaction_half_2 = replace(example_buy_transaction, nr_stocks=8.0)
    transactions = (
        example_buy_transaction_half_1,
        example_buy_transaction_half_2,
    )
    date_after = list(example_pfdict_today.keys())[0]
    isin_buy = example_buy_transaction.isin
    apply_transactions(transactions, portfolios)
    assert portfolios[date_after][isin_buy].investment == 2060.0


def test_double_sell_transaction(
    example_pfdict_today: SharePortfolio,
    example_pfdict_3w_ago: SharePortfolio,
    example_sell_transaction_1: ShareTransaction,
) -> None:
    portfolios = example_pfdict_3w_ago | example_pfdict_today
    example_sell_transaction_1_half_1 = replace(
        example_sell_transaction_1, nr_stocks=18.0
    )
    example_sell_transaction_1_half_2 = replace(
        example_sell_transaction_1, nr_stocks=18.0
    )
    transactions = (
        example_sell_transaction_1_half_1,
        example_sell_transaction_1_half_2,
    )
    date_after = list(example_pfdict_today.keys())[0]
    isin_sell = example_sell_transaction_1.isin
    apply_transactions(transactions, portfolios)
    assert portfolios[date_after][isin_sell].investment == 0.0
    assert portfolios[date_after][isin_sell].realized == 122.86


def test_dividend_transaction(
    example_pfdict_today: SharePortfolio,
    example_pfdict_3w_ago: SharePortfolio,
    example_dividend_transaction: ShareTransaction,
) -> None:
    portfolios = example_pfdict_3w_ago | example_pfdict_today
    transactions = (example_dividend_transaction,)
    date_after = list(example_pfdict_today.keys())[0]
    isin_div = example_dividend_transaction.isin
    apply_transactions(transactions, portfolios)
    assert portfolios[date_after][isin_div].investment == 970.0
    assert portfolios[date_after][isin_div].realized == 36.79

    # and test the degenerate cases, that they do not raise an exception
    example_dividend_transaction = replace(
        example_dividend_transaction,
        transaction_datetime=datetime.today() - timedelta(days=50),
    )
    apply_transactions((example_dividend_transaction,), portfolios)
    example_dividend_transaction = replace(
        example_dividend_transaction,
        isin="IE00B02KXL92",
        transaction_datetime=datetime.today() - timedelta(days=9),
    )
    apply_transactions((example_dividend_transaction,), portfolios)
