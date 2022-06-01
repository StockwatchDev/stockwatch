"""Dash app callbacks for importing/scraping data from DeGiro."""
from collections import namedtuple
from datetime import date
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from stockwatch.use_cases import degiro, stockdir
from stockwatch.app.ids import HeaderIds, PageIds, ScrapingId

_SCRAPE_THREAD = degiro.ScrapeThread()
layout = dash.dash.html.Div()


def init_layout(folder: Path) -> None:
    """Initialze the layout for the scraping page."""
    global layout  # pylint: disable=global-statement, invalid-name
    layout = dash.html.Div(
        [
            dbc.Container(
                [
                    dbc.Row(
                        dbc.Col(
                            [
                                dash.html.H2("Portfolio Scraping"),
                                dash.dcc.Interval(
                                    id=ScrapingId.INTERVAL,
                                    n_intervals=0,
                                    interval=500,
                                    disabled=True,
                                ),
                            ]
                        )
                    ),
                    dbc.Row(
                        dbc.Col(
                            dash.html.Label(
                                [
                                    "This wizard will import data from the DeGiro site. "
                                    "For instructions on how to get the attributes see ",
                                    dash.html.A(
                                        "the README.md",
                                        href="https://bitbucket.org/stockwatch-ws/stockwatch"
                                        + "/src/develop/README.md#markdown-header-scraping-"
                                        + "the-porfolio-data-from-de-giro",
                                        target="_blank",
                                    ),
                                ]
                            )
                        )
                    ),
                    dbc.Row(dash.html.Hr()),
                    dbc.Container(_get_scraping_form(folder), fluid=True),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Scraping progress...")),
                            dbc.ModalBody(
                                [
                                    dash.html.Label("Importing data from DeGiro"),
                                    dbc.Progress(
                                        id=ScrapingId.PROGRESS, style={"height": "30px"}
                                    ),
                                    dash.html.Label("", id=ScrapingId.CURRENT),
                                ]
                            ),
                            dbc.ModalFooter(
                                dbc.Button("Cancel", id=ScrapingId.CLOSE, n_clicks=0)
                            ),
                        ],
                        id=ScrapingId.MODAL,
                        is_open=False,
                    ),
                    dash.html.Hr(),
                    dash.html.P(id=ScrapingId.PLACEHOLDER),
                ]
            )
        ]
    )


def _get_scraping_form(folder: Path) -> list[dbc.Row]:
    start_date = stockdir.get_first_date(folder / "portfolio")
    if start_date is None:
        start_date = date(2020, 1, 1)

    return [
        dbc.Row(
            [
                dbc.Col(dash.html.Label("Folder:"), width=2, xl=1),
                dbc.Col(
                    dbc.Input(id=ScrapingId.FOLDER, value=f"{folder}", type="text"),
                    width=7,
                ),
            ],
            align="center",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(dash.html.Label("Account ID:"), width=2, xl=1),
                dbc.Col(
                    dbc.Input(
                        placeholder="account ID",
                        id=ScrapingId.ACCOUNT_ID,
                        type="number",
                        style={"appearance": "textfield"},
                    ),
                    width=7,
                ),
            ],
            align="center",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(dash.html.Label("Session ID:"), width=2, xl=1),
                dbc.Col(
                    dbc.Input(
                        placeholder="session ID", id=ScrapingId.SESSION_ID, type="text"
                    ),
                    width=7,
                ),
            ],
            align="center",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(dash.html.Label("Start date:"), width=2, xl=1),
                dbc.Col(
                    dash.dcc.DatePickerSingle(
                        id=ScrapingId.START_DATE,
                        min_date_allowed=date(2008, 1, 1),
                        max_date_allowed=date.today(),
                        date=start_date,
                        display_format="DD/MM/YYYY",
                        className="dbc",
                    ),
                    width="auto",
                    lg=2,
                ),
                dbc.Col(
                    dash.html.Label("End date:"),
                    width=2,
                    xl=1,
                    style={"float": "right"},
                ),
                dbc.Col(
                    dash.dcc.DatePickerSingle(
                        id=ScrapingId.END_DATE,
                        min_date_allowed=date(2008, 1, 1),
                        max_date_allowed=date.today(),
                        display_format="DD/MM/YYYY",
                        date=date.today(),
                        className="dbc",
                        style={"float": "right"},
                    ),
                    width="auto",
                    lg=2,
                ),
            ],
            align="center",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            "Import", id=ScrapingId.EXECUTE, n_clicks=0, disabled=True
                        )
                    ],
                    width="auto",
                )
            ]
        ),
    ]


