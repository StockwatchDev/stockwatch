"""This module defines the visual layout of the share portfolios dashboard.

This package has a clean architecture. This module should not contain any business- or
application logic, nor any adapters.
"""
from datetime import date
from pathlib import Path

import dash_bootstrap_components as dbc
from dash import dcc, html

from . import ids


def get_layout(folder: Path) -> dbc.Container:
    """Get the layout of the stockwatch dash application."""
    return dbc.Container(
        [
            html.Div(
                [
                    html.H1(children="Stockwatch"),
                    html.Div(children="Analysis of your DeGiro portfolio."),
                    html.Hr(),
                ],
                id="header",
            ),
            dbc.Tabs(
                [
                    dcc.Tab(
                        label="plotting",
                        children=[
                            html.Div(
                                [
                                    html.Hr(),
                                    html.H2("Portfolio"),
                                    dcc.Graph(
                                        id=ids.PlottingId.GRAPH_RESULT,
                                        style={"width": "100%", "height": "700px"},
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Hr(),
                                    html.H2("Portfolio (Totals)"),
                                    dcc.Graph(
                                        id=ids.PlottingId.GRAPH_TOTAL,
                                        style={"width": "100%", "height": "700px"},
                                    ),
                                    html.Button(
                                        "Refresh",
                                        id=ids.PlottingId.REFRESH,
                                        n_clicks=0,
                                        hidden=True,
                                    ),
                                ]
                            ),
                        ],
                    ),
                    _get_scraping_tab(folder),
                ]
            ),
        ],
        fluid=True,
    )


def _get_scraping_form(folder: Path) -> list[dbc.Row]:
    return [
        dbc.Row(
            [
                dbc.Col(html.Label("folder:"), width=2),
                dbc.Col(
                    dbc.Input(
                        id=ids.ScrapingId.FOLDER,
                        value=f"{folder}",
                        type="text",
                        size="50",
                    ),
                    width=6,
                ),
            ],
            align="center",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(html.Label("account id:"), width=2),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Input(
                                placeholder="accountId",
                                id=ids.ScrapingId.ACCOUNT_ID,
                                type="number",
                                style={"appearance": "textfield"},
                            ),
                            dbc.FormFeedback(
                                "The account id should be a positive number",
                                type="invalid",
                            ),
                        ]
                    ),
                    width=6,
                ),
            ],
            align="center",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(html.Label("session id:"), width=2),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Input(
                                placeholder="sessionId",
                                id=ids.ScrapingId.SESSION_ID,
                                type="text",
                                size="50",
                            ),
                            dbc.FormFeedback(
                                "The sessionid should end with .prod_b_112_1",
                                type="invalid",
                            ),
                        ]
                    ),
                    width=6,
                ),
            ],
            align="center",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(html.Label("start date:"), width=2),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id=ids.ScrapingId.START_DATE,
                        min_date_allowed=date(1995, 8, 5),
                        max_date_allowed=date.today(),
                        initial_visible_month=date(2020, 1, 1),
                        date=date(2020, 1, 1),
                        className="dbc",
                    ),
                    width=2,
                ),
                dbc.Col(html.Label("end date:"), width=2),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id=ids.ScrapingId.END_DATE,
                        min_date_allowed=date(1995, 8, 5),
                        max_date_allowed=date.today(),
                        initial_visible_month=date.today(),
                        date=date.today(),
                        className="dbc",
                    ),
                    width=3,
                ),
            ],
            align="center",
            className="mb-3",
        ),
    ]


def _get_scraping_tab(folder: Path) -> dcc.Tab:
    return dcc.Tab(
        label="scraping",
        children=[
            html.Div([html.Hr(), html.H2("Portfolio Scraping")]),
            html.Div(
                [
                    dcc.Interval(
                        id=ids.ScrapingId.INTERVAL,
                        n_intervals=0,
                        interval=500,
                        disabled=True,
                    ),
                    html.Label(
                        [
                            "This wizard will import data from the DeGiro site. "
                            "For instructions on how to get the attributes see ",
                            html.A(
                                "the README.md",
                                href="https://bitbucket.org/stockwatch-ws/stockwatch"
                                + "/src/develop/README.md#markdown-header-scraping-"
                                + "the-porfolio-data-from-de-giro",
                                target="_blank",
                            ),
                        ]
                    ),
                    html.Hr(),
                    dbc.Container(_get_scraping_form(folder), fluid=True),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Scraping progress...")),
                            dbc.ModalBody(
                                [
                                    html.Label("Importing data from DeGiro"),
                                    dbc.Progress(
                                        id=ids.ScrapingId.PROGRESS,
                                        style={"height": "30px"},
                                    ),
                                    html.Label("", id=ids.ScrapingId.CURRENT),
                                ]
                            ),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Cancel", id=ids.ScrapingId.CLOSE, n_clicks=0
                                )
                            ),
                        ],
                        id=ids.ScrapingId.MODAL,
                        is_open=False,
                    ),
                    html.Hr(),
                    dbc.Button(
                        "Import", id=ids.ScrapingId.EXECUTE, n_clicks=0, disabled=True
                    ),
                    html.P(id=ids.ScrapingId.PLACEHOLDER),
                ]
            ),
        ],
    )
