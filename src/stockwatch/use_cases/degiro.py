"""The use cases related to getting data from the DeGiro website."""
import threading
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import requests

from . import stockdir


def get_portfolio_at(day: date, account: int, session_id: str) -> str | None:
    """Obtain the DeGiro portfolio csv data at a certain date.

    The method raises a RuntimeError if an error occurred while connecting
    to the DeGiro website.
    """
    if day.weekday() == 5 or day.weekday() == 6:
        # No need to get the portfolio at a weekend
        return None

    url = "https://trader.degiro.nl/reporting/secure/v3/positionReport/csv"
    curl_args: dict[str, str | int] = {
        "sessionId": session_id,
        "country": "NL",
        "lang": "nl",
        "intAccount": account,
        "toDate": day.strftime("%d/%m/%Y"),
    }

    res = requests.get(url, params=curl_args)

    if res.ok:
        return str(res.text)

    raise RuntimeError(f"Got an unexpected response: {res.reason}")


@dataclass(frozen=True)
class PortfolioImportData:
    """The input data to obtain the portfolio csv files."""

    session_id: str = ""
    account_id: int = 0
    start_date: date = date.today()
    end_date: date = date.today()
    folder: Path = Path()


class ScrapeThread:
    """Class to support obtaining the data from DeGiro in a
    separate thread."""

    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._data = PortfolioImportData()
        self._current_date: date = date.today()
        self._stop = False

    def start(self, data: PortfolioImportData) -> bool:
        """Start obtaining data from DeGiro"""
        if self._thread:
            return False
        self._data = data

        self._stop = False
        self._thread = threading.Thread(target=self._process)
        self._thread.start()
        print("started")
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
            print(f"processing: {self._current_date}")
            if self._stop:
                break

            if stockdir.check_portfolio_exists(self._data.folder, self._current_date):
                self._current_date += timedelta(days=1)
                continue

            try:
                portfolio = get_portfolio_at(
                    self._current_date, self._data.account_id, self._data.session_id
                )
            except RuntimeError as ex:
                # We should at least show a pop-up or something
                print(f"Error: {ex}")
                self._current_date = self._data.end_date
                break

            if portfolio:
                stockdir.portfolio_to_file(
                    self._data.folder, portfolio, self._current_date
                )

            self._current_date += timedelta(days=1)