@dash.callback(
    Output(ScrapingId.EXECUTE, "disabled"),
    Input(ScrapingId.SESSION_ID, "valid"),
    Input(ScrapingId.ACCOUNT_ID, "valid"),
)
def _disable_execute(session_id_valid: bool, account_id_valid: bool) -> bool:
    return not session_id_valid or not account_id_valid


@dash.callback(
    Output(ScrapingId.PLACEHOLDER, "n_clicks"), Input(ScrapingId.CLOSE, "n_clicks")
)
def _stop_execution(_n_clicks: int) -> None:
    _SCRAPE_THREAD.stop()


@dash.callback(
    Output(ScrapingId.MODAL, "is_open"),
    Input(ScrapingId.EXECUTE, "n_clicks"),
    State(ScrapingId.SESSION_ID, "value"),
    State(ScrapingId.ACCOUNT_ID, "value"),
    State(ScrapingId.START_DATE, "date"),
    State(ScrapingId.END_DATE, "date"),
    State(ScrapingId.FOLDER, "value"),
)
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


@dash.callback(
    [Output(ScrapingId.SESSION_ID, "valid"), Output(ScrapingId.SESSION_ID, "invalid")],
    Input(ScrapingId.SESSION_ID, "value"),
)
def _validate_sessionid(sessionid: str | None) -> ValidationOutput:
    if sessionid:
        valid = degiro.is_valid_sessionid(sessionid)
        return ValidationOutput(valid=valid, invalid=not valid)
    return ValidationOutput(False, False)


@dash.callback(
    [Output(ScrapingId.ACCOUNT_ID, "valid"), Output(ScrapingId.ACCOUNT_ID, "invalid")],
    Input(ScrapingId.ACCOUNT_ID, "value"),
)
def _validate_accountid(accountid: int | None) -> ValidationOutput:
    if accountid:
        valid = degiro.is_valid_accountid(accountid)
        return ValidationOutput(valid=valid, invalid=not valid)
    return ValidationOutput(False, False)


@dash.callback(
    Output(ScrapingId.INTERVAL, "disabled"), Input(ScrapingId.MODAL, "is_open")
)
def _set_interval(is_open: bool) -> bool:
    return not is_open


@dash.callback(
    Output(ScrapingId.PROGRESS, "value"), Input(ScrapingId.INTERVAL, "n_intervals")
)
def _update_progress_bar(_iter: int) -> int:
    if _SCRAPE_THREAD.finished:
        _SCRAPE_THREAD.clear()
        return 0

    return _SCRAPE_THREAD.progress


@dash.callback(
    Output(ScrapingId.CURRENT, "children"), Input(ScrapingId.INTERVAL, "n_intervals")
)
def _update_progress_info(_iter: int) -> str:
    if _SCRAPE_THREAD.finished:
        return ""

    return (
        f"Currently processing: {_SCRAPE_THREAD.current_date} - still "
        f"{(_SCRAPE_THREAD.end_date - _SCRAPE_THREAD.current_date).days} "
        f"days to go"
    )


@dash.callback(
    Output(HeaderIds.LOCATION, "pathname"), Input(ScrapingId.INTERVAL, "n_intervals")
)
def _update_progress_finished(_iter: int) -> str | dash._callback.NoUpdate:
    if not _SCRAPE_THREAD.created:
        return dash.no_update
    return PageIds.PLOTS
