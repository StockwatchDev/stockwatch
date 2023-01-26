from datetime import date, timedelta

import pytest

from stockwatch import use_cases
from stockwatch.app import runtime
from stockwatch.entities.shares import SharePortfolio


@pytest.fixture
def example_portfolio_1() -> tuple[SharePortfolio, SharePortfolio, SharePortfolio]:
    return (
        SharePortfolio(portfolio_date=date(2020, 5, 31), share_positions=tuple()),
        SharePortfolio(portfolio_date=date(2021, 5, 31), share_positions=tuple()),
        SharePortfolio(portfolio_date=date(2022, 5, 31), share_positions=tuple()),
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
