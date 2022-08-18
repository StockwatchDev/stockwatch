"""The use cases related to getting data from the DeGiro website."""
import threading
from dataclasses import dataclass
from datetime import date, timedelta

import requests

from stockwatch.use_cases.configuring import get_config

from . import stockdir


def login(username: str, password: str, goauth: str | None) -> tuple[int, str] | None:
    """Login into the degiro site. Obtain a `intAccount` and `sessionId`, return None
    if the login failed.
    """
    url: str = get_config().DeGiroServer.login_url
    curl_args: dict[str, str | dict[str, str]] = {
        "username": username,
        "password": password,
        "queryParams": {},
    }

    if goauth:
        url += get_config().DeGiroServer.ga_ext
        curl_args["oneTimePassword"] = goauth

    res = requests.post(url, json=curl_args)

    if not res.ok:
        print("failed wrong password")
        return None

    data = res.json()
    if (session_id := data.get("sessionId")) is None:
        print("Failed to get session id")
        return None

    session_id = str(session_id)

    # Let's also get the intAccount number.
    url = get_config().DeGiroServer.clientnr_url
    curl_args = {
        "sessionId": session_id,
    }

    res = requests.get(url, params=curl_args)

    if not res.ok:
        print("Failed to obtain account info")
        return None

    data = res.json()
    return int(data["data"]["intAccount"]), session_id


def get_portfolio_at(day: date, account: int, session_id: str) -> str:
    """Obtain the DeGiro portfolio csv data at a certain date.

    The method raises a RuntimeError if an error occurred while connecting
    to the DeGiro website.
    """
    url = get_config().DeGiroServer.portfolio_url
    curl_args: dict[str, str | int] = {
        "sessionId": session_id,
        "country": get_config().DeGiroServer.country,
        "lang": get_config().DeGiroServer.lang,
        "intAccount": account,
        "toDate": day.strftime("%d/%m/%Y"),
    }

    res = requests.get(url, params=curl_args)

    if res.ok:
        return str(res.text)

    raise RuntimeError(f"Got an unexpected response: {res.reason}")


def get_account_report(
    start_day: date, end_day: date, account: int, session_id: str
) -> str:
    """Obtain the account report of a DeGiro account between the start and end date.

    The method raises a RuntimeError if an error occurred while connecting to the
    DeGiro website.
    """

    url = get_config().DeGiroServer.account_url
    curl_args: dict[str, str | int] = {
        "sessionId": session_id,
        "country": get_config().DeGiroServer.country,
        "lang": get_config().DeGiroServer.lang,
        "intAccount": account,
        "fromDate": start_day.strftime("%d/%m/%Y"),
        "toDate": end_day.strftime("%d/%m/%Y"),
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


class ScrapeThread:
    """Class to support obtaining the data from DeGiro in a
    separate thread."""

    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._data = PortfolioImportData()
        self._current_date: date = date.today()
        self._stop = False
        self._finished = True

    def start(self, data: PortfolioImportData) -> bool:
        """Start obtaining data from DeGiro"""
        if self._thread and not self.finished:
            return False

        self._data = data

        self._stop = False
        self._finished = False
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
        return self._finished

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
        if not self._import_porfolio():
            print("Failed to obtain all necessary portfolios")
            self._finished = True
            return

        if not self._import_transactions():
            print("Failed to obtain the transactions.")
            self._finished = True
            return

        self._finished = True

    def _import_transactions(self) -> bool:
        # Let's also obtain the transactions.
        if not self._stop:
            try:
                report = get_account_report(
                    self._data.start_date,
                    self._data.end_date,
                    self._data.account_id,
                    self._data.session_id,
                )
            except RuntimeError as ex:
                # We should at least show a pop-up or something
                print(f"Error during getting account report: {ex}")
                self._stop = True
                return False

            stockdir.account_report_to_file(report)
        return True

    def _import_porfolio(self) -> bool:
        self._current_date = self._data.start_date
        while self._current_date < self._data.end_date:
            if self._stop:
                return False

            if stockdir.check_portfolio_exists(self._current_date):
                self._current_date += timedelta(days=1)
                continue

            try:
                portfolio = get_portfolio_at(
                    self._current_date, self._data.account_id, self._data.session_id
                )
            except RuntimeError as ex:
                # We should at least show a pop-up or something
                print(f"Error during getting portfolio at {self._current_date}: {ex}")
                self._stop = True
                return False

            stockdir.portfolio_to_file(portfolio, self._current_date)

            self._current_date += timedelta(days=1)
        return True
