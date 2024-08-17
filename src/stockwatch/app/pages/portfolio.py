"""All dash specific callbacks and layout related to the plots page."""

# pylint: disable=duplicate-code
from datetime import date, timedelta

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from stockwatch import analysis, entities
from stockwatch.app import ids, runtime


def _get_layout() -> dash.html.Div:
    """Get the layout."""
    return dash.html.Div(
        [
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dash.html.Label("Start date:"),
                                width={
                                    "size": 2,
                                    "offset": 1,
                                },
                                xl=1,
                                style={"float": "right"},
                            ),
                            dbc.Col(
                                dash.dcc.DatePickerSingle(
                                    id=ids.PortfolioId.START_DATE,
                                    min_date_allowed=date(2008, 1, 1),
                                    max_date_allowed=date.today(),
                                    initial_visible_month=date.today(),
                                    display_format="DD/MM/YYYY",
                                    className="dbc",
                                    number_of_months_shown=3,
                                    clearable=True,
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
                                    id=ids.PortfolioId.END_DATE,
                                    min_date_allowed=date(2008, 1, 1),
                                    max_date_allowed=date.today(),
                                    initial_visible_month=date.today(),
                                    display_format="DD/MM/YYYY",
                                    className="dbc",
                                    number_of_months_shown=3,
                                    clearable=True,
                                ),
                                width="auto",
                                lg=2,
                            ),
                        ],
                        align="center",
                        className="mb-3",
                    ),
                    dbc.Row(
                        [dbc.Col(width=1)]
                        + [
                            dbc.Col(
                                dbc.Button(
                                    title,
                                    n_clicks=0,
                                    id=btn_id,
                                    color="dark",
                                    outline=btn_id is ids.PortfolioId.REFRESH,
                                ),
                                width=1,
                                className="d-grid gap-2",
                            )
                            for title, btn_id in (
                                ("Year to Date", ids.PortfolioId.YTD_BTN),
                                ("Last Year", ids.PortfolioId.LY_BTN),
                                ("Month to Date", ids.PortfolioId.MTD_BTN),
                                ("Last Month", ids.PortfolioId.LM_BTN),
                                ("All", ids.PortfolioId.ALL_BTN),
                                ("Refresh", ids.PortfolioId.REFRESH),
                            )
                        ],
                        justify="start",
                        className="mb-3",
                    ),
                    dbc.Row(
                        dbc.Col(dash.html.Hr()),
                        className="mb-3",
                    ),
                    dbc.Row(
                        dbc.Col(
                            _create_graph_card(
                                "Portfolio", ids.PortfolioId.GRAPH_RESULT
                            ),
                            width=10,
                        ),
                        justify="center",
                    ),
                    dbc.Row(
                        dbc.Col(
                            _create_graph_card("Totals", ids.PortfolioId.GRAPH_TOTAL),
                            width=10,
                        ),
                        justify="center",
                    ),
                ],
                fluid=True,
            ),
        ]
    )


def _create_graph_card(title: str, graph_id: ids.PortfolioId) -> dbc.Card:
    return dbc.Card(
        [
            dbc.CardHeader(
                dash.html.H2(
                    title,
                    style={"textAlign": "center", "color": "#ECECEC"},
                    className="card-title",
                ),
                class_name="bg-dark",
            ),
            dbc.CardBody(
                [
                    dash.dcc.Loading(
                        dash.dcc.Graph(
                            id=graph_id, style={"width": "100%", "height": "700px"}
                        ),
                        color="var(--bs-gray)",
                    )
                ]
            ),
        ],
        style={"marginBottom": "5em", "verticalAlign": "middle"},
        class_name="border-dark",
    )


layout = _get_layout()


@dash.callback(
    dash.Output(ids.PortfolioId.REFRESH, "n_clicks"),
    dash.State(ids.PortfolioId.REFRESH, "n_clicks"),
    dash.Input(ids.HeaderIds.PORTFOLIO, "n_clicks"),
    dash.Input(ids.PortfolioId.YTD_BTN, "n_clicks"),
    dash.Input(ids.PortfolioId.MTD_BTN, "n_clicks"),
    dash.Input(ids.PortfolioId.LM_BTN, "n_clicks"),
    dash.Input(ids.PortfolioId.LY_BTN, "n_clicks"),
    dash.Input(ids.PortfolioId.ALL_BTN, "n_clicks"),
)
def _update_portfolios(
    refresh_clicks: int, *_other_buttons: list[int]
) -> int | dash._callback.NoUpdate:
    runtime.load_portfolios()
    return refresh_clicks + 1


@dash.callback(
    dash.Output(ids.PortfolioId.GRAPH_RESULT, "figure"),
    dash.State(ids.PortfolioId.START_DATE, "date"),
    dash.State(ids.PortfolioId.END_DATE, "date"),
    dash.Input(ids.PortfolioId.REFRESH, "n_clicks"),
)
def _draw_portfolio_graph(
    start_date_str: str | None, end_date_str: str | None, _clicks: int
) -> dash.dcc.Graph | go.Figure:
    start_date = date.fromisoformat(start_date_str) if start_date_str else None
    end_date = date.fromisoformat(end_date_str) if end_date_str else None

    if not (portos := runtime.get_date_filtered_portfolios(start_date, end_date)):
        return go.Figure()
    return analysis.plot_positions(portos)


