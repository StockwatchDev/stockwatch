"""Dash app callbacks for importing/scraping data from DeGiro."""
import threading
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import dash
from dash.dependencies import Input, Output, State

from ..scraping import process_date
from .ids import ScrapingId


@dataclass(frozen=True)
class PortfolioData:
    """The input data to obtain the portfolio csv files."""

    session_id: str = ""
    account_id: int = 0
    start_date: date = date.today()
    end_date: date = date.today()
    folder: Path = Path()


class _ImportFiles:
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._data = PortfolioData()
        self._current_date: date = date.today()
        self._stop = False

    def start(self, data: PortfolioData) -> bool:
        """Start obtaining data from DeGiro"""
        if self._thread:
            return False
        self._data = data

        self._stop = False
        self._thread = threading.Thread(target=self._process)
        self._thread.start()
        return True

    def stop(self) -> None:
        """Stop the currently running execution."""
        self._stop = True

    def clear(self) -> None:
        """Clear the scraping thread."""
        self._stop = True
        self._thread = None
        self._current_date = self._data.end_date

    @property
    def created(self) -> bool:
        """Return True if the process is running."""
        return self._thread is not None

    @property
    def finished(self) -> bool:
        """Return True if the process has finished."""
        return self._stop or self._current_date == self._data.end_date

    @property
    def progress(self) -> int:
        """Return the current progress as a percentage."""
        if not self.created:
            return 0
        part = (self._current_date - self._data.start_date).days
        whole = (self._data.end_date - self._data.start_date).days

        return int(part / whole * 100)

    @property
    def current_date(self) -> date:
        """Get the currently processing scrape date."""
        return self._current_date

    @property
    def end_date(self) -> date:
        """Get the end date."""
        return self._data.end_date

    def _process(self) -> None:
        self._current_date = self._data.start_date
        while self._current_date < self._data.end_date:
            if self._stop:
                break

            try:
                process_date(
                    self._current_date,
                    self._data.account_id,
                    self._data.session_id,
                    self._data.folder,
                )
            except RuntimeError as ex:
                print(f"Error: {ex}")
                self._current_date = self._data.end_date
                break

            self._current_date += timedelta(days=1)


_SCRAPE_THREAD = _ImportFiles()


def _disable_execute(session_id_valid: bool, account_id_valid: bool) -> bool:
    return not session_id_valid or not account_id_valid


def _update_progress(_iter: int) -> tuple[bool, int, str, str]:
    if _SCRAPE_THREAD.finished:
        _SCRAPE_THREAD.clear()
        return False, 0, "", ""

    return (
        True,
        _SCRAPE_THREAD.progress,
        "" if _SCRAPE_THREAD.progress < 5 else f"{_SCRAPE_THREAD.progress}%",
        f"Currently processing: {_SCRAPE_THREAD.current_date} - "
        f"still {(_SCRAPE_THREAD.end_date - _SCRAPE_THREAD.current_date).days} "
        f"days to go",
    )


def _stop_execution(_n_clicks: int) -> None:
    _SCRAPE_THREAD.stop()


def _execute_scraping(
    _execute_clicks: int,
    session_id: str | None,
    account_id: int | None,
    start_date: str,
    end_date: str,
    folder: str,
) -> bool:
    if not session_id or not account_id:
        return False

    started = _SCRAPE_THREAD.start(
        PortfolioData(
            session_id,
            account_id,
            date.fromisoformat(start_date),
            date.fromisoformat(end_date),
            Path(folder) / "portfolio",
        )
    )

    return started


def _validate_sessionid(sessionid: str | None) -> tuple[bool, bool]:
    if sessionid:
        if sessionid.endswith(".prod_b_112_1"):
            return True, False
        return False, True

    return False, False


def _validate_accountid(accountid: int | None) -> tuple[bool, bool]:
    if accountid:
        if accountid > 0:
            return True, False
        return False, True
    return False, False


def _set_interval(is_open: bool) -> bool:
    return not is_open


def init_app(app: dash.Dash) -> None:
    """Initialize the application with all the scraping callbacks"""
    app.callback(
        Output(ScrapingId.EXECUTE, "disabled"),
        Input(ScrapingId.SESSION_ID, "valid"),
        Input(ScrapingId.ACCOUNT_ID, "valid"),
        prevent_initial_callback=True,
    )(_disable_execute)

    app.callback(
        [
            Output(ScrapingId.MODAL, "is_open"),
            Output(ScrapingId.PROGRESS, "value"),
            Output(ScrapingId.PROGRESS, "label"),
            Output(ScrapingId.CURRENT, "children"),
        ],
        Input(ScrapingId.INTERVAL, "n_intervals"),
        prevent_initial_callback=True,
    )(_update_progress)

    app.callback(
        Output(ScrapingId.INTERVAL, "disabled"),
        Input(ScrapingId.MODAL, "is_open"),
        prevent_initial_callback=True,
    )(_set_interval)

    app.callback(
        Output(ScrapingId.MODAL, "is_open"),
        Input(ScrapingId.EXECUTE, "n_clicks"),
        State(ScrapingId.SESSION_ID, "value"),
        State(ScrapingId.ACCOUNT_ID, "value"),
        State(ScrapingId.START_DATE, "date"),
        State(ScrapingId.END_DATE, "date"),
        State(ScrapingId.FOLDER, "value"),
        prevent_initial_callback=True,
    )(_execute_scraping)

    app.callback(
        Output(ScrapingId.PLACEHOLDER, "n_clicks"),
        Input(ScrapingId.CLOSE, "n_clicks"),
        prevent_initial_callback=True,
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
