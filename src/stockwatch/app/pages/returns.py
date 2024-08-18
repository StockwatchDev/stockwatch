"""All dash specific callbacks and layout related to the plots page."""

# pylint: disable=duplicate-code
from datetime import date, timedelta

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from stockwatch import analysis, entities
from stockwatch.app import ids, runtime
from stockwatch.use_cases import stockdir

_SECONDS_IN_WEEK = 60 * 60 * 24 * 7


def _get_layout() -> dash.html.Div:
    """Get the layout."""
    if (
        start_date_limit := stockdir.get_first_date(stockdir.get_portfolio_folder())
    ) is None:
        start_date_limit = date(2008, 1, 1)
    period_long = timedelta(weeks=104)
    period_short = timedelta(weeks=13)
    start_date = start_date_limit + period_long
    end_date = date.today()

    return dash.html.Div(
        [
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dash.html.Label("Start date:"),
                                width={
                                    "size": 1,
                                    "offset": 1,
                                },
                                xl=1,
                                style={"float": "right"},
                            ),
                            dbc.Col(
                                dash.dcc.DatePickerSingle(
                                    id=ids.ReturnsId.START_DATE,
                                    min_date_allowed=start_date_limit,
                                    max_date_allowed=date.today(),
                                    date=start_date,
                                    initial_visible_month=start_date,
                                    display_format="DD/MM/YYYY",
                                    className="dbc",
                                    number_of_months_shown=3,
                                    clearable=False,
                                ),
                                width=1,
                                lg=2,
                            ),
                            dbc.Col(
                                dash.html.Label("End date:"),
                                width=1,
                                xl=1,
                                style={"float": "right"},
                            ),
                            dbc.Col(
                                dash.dcc.DatePickerSingle(
                                    id=ids.ReturnsId.END_DATE,
                                    min_date_allowed=date(2008, 1, 1),
                                    max_date_allowed=date.today(),
                                    date=end_date,
                                    initial_visible_month=date.today(),
                                    display_format="DD/MM/YYYY",
                                    className="dbc",
                                    number_of_months_shown=3,
                                    clearable=False,
                                ),
                                width=1,
                                lg=2,
                            ),
                        ],
                        align="center",
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dash.html.Label("Period 1 (weeks):"),
                                width={
                                    "size": 1,
                                    "offset": 1,
                                },
                                xl=1,
                                style={"float": "right"},
                            ),
                            dbc.Col(
                                dash.dcc.Input(
                                    id=ids.ReturnsId.PERIOD_ONE,
                                    type="number",
                                    value=period_short.total_seconds()
                                    / _SECONDS_IN_WEEK,
                                ),
                                width=1,
                                lg=2,
                            ),
                            dbc.Col(
                                dash.html.Label("Period 2 (weeks):"),
                                width=1,
                                xl=1,
                                style={"float": "right"},
                            ),
                            dbc.Col(
                                dash.dcc.Input(
                                    id=ids.ReturnsId.PERIOD_TWO,
                                    type="number",
                                    value=period_long.total_seconds()
                                    / _SECONDS_IN_WEEK,
                                ),
                                width=1,
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
                                    outline=btn_id is ids.ReturnsId.REFRESH,
                                ),
                                width=1,
                                className="d-grid gap-2",
                            )
                            for title, btn_id in (("Refresh", ids.ReturnsId.REFRESH),)
                        ],
                        justify="start",
                        className="mb-3",
                    ),
                    dbc.Row(
                        dbc.Col(
                            _create_graph_card(
                                "Returns comparison",
                                ids.ReturnsId.GRAPH_COMPARISON,
                            ),
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
    dash.Output(ids.ReturnsId.GRAPH_COMPARISON, "figure"),
    dash.State(ids.ReturnsId.START_DATE, "date"),
    dash.State(ids.ReturnsId.END_DATE, "date"),
    dash.State(ids.ReturnsId.PERIOD_ONE, "value"),
    dash.State(ids.ReturnsId.PERIOD_TWO, "value"),
    dash.Input(ids.ReturnsId.REFRESH, "n_clicks"),
)
def _draw_returns_graph_comparison(
    start_date_str: str,
    end_date_str: str,
    period_one: int,
    period_two: int,
    _clicks: int,
) -> dash.dcc.Graph | go.Figure:
    if not (portos := runtime.get_date_filtered_portfolios(None, None)):
        return go.Figure()
    start_date = date.fromisoformat(start_date_str)
    end_date = date.fromisoformat(end_date_str)

    period_one = timedelta(weeks=period_one)
    period_two = timedelta(weeks=period_two)

    index_positions: list[tuple[entities.shares.SharePosition, ...]] = []

    return analysis.plot_returns_comparison(
        portos,
        index_positions,
        start_date,
        end_date,
        period_1=period_one,
        period_2=period_two,
    )
