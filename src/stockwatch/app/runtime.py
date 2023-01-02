"""Runtime data used for displaying the Stockwatch site."""
from datetime import date

from stockwatch import entities, use_cases

_SCRAPE_THREAD = use_cases.degiro.ScrapeThread()
_PORTOS: tuple[entities.shares.SharePortfolio, ...] = ()
_INDICES: list[tuple[entities.shares.SharePosition, ...]] = []


def load_portfolios() -> None:
    """Load portfolios from the stockwatch dir"""
    global _PORTOS  # pylint: disable=global-statement
    global _INDICES  # pylint: disable=global-statement
    _PORTOS, _INDICES = use_cases.get_portfolios_index_positions()


def get_portfolios(
    start_date: date | None, end_date: date | None
) -> tuple[entities.shares.SharePortfolio, ...]:
    """Get the portfolios, filtered by the start and end date."""
    start_idx = 0
    end_idx = -1

    if start_date:
        for idx, portfolio in enumerate(_PORTOS):
            if portfolio.portfolio_date >= start_date:
                start_idx = idx
                break

    if end_date:
        for idx, portfolio in enumerate(_PORTOS):
            if portfolio.portfolio_date >= end_date:
                end_idx = idx
                break

    return _PORTOS[start_idx:end_idx]


def get_startdate() -> date:
    """Get the start date of the currently loaded portfolios."""
    if _PORTOS:
        return _PORTOS[0].portfolio_date
    return date(year=2020, month=1, day=1)


def get_enddate() -> date:
    """Get the end date of the currently loaded portfolios."""
    if _PORTOS:
        return _PORTOS[-1].portfolio_date
    return date.today()


def get_scrape_thread() -> use_cases.degiro.ScrapeThread:
    """Get the singleton scrape thread."""
    return _SCRAPE_THREAD
