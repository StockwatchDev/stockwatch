# type: ignore[no-untyped-def]
# type: ignore[missing-function-docstring]
"""Test the scraping Dash app."""
import datetime
import random

import dash

from stockwatch.app import runtime
from stockwatch.app.ids import PageIds
from stockwatch.app.pages import scraping


def test_disable_execute() -> None:
    for username in (True, False):
        for password in (True, False):
            for goauth in (True, False):
                if all((username, password, goauth)):
                    assert not scraping.disable_execute(username, password, goauth)
                else:
                    assert scraping.disable_execute(username, password, goauth)


def test_stop_execution(monkeypatch) -> None:
    class MockedThread:
        """Mocked thread implementation."""

        def __init__(self) -> None:
            self.stopped = False

        def stop(self) -> None:
            """Mocked stop method."""
            self.stopped = True

    for _ in range(10):
        mocked_thread = MockedThread()
        monkeypatch.setattr(
            runtime, "get_scrape_thread", lambda: mocked_thread
        )

        assert mocked_thread.stopped is False
        scraping.stop_execution(random.randint(-1000, 1000))
        assert mocked_thread.stopped is True


def test_validate_password() -> None:
    for password in ("whsomahe", "2o3ijjIJEOJjeljs!#($#(", "a", "234234"):
        valid, invalid = scraping.validate_password(password)
        assert valid is not invalid
        assert valid

    valid, invalid = scraping.validate_password("")
    assert valid is not invalid
    assert not valid


def test_validate_goauth() -> None:
    for goauth in ("a12345", "aebfib", "1234567", "1241", "-323456"):
        valid, invalid = scraping.validate_goauth(goauth)
        assert valid is not invalid
        assert not valid

    for goauth in ("123456", "000000", "039485", ""):
        valid, invalid = scraping.validate_goauth(goauth)
        assert valid is not invalid
        assert valid


def test_validate_accountid() -> None:
    for accountid in ("eoije", "12341241", "93J#Jf#@#", "a"):
        valid, invalid = scraping.validate_accountid(accountid)
        assert valid is not invalid
        assert valid

    valid, invalid = scraping.validate_accountid("")
    assert valid is not invalid
    assert not valid


def validate_set_interval() -> None:
    for is_open in (True, False):
        assert scraping.set_interval(is_open) is is_open


def validate_update_progress_bar(monkeypatch) -> None:
    class MockedThread:
        """Mocked thread implementation."""

        def __init__(self) -> None:
            self.progress = 0

    mocked_thread = MockedThread()
    monkeypatch.setattr(runtime, "get_scrape_thread", lambda: mocked_thread)

    for i in range(10):
        mocked_thread.progress = random.randint(0, 1000)

        assert mocked_thread.progress == scraping.update_progress_bar(
            random.randint(0, 1000)
        )


def test_update_progress(monkeypatch) -> None:
    class MockedThread:
        """Mocked thread implementation."""

        def __init__(self) -> None:
            self.current_date = datetime.date.today()
            self.end_date = datetime.date.today()
            self.finished = False

    mocked_thread = MockedThread()
    mocked_thread.finished = True

    monkeypatch.setattr(runtime, "get_scrape_thread", lambda: mocked_thread)
    assert not scraping.update_progress_info(10)

    mocked_thread.finished = False
    info_string = scraping.update_progress_info(10)
    assert f"{mocked_thread.current_date}" in info_string


def test_update_progress_finished(monkeypatch) -> None:
    class MockedThread:
        """Mocked thread implementation."""

        def __init__(self) -> None:
            self.created = False
            self.finished = False

    for created in (False, True):
        for finished in (False, True):
            mocked_thread = MockedThread()
            mocked_thread.created = created
            mocked_thread.finished = finished

            monkeypatch.setattr(
                runtime, "get_scrape_thread", lambda: mocked_thread
            )

            ret = scraping.update_progress_finished(random.randint(0, 1000))

            if created and finished:
                assert ret == PageIds.PLOTS
            else:
                assert ret == dash.no_update