@dash.callback(
    dash.Output(ids.PortfolioId.GRAPH_TOTAL, "figure"),
    dash.State(ids.PortfolioId.START_DATE, "date"),
    dash.State(ids.PortfolioId.END_DATE, "date"),
    dash.Input(ids.PortfolioId.REFRESH, "n_clicks"),
)
def _draw_portfolio_graph_total(
    start_date_str: str | None, end_date_str: str | None, _clicks: int
) -> dash.dcc.Graph | go.Figure:
    start_date = date.fromisoformat(start_date_str) if start_date_str else None
    end_date = date.fromisoformat(end_date_str) if end_date_str else None

    if not (portos := runtime.get_date_filtered_portfolios(start_date, end_date)):
        return go.Figure()

    index_positions: list[tuple[entities.shares.SharePosition, ...]] = []

    return analysis.plot_returns(portos, index_positions)


def _get_start_end_date(date_id: ids.PortfolioId) -> tuple[date | None, date | None]:
    match date_id:
        case ids.PortfolioId.ALL_BTN:
            start_date = None
            end_date = None
        case ids.PortfolioId.YTD_BTN:
            end_date = date.today()
            start_date = date(year=end_date.year, month=1, day=1)
        case ids.PortfolioId.MTD_BTN:
            end_date = date.today()
            start_date = date(year=end_date.year, month=end_date.month, day=1)
        case ids.PortfolioId.LY_BTN:
            today = date.today()
            start_date = date(year=today.year - 1, month=1, day=1)
            end_date = date(
                year=today.year - 1,
                month=12,
                day=31,
            )
        case ids.PortfolioId.LM_BTN:
            today = date.today()
            end_date = today - timedelta(days=today.day)
            start_date = date(year=end_date.year, month=end_date.month, day=1)
        case _:
            start_date = None
            end_date = None

    return start_date, end_date


@dash.callback(
    [
        dash.Output(ids.PortfolioId.START_DATE, "date"),
        dash.Output(ids.PortfolioId.END_DATE, "date"),
    ],
    [
        dash.Input(ids.PortfolioId.LY_BTN, "n_clicks"),
        dash.Input(ids.PortfolioId.YTD_BTN, "n_clicks"),
        dash.Input(ids.PortfolioId.MTD_BTN, "n_clicks"),
        dash.Input(ids.PortfolioId.LM_BTN, "n_clicks"),
        dash.Input(ids.PortfolioId.ALL_BTN, "n_clicks"),
    ],
)
def _update_start_end_date(
    *_n_clicks: list[int],
) -> tuple[date | None, date | None] | dash._callback.NoUpdate:
    if dash.callback_context.triggered_id is None:
        return dash.no_update
    return _get_start_end_date(dash.callback_context.triggered_id)


@dash.callback(
    dash.Output(ids.PortfolioId.YTD_BTN, "disabled"),
    dash.Input(ids.PortfolioId.REFRESH, "n_clicks"),
)
def _update_ytd_disabled(_n_clicks: int) -> bool:
    if (requested_start := _get_start_end_date(ids.PortfolioId.YTD_BTN)[0]) is None:
        return True
    return requested_start >= runtime.get_enddate()


@dash.callback(
    dash.Output(ids.PortfolioId.MTD_BTN, "disabled"),
    dash.Input(ids.PortfolioId.REFRESH, "n_clicks"),
)
def _update_mtd_disabled(_n_clicks: int) -> bool:
    if (requested_start := _get_start_end_date(ids.PortfolioId.MTD_BTN)[0]) is None:
        return True
    return requested_start >= runtime.get_enddate()


@dash.callback(
    dash.Output(ids.PortfolioId.LY_BTN, "disabled"),
    dash.Input(ids.PortfolioId.REFRESH, "n_clicks"),
)
def _update_ly_disabled(_n_clicks: int) -> bool:
    if (requested_start := _get_start_end_date(ids.PortfolioId.LY_BTN)[0]) is None:
        return True
    return requested_start >= runtime.get_enddate()


@dash.callback(
    dash.Output(ids.PortfolioId.LM_BTN, "disabled"),
    dash.Input(ids.PortfolioId.REFRESH, "n_clicks"),
)
def _update_lm_disabled(_n_clicks: int) -> bool:
    if (requested_start := _get_start_end_date(ids.PortfolioId.LM_BTN)[0]) is None:
        return True
    return requested_start >= runtime.get_enddate()


@dash.callback(
    dash.Output(ids.PortfolioId.START_DATE, "min_date_allowed"),
    dash.Output(ids.PortfolioId.START_DATE, "max_date_allowed"),
    dash.Input(ids.PortfolioId.END_DATE, "date"),
    dash.Input(ids.PortfolioId.REFRESH, "n_clicks"),
)
def _update_allowed_start_date(end_date_str: str, _n_clicks: int) -> tuple[date, date]:
    min_date = runtime.get_startdate()
    max_date = runtime.get_enddate() - timedelta(days=1)

    if end_date_str:
        if end_date := date.fromisoformat(end_date_str):
            max_date = min(max_date, end_date - timedelta(days=1))

    return min_date, max_date


@dash.callback(
    dash.Output(ids.PortfolioId.END_DATE, "min_date_allowed"),
    dash.Output(ids.PortfolioId.END_DATE, "max_date_allowed"),
    dash.Input(ids.PortfolioId.START_DATE, "date"),
    dash.Input(ids.PortfolioId.REFRESH, "n_clicks"),
)
def _update_allowed_end_date(start_date_str: str, _n_clicks: int) -> tuple[date, date]:
    min_date = runtime.get_startdate() + timedelta(days=1)
    max_date = runtime.get_enddate()

    if start_date_str:
        if start_date := date.fromisoformat(start_date_str):
            min_date = max(min_date, start_date + timedelta(days=1))

    return min_date, max_date
