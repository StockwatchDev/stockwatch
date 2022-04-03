# pylint: skip-file
from datetime import date, timedelta
import pytest
from stockwatch.entities import (
    SharePosition,
    SharePortfolio,
    closest_portfolio_after_date,
    closest_portfolio_before_date,
    get_all_isins,
)


@pytest.fixture
def example_portfolio_1() -> SharePortfolio:
    sp1 = SharePosition(
        "iShares MSCI World EUR Hedged UCITS ETF",
        "IE00B441G979",
        "EUR",
        1030.00,
        16,
        74.42,
        1190.72,
        -10.50,
        date.today(),
    )
    sp2 = SharePosition(
        "Vanguard FTSE All-World UCITS ETF USD Dis",
        "IE00B3RBWM25",
        "EUR",
        970.00,
        10,
        106.00,
        1060.00,
        23.66,
        date.today(),
    )
    return SharePortfolio((sp1, sp2), date.today())


@pytest.fixture
def example_portfolio_2() -> SharePortfolio:
    sp1 = SharePosition(
        "VanEck Sustainable World Equal Weight UCITS ETF",
        "NL0010408704",
        "EUR",
        1000.00,
        36,
        28.76,
        1035,
        86.50,
        date.today() - timedelta(days=21),
    )
    sp2 = SharePosition(
        "Vanguard FTSE All-World UCITS ETF USD Dis",
        "IE00B3RBWM25",
        "EUR",
        970.00,
        10,
        104.23,
        1042.30,
        23.66,
        date.today() - timedelta(days=21),
    )
    return SharePortfolio((sp1, sp2), date.today() - timedelta(days=21))


def test_value(example_portfolio_1: SharePortfolio) -> None:
    assert example_portfolio_1.value_of("IE00B441G979") == 1190.72
    assert example_portfolio_1.total_value == 2250.72


def test_investment(example_portfolio_1: SharePortfolio) -> None:
    assert example_portfolio_1.investment_of("IE00B441G979") == 1030.00
    assert example_portfolio_1.total_investment == 2000.0


def test_contains_get_position(example_portfolio_1: SharePortfolio) -> None:
    assert not example_portfolio_1.contains("IE00B02KXL92")
    assert example_portfolio_1.get_position("IE00B02KXL92") == None
    assert example_portfolio_1.get_position("IE00B441G979").isin == "IE00B441G979"


def test_realized_return(example_portfolio_1: SharePortfolio) -> None:
    assert example_portfolio_1.realized_return_of("IE00B441G979") == -10.50
    assert example_portfolio_1.total_realized_return == 13.16


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


def test_closest_portfolio(
    example_portfolio_1: SharePortfolio, example_portfolio_2: SharePortfolio
) -> None:
    portfolio_set = (example_portfolio_2, example_portfolio_1)
    assert (
        closest_portfolio_after_date(portfolio_set, date.today() + timedelta(days=1))
        == None
    )
    assert (
        closest_portfolio_after_date(portfolio_set, date.today() - timedelta(days=1))
        == example_portfolio_1
    )
    assert (
        closest_portfolio_before_date(portfolio_set, date.today() + timedelta(days=1))
        == example_portfolio_1
    )
    assert (
        closest_portfolio_before_date(portfolio_set, date.today() - timedelta(days=1))
        == example_portfolio_2
    )
    assert (
        closest_portfolio_before_date(portfolio_set, date.today() - timedelta(days=50))
        == None
    )


def test_get_all_isins(
    example_portfolio_1: SharePortfolio, example_portfolio_2: SharePortfolio
) -> None:
    portfolio_set = (example_portfolio_2, example_portfolio_1)
    all_isins = get_all_isins(portfolio_set)
    assert len(all_isins) == 3
    assert "NL0010408704" in all_isins
    assert "IE00B441G979" in all_isins
    assert "IE00B3RBWM25" in all_isins
