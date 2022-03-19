from pathlib import Path
from typing import Optional, Tuple

import plotly.graph_objects as go  # type: ignore
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

from . import analysis
from .app.layout import get_layout

_APP = Dash("StockWatcher")
_PORTOS: Optional[Tuple[analysis.SharePortfolio, ...]] = None


@_APP.callback(
    Output("portfolio-refresh", "n_clicks"),
    Input("portfolio-refresh-folder", "n_clicks"),
    State("folder-selected", "value"),
    State("portfolio-refresh", "n_clicks"),
    prevent_initial_callback=True,
)
def _update_portfolios(_clicks: int, folder: str, refresh_clicks: int):
    global _PORTOS
    path = Path(folder)
    _PORTOS = analysis.create_share_portfolios(folder=path, rename=False)

    analysis.process_transactions(share_portfolios=_PORTOS, folder=path, rename=False)
    return refresh_clicks + 1


@_APP.callback(
    Output("portfolio-graph", "figure"),
    Input("portfolio-refresh", "n_clicks"),
    prevent_initial_callback=True,
)
def _draw_portfolio_graph(_clicks: int) -> dcc.Graph:
    if not _PORTOS:
        return go.Figure()
    return analysis.plot_positions(_PORTOS)


@_APP.callback(
    Output("portfolio-graph-total", "figure"),
    Input("portfolio-refresh", "n_clicks"),
    prevent_initial_callback=True,
)
def _draw_portfolio_graph_total(_clicks: int) -> dcc.Graph:
    if not _PORTOS:
        return go.Figure()
    return analysis.plot_returns(_PORTOS)


def run_blocking(folder: Path):
    _APP.layout = get_layout(folder)
    _APP.run_server(debug=True)
