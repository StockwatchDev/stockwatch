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
                                    id=ids.PlottingId.START_DATE,
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
                                    id=ids.PlottingId.END_DATE,
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
                                    outline=btn_id is ids.PlottingId.REFRESH,
                                ),
                                width=1,
                                className="d-grid gap-2",
                            )
                            for title, btn_id in (
                                ("Year to Date", ids.PlottingId.YTD_BTN),
                                ("Last Year", ids.PlottingId.LY_BTN),
                                ("This Month", ids.PlottingId.TM_BTN),
                                ("Last Month", ids.PlottingId.LM_BTN),
                                ("Clear", ids.PlottingId.CLEAR_BTN),
                                ("Refresh", ids.PlottingId.REFRESH),
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
                                "Portfolio", ids.PlottingId.GRAPH_RESULT
                            ),
                            width=10,
                        ),
                        justify="center",
                    ),
                    dbc.Row(
                        dbc.Col(
                            _create_graph_card("Totals", ids.PlottingId.GRAPH_TOTAL),
                            width=10,
                        ),
                        justify="center",
                    ),
                ],
                fluid=True,
            ),
        ]
    )


def _create_graph_card(title: str, graph_id: ids.PlottingId) -> dbc.Card:
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
    dash.Output(ids.PlottingId.REFRESH, "n_clicks"),
    dash.Input(ids.HeaderIds.PLOTS, "n_clicks"),
    dash.State(ids.PlottingId.REFRESH, "n_clicks"),
)
def _update_portfolios(_: int, refresh_clicks: int) -> int | dash._callback.NoUpdate:
    runtime.load_portfolios()
    return refresh_clicks + 1


@dash.callback(
    dash.Output(ids.PlottingId.GRAPH_RESULT, "figure"),
    dash.State(ids.PlottingId.START_DATE, "date"),
    dash.State(ids.PlottingId.END_DATE, "date"),
    dash.Input(ids.PlottingId.REFRESH, "n_clicks"),
)
def _draw_portfolio_graph(
    start_date_str: str | None, end_date_str: str | None, _clicks: int
) -> dash.dcc.Graph | go.Figure:
    start_date = date.fromisoformat(start_date_str) if start_date_str else None
    end_date = date.fromisoformat(end_date_str) if end_date_str else None

    if not (portos := runtime.get_portfolios(start_date, end_date)):
        return go.Figure()
    return analysis.plot_positions(portos)


@dash.callback(
    dash.Output(ids.PlottingId.GRAPH_TOTAL, "figure"),
    dash.State(ids.PlottingId.START_DATE, "date"),
    dash.State(ids.PlottingId.END_DATE, "date"),
    dash.Input(ids.PlottingId.REFRESH, "n_clicks"),
)
def _draw_portfolio_graph_total(
    start_date_str: str | None, end_date_str: str | None, _clicks: int
) -> dash.dcc.Graph | go.Figure:
    start_date = date.fromisoformat(start_date_str) if start_date_str else None
    end_date = date.fromisoformat(end_date_str) if end_date_str else None

    if not (portos := runtime.get_portfolios(start_date, end_date)):
        return go.Figure()

    index_positions: list[tuple[entities.shares.SharePosition, ...]] = []

    return analysis.plot_returns(portos, index_positions)


@dash.callback(
    [
        dash.Output(ids.PlottingId.START_DATE, "date"),
        dash.Output(ids.PlottingId.END_DATE, "date"),
    ],
    [
        dash.Input(ids.PlottingId.LY_BTN, "n_clicks"),
        dash.Input(ids.PlottingId.YTD_BTN, "n_clicks"),
        dash.Input(ids.PlottingId.TM_BTN, "n_clicks"),
        dash.Input(ids.PlottingId.LM_BTN, "n_clicks"),
        dash.Input(ids.PlottingId.CLEAR_BTN, "n_clicks"),
    ],
)
def _update_start_end_date(
    _n_clicks_ly: int,
    _n_clicks_ytd: int,
    _n_clicks_tm: int,
    _n_clicks_lm: int,
    _n_clicks_clear: int,
) -> tuple[date | None, date | None] | dash._callback.NoUpdate:
    start_date: date | None = date.today()
    end_date: date | None = date.today()
    match dash.callback_context.triggered_id:
        case None:
            return dash.no_update
        case ids.PlottingId.CLEAR_BTN:
            start_date = None
            end_date = None
        case ids.PlottingId.YTD_BTN:
            end_date = date.today()
            start_date = date(year=end_date.year, month=1, day=1)
        case ids.PlottingId.TM_BTN:
            end_date = date.today()
            start_date = date(year=end_date.year, month=end_date.month, day=1)
        case ids.PlottingId.LY_BTN:
            today = date.today()
            start_date = date(year=today.year - 1, month=1, day=1)
            end_date = date(
                year=today.year - 1,
                month=12,
                day=31,
            )
        case ids.PlottingId.LM_BTN:
            today = date.today()
            end_date = today - timedelta(days=today.day + 1)
            start_date = date(year=end_date.year, month=end_date.month, day=1)
    return start_date, end_date
