"""All dash specific callbacks and layout related to the plots page."""
from datetime import date
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from ... import analysis, entities, use_cases
from .. import ids

_PORTOS: tuple[entities.SharePortfolio, ...] | None = None
_TRANSACTIONS: tuple[entities.ShareTransaction, ...] | None = None
_INDICES: dict[str, dict[date, float]] | None = None


def _get_layout() -> dash.html.Div:
    """Get the layout."""
    return dash.html.Div(
        [
            dash.html.Button(
                "Refresh",
                id=ids.PlottingId.REFRESH,
                n_clicks=0,
                hidden=True,
            ),
            dbc.Container(
                [
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
                    style={"text-align": "center"},
                    className="card-title",
                ),
            ),
            dbc.CardBody(
                [
                    dash.dcc.Loading(
                        dash.dcc.Graph(
                            id=graph_id,
                            style={
                                "width": "100%",
                                "height": "700px",
                            },
                        ),
                        color="var(--bs-gray)",
                    ),
                ],
            ),
        ],
        style={"marginBottom": "5em", "verticalAlign": "middle"},
        class_name="border-dark",
    )


layout = _get_layout()

###############################################################################
#                               The Callbacks                                 #
###############################################################################


@dash.callback(
    dash.Output(ids.PlottingId.REFRESH, "n_clicks"),
    dash.Input(ids.HeaderIds.PLOTS, "n_clicks"),
    dash.State(ids.PlottingId.REFRESH, "n_clicks"),
)
def _update_portfolios(_: int, refresh_clicks: int) -> int | dash._callback.NoUpdate:
    global _PORTOS  # pylint: disable=global-statement
    global _TRANSACTIONS  # pylint: disable=global-statement
    global _INDICES  # pylint: disable=global-statement
    folder = "/home/jorik/Documents/stockwatch"

    path = Path(folder)
    _PORTOS = use_cases.process_portfolios(folder=path)

    _TRANSACTIONS = use_cases.process_transactions(
        isins=entities.get_all_isins(_PORTOS), folder=path
    )
    entities.apply_transactions(_TRANSACTIONS, _PORTOS)

    _INDICES = use_cases.process_index_prices(path)

    return refresh_clicks + 1


@dash.callback(
    dash.Output(ids.PlottingId.GRAPH_RESULT, "figure"),
    dash.Input(ids.PlottingId.REFRESH, "n_clicks"),
)
def _draw_portfolio_graph(_clicks: int) -> dash.dcc.Graph:
    if not _PORTOS:
        return go.Figure()
    return analysis.plot_positions(_PORTOS)


@dash.callback(
    dash.Output(ids.PlottingId.GRAPH_TOTAL, "figure"),
    dash.Input(ids.PlottingId.REFRESH, "n_clicks"),
)
def _draw_portfolio_graph_total(_clicks: int) -> dash.dcc.Graph:
    if not _PORTOS:
        return go.Figure()

    index_positions = (
        use_cases.process_indices(
            _INDICES, _TRANSACTIONS, [x.portfolio_date for x in _PORTOS]
        )
        if _INDICES and _TRANSACTIONS
        else []
    )

    return analysis.plot_returns(_PORTOS, index_positions)
