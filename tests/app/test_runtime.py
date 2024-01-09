from datetime import date, timedelta

import pytest

from stockwatch import use_cases
from stockwatch.app import runtime
from stockwatch.entities.money import Amount
from stockwatch.entities.shares import SharePortfolio, SharePosition


@pytest.fixture
def example_position_1() -> SharePosition:
    return SharePosition(
        date.today() - timedelta(days=21),
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
        date.today() - timedelta(days=10),
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
        date.today() - timedelta(days=2),
        Amount(1035),
        "NL0010408704",
        "VanEck Sustainable World Equal Weight UCITS ETF",
        Amount(1000.08),
        36,
        Amount(28.75),
        Amount(86.50),
    )


@pytest.fixture
def example_portfolio_1(
    example_position_1: SharePortfolio,
    example_position_2: SharePortfolio,
    example_position_3: SharePortfolio,
) -> tuple[SharePortfolio, SharePortfolio, SharePortfolio]:
    return (
        SharePortfolio(share_positions=(example_position_1,)),
        SharePortfolio(share_positions=(example_position_2,)),
        SharePortfolio(share_positions=(example_position_3,)),
    )


@pytest.fixture(autouse=True)
def run_around_tests():
    # Any code before the tests
    yield
    # Clear any set portfolios
    runtime.clear()


def test_get_default_dates() -> None:
    # No portos loaded default date
    assert runtime.get_startdate() == date(2020, 1, 1)
    assert runtime.get_enddate() == date.today()


def test_get_dates(
    monkeypatch, example_portfolio_1: tuple[SharePortfolio, ...]
) -> None:
    monkeypatch.setattr(
        use_cases,
        "get_portfolios_index_positions",
        lambda: (example_portfolio_1, tuple()),
    )
    runtime.load_portfolios()
    assert runtime.get_startdate() == example_portfolio_1[0].portfolio_date
    assert runtime.get_enddate() == example_portfolio_1[-1].portfolio_date


def test_get_date_filtered_portfolios(
    monkeypatch, example_portfolio_1: tuple[SharePortfolio, ...]
) -> None:
    monkeypatch.setattr(
        use_cases,
        "get_portfolios_index_positions",
        lambda: (example_portfolio_1, tuple()),
    )

    assert runtime.get_date_filtered_portfolios(None, None) == tuple()

    runtime.load_portfolios()

    assert runtime.get_date_filtered_portfolios(None, None) == example_portfolio_1
    # We can filter out the first portfolio
    start_date = example_portfolio_1[0].portfolio_date + timedelta(days=1)
    assert (
        runtime.get_date_filtered_portfolios(start_date, None)
        == example_portfolio_1[1:]
    )

    # And also the last portfolio
    end_date = example_portfolio_1[-1].portfolio_date - timedelta(days=1)
    assert (
        runtime.get_date_filtered_portfolios(start_date, end_date)
        == example_portfolio_1[1:-1]
    )
