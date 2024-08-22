"""Dash app callbacks for importing/scraping data from DeGiro."""

from collections import namedtuple
from datetime import date

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from stockwatch.app import runtime
from stockwatch.app.ids import HeaderIds, PageIds, ScrapingId
from stockwatch.use_cases import degiro, stockdir

layout = dash.dash.html.Div()


def init_layout() -> None:
    """Initialze the layout for the scraping page."""
    global layout  # pylint: disable=global-statement
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
                    dbc.Alert(
                        "Failed to login",
                        color="danger",
                        dismissable=True,
                        id=ScrapingId.LOGIN_FAIL,
                        is_open=False,
                    ),
                    dbc.Container(_get_scraping_form(), fluid=True),
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


def _get_scraping_form() -> list[dbc.Row]:
    folder = stockdir.get_stockdir()
    if (start_date := stockdir.get_first_date(stockdir.get_portfolio_folder())) is None:
        start_date = date(2020, 1, 1)

    return [
        dbc.Row(
            [
                dbc.Col(dash.html.Label("Folder:"), width=2, xl=1),
                dbc.Col(
                    dbc.Input(
                        id=ScrapingId.FOLDER,
                        value=f"{folder}",
                        type="text",
                        disabled=True,
                    ),
                    width=7,
                ),
            ],
            align="center",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(dash.html.Label("Username:"), width=2, xl=1),
                dbc.Col(
                    dbc.Input(
                        placeholder="username",
                        id=ScrapingId.USERNAME,
                        type="text",
                    ),
                    width=7,
                ),
            ],
            align="center",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(dash.html.Label("Password:"), width=2, xl=1),
                dbc.Col(
                    dbc.Input(
                        placeholder="password",
                        id=ScrapingId.PASSWORD,
                        type="password",
                    ),
                    width=7,
                ),
            ],
            align="center",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(dash.html.Label("TOTP:"), width=2, xl=1),
                dbc.Col(
                    dbc.Input(
                        placeholder="Google Authenticator code",
                        id=ScrapingId.GOAUTH,
                        type="text",
                        maxlength=6,
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
    Input(ScrapingId.USERNAME, "valid"),
    Input(ScrapingId.PASSWORD, "valid"),
    Input(ScrapingId.GOAUTH, "valid"),
)
def disable_execute(
    username_valid: bool, password_valid: bool, goauth_valid: bool
) -> bool:
    """Callback to disable the execute button."""
    return not (username_valid and password_valid and goauth_valid)


@dash.callback(
    Output(ScrapingId.PLACEHOLDER, "n_clicks"), Input(ScrapingId.CLOSE, "n_clicks")
)
def stop_execution(_n_clicks: int) -> None:
    """Callback to stop execution."""
    runtime.get_scrape_thread().stop()


@dash.callback(
    [
        Output(ScrapingId.MODAL, "is_open"),
        Output(ScrapingId.LOGIN_FAIL, "is_open"),
    ],
    Input(ScrapingId.EXECUTE, "n_clicks"),
    State(ScrapingId.USERNAME, "value"),
    State(ScrapingId.PASSWORD, "value"),
    State(ScrapingId.GOAUTH, "value"),
    State(ScrapingId.START_DATE, "date"),
    State(ScrapingId.END_DATE, "date"),
)
def execute_scraping(
    _execute_clicks: int,
    username: str | None,
    password: str | None,
    goauth: str | None,
    start_date: str,
    end_date: str,
) -> tuple[bool, bool] | dash._callback.NoUpdate:
    """Callback to start the scraping thread."""
    if not username or not password:
        return dash.no_update

    if (
        login := degiro.login(username=username, password=password, goauth=goauth)
    ) is None:
        # Here we should raise a popup or something?
        return False, True

    started = runtime.get_scrape_thread().start(
        degiro.PortfolioImportData(
            account_id=login[0],
            session_id=login[1],
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
        )
    )

    return started, False


ValidationOutput = namedtuple("ValidationOutput", ["valid", "invalid"])


@dash.callback(
    [Output(ScrapingId.PASSWORD, "valid"), Output(ScrapingId.PASSWORD, "invalid")],
    Input(ScrapingId.PASSWORD, "value"),
)
def validate_password(password: str | None) -> ValidationOutput:
    """Callback to validate the current password."""
    if not password:
        return ValidationOutput(False, True)
    return ValidationOutput(True, False)


@dash.callback(
    [Output(ScrapingId.GOAUTH, "valid"), Output(ScrapingId.GOAUTH, "invalid")],
    Input(ScrapingId.GOAUTH, "value"),
)
def validate_goauth(goauth: str | None) -> ValidationOutput:
    """Callback to validate the google authenticator code."""
    if not goauth:
        return ValidationOutput(True, False)

    if not goauth.isnumeric():
        return ValidationOutput(False, True)

    if len(goauth) != 6:
        return ValidationOutput(False, True)

    return ValidationOutput(True, False)


@dash.callback(
    [Output(ScrapingId.USERNAME, "valid"), Output(ScrapingId.USERNAME, "invalid")],
    Input(ScrapingId.USERNAME, "value"),
)
def validate_accountid(username: str | None) -> ValidationOutput:
    """Callback to validate the account id."""
    if not username:
        return ValidationOutput(False, True)
    return ValidationOutput(True, False)


@dash.callback(
    Output(ScrapingId.INTERVAL, "disabled"), Input(ScrapingId.MODAL, "is_open")
)
def set_interval(is_open: bool) -> bool:
    """Callback to enable the interval timer."""
    return not is_open


@dash.callback(
    Output(ScrapingId.PROGRESS, "value"), Input(ScrapingId.INTERVAL, "n_intervals")
)
def update_progress_bar(_iter: int) -> int:
    """Callback to update the progress bar fill."""
    return runtime.get_scrape_thread().progress


@dash.callback(
    Output(ScrapingId.CURRENT, "children"), Input(ScrapingId.INTERVAL, "n_intervals")
)
def update_progress_info(_iter: int) -> str:
    """Callback to update the progress bar info text."""
    if runtime.get_scrape_thread().finished:
        return ""

    days_left = (
        runtime.get_scrape_thread().end_date - runtime.get_scrape_thread().current_date
    ).days + 1
    return (
        f"Currently processing: {runtime.get_scrape_thread().current_date} - still "
        f"{days_left} days to go"
    )


@dash.callback(
    Output(HeaderIds.LOCATION, "pathname"), Input(ScrapingId.INTERVAL, "n_intervals")
)
def update_progress_finished(_iter: int) -> str | dash._callback.NoUpdate:
    """Callback to switch the page when finished."""
    if not runtime.get_scrape_thread().created:
        return dash.no_update
    if not runtime.get_scrape_thread().finished:
        return dash.no_update
    return PageIds.PLOTS
