"""This module defines the visual layout of the share portfolios dashboard.

This package has a clean architecture. This module should not contain any business- or
application logic, nor any adapters.
"""
from datetime import date
from pathlib import Path

import dash_bootstrap_components as dbc
from dash import dcc, html

from .. import use_cases
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
                    dbc.Tab(
                        label="Plotting",
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
                dbc.Col(html.Label("Folder:"), width=2),
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
                dbc.Col(html.Label("Account ID:"), width=2),
                dbc.Col(
                    dbc.Input(
                        placeholder="account ID",
                        id=ids.ScrapingId.ACCOUNT_ID,
                        type="number",
                        style={"appearance": "textfield"},
                    ),
                    width=6,
                ),
            ],
            align="center",
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(html.Label("Session ID:"), width=2),
                dbc.Col(
                    dbc.Input(
                        placeholder="session ID",
                        id=ids.ScrapingId.SESSION_ID,
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
                dbc.Col(html.Label("Start date:"), width=2),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id=ids.ScrapingId.START_DATE,
                        min_date_allowed=date(2008, 1, 1),
                        max_date_allowed=date.today(),
                        date=use_cases.stockdir.get_last_date(folder / "portfolio"),
                        display_format="DD/MM/YYYY",
                        className="dbc",
                    ),
                    width=2,
                ),
                dbc.Col(html.Label("End date:"), width=2),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id=ids.ScrapingId.END_DATE,
                        min_date_allowed=date(2008, 1, 1),
                        max_date_allowed=date.today(),
                        display_format="DD/MM/YYYY",
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


def _get_scraping_tab(folder: Path) -> dbc.Tab:
    return dbc.Tab(
        label="Scraping",
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
