"""
This module provides a dashboard for analysis of share portfolios.

The dashboard is defined by connecting widgets, events, etc. as defined in layout
to methods provided by analysis and use_cases.

This package has a clean architecture. This module should not contain any business- or 
application logic, nor any adapters.
"""
from pathlib import Path
from typing import Optional, Tuple

import plotly.graph_objects as go
from dash import Dash, dcc
from dash.dependencies import Input, Output, State

from .app.layout import get_layout
from .entities import SharePortfolio
from .use_cases import process_portfolios, process_transactions
from .analysis import plot_positions, plot_returns

_APP = Dash("StockWatcher")
_PORTOS: Optional[Tuple[SharePortfolio, ...]] = None


@_APP.callback(
    Output("portfolio-refresh", "n_clicks"),
    Input("portfolio-refresh-folder", "n_clicks"),
    State("folder-selected", "value"),
    State("portfolio-refresh", "n_clicks"),
    prevent_initial_callback=True,
)
def _update_portfolios(_clicks: int, folder: str, refresh_clicks: int) -> int:
    global _PORTOS
    path = Path(folder)
    _PORTOS = process_portfolios(folder=path, rename=False)

    process_transactions(share_portfolios=_PORTOS, folder=path, rename=False)
    return refresh_clicks + 1


@_APP.callback(
    Output("portfolio-graph", "figure"),
    Input("portfolio-refresh", "n_clicks"),
    prevent_initial_callback=True,
)
def _draw_portfolio_graph(_clicks: int) -> dcc.Graph:
    if not _PORTOS:
        return go.Figure()
    return plot_positions(_PORTOS)


@_APP.callback(
    Output("portfolio-graph-total", "figure"),
    Input("portfolio-refresh", "n_clicks"),
    prevent_initial_callback=True,
)
def _draw_portfolio_graph_total(_clicks: int) -> dcc.Graph:
    if not _PORTOS:
        return go.Figure()
    return plot_returns(_PORTOS)


def run_blocking(folder: Path) -> None:
    _APP.layout = get_layout(folder)
    _APP.run_server(debug=True)
