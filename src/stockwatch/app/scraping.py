"""Dash app callbacks for importing/scraping data from DeGiro."""
from collections import namedtuple
from datetime import date
from pathlib import Path

import dash
from dash.dependencies import Input, Output, State

from ..use_cases import degiro
from .ids import ScrapingId

_SCRAPE_THREAD = degiro.ScrapeThread()


def _disable_execute(session_id_valid: bool, account_id_valid: bool) -> bool:
    return not session_id_valid or not account_id_valid


def _stop_execution(_n_clicks: int) -> None:
    _SCRAPE_THREAD.stop()


def _execute_scraping(
    _execute_clicks: int,
    session_id: str | None,
    account_id: int | None,
    start_date: str,
    end_date: str,
    folder: str,
) -> bool | dash._callback.NoUpdate:
    if not session_id or not account_id:
        return dash.no_update

    started = _SCRAPE_THREAD.start(
        degiro.PortfolioImportData(
            session_id,
            account_id,
            date.fromisoformat(start_date),
            date.fromisoformat(end_date),
            Path(folder),
        )
    )

    return started


ValidationOutput = namedtuple("ValidationOutput", ["valid", "invalid"])


def _validate_sessionid(sessionid: str | None) -> ValidationOutput:
    if sessionid:
        valid = degiro.is_valid_sessionid(sessionid)
        return ValidationOutput(valid=valid, invalid=not valid)
    return ValidationOutput(False, False)


def _validate_accountid(accountid: int | None) -> ValidationOutput:
    if accountid:
        valid = degiro.is_valid_accountid(accountid)
        return ValidationOutput(valid=valid, invalid=not valid)
    return ValidationOutput(False, False)


def _set_interval(is_open: bool) -> bool:
    return not is_open


def _update_progress_bar(_iter: int) -> int:
    if _SCRAPE_THREAD.finished:
        _SCRAPE_THREAD.clear()
        return 0

    return _SCRAPE_THREAD.progress


def _update_progress_info(_iter: int) -> str:
    if _SCRAPE_THREAD.finished:
        return ""

    return (
        f"Currently processing: {_SCRAPE_THREAD.current_date} - still "
        f"{(_SCRAPE_THREAD.end_date - _SCRAPE_THREAD.current_date).days} "
        f"days to go"
    )


def _update_progress_modal(_iter: int) -> bool | dash._callback.NoUpdate:
    # Close the modal window when the scraping is finished
    return not _SCRAPE_THREAD.finished


def init_app(app: dash.Dash) -> None:
    """Initialize the application with all the scraping callbacks"""
    app.callback(
        Output(ScrapingId.EXECUTE, "disabled"),
        Input(ScrapingId.SESSION_ID, "valid"),
        Input(ScrapingId.ACCOUNT_ID, "valid"),
    )(_disable_execute)

    app.callback(
        Output(ScrapingId.INTERVAL, "disabled"), Input(ScrapingId.MODAL, "is_open")
    )(_set_interval)

    app.callback(
        Output(ScrapingId.MODAL, "is_open"),
        Input(ScrapingId.EXECUTE, "n_clicks"),
        State(ScrapingId.SESSION_ID, "value"),
        State(ScrapingId.ACCOUNT_ID, "value"),
        State(ScrapingId.START_DATE, "date"),
        State(ScrapingId.END_DATE, "date"),
        State(ScrapingId.FOLDER, "value"),
    )(_execute_scraping)

    app.callback(
        Output(ScrapingId.PLACEHOLDER, "n_clicks"), Input(ScrapingId.CLOSE, "n_clicks")
    )(_stop_execution)

    app.callback(
        [
            Output(ScrapingId.SESSION_ID, "valid"),
            Output(ScrapingId.SESSION_ID, "invalid"),
        ],
        Input(ScrapingId.SESSION_ID, "value"),
    )(_validate_sessionid)

    app.callback(
        [
            Output(ScrapingId.ACCOUNT_ID, "valid"),
            Output(ScrapingId.ACCOUNT_ID, "invalid"),
        ],
        Input(ScrapingId.ACCOUNT_ID, "value"),
    )(_validate_accountid)

    app.callback(
        Output(ScrapingId.PROGRESS, "value"), Input(ScrapingId.INTERVAL, "n_intervals")
    )(_update_progress_bar)

    app.callback(
        Output(ScrapingId.CURRENT, "children"),
        Input(ScrapingId.INTERVAL, "n_intervals"),
    )(_update_progress_info)

    app.callback(
        Output(ScrapingId.MODAL, "is_open"), Input(ScrapingId.INTERVAL, "n_intervals")
    )(_update_progress_modal)
