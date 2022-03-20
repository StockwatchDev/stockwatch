"""
This module provides a dashboard for analysis of share portfolios.

The dashboard is defined by connecting widgets, events, etc. as defined in layout
to methods provided by analysis and use_cases.

This package has a clean architecture. This module should not contain any business- or 
application logic, nor any adapters.
"""
from datetime import date
from pathlib import Path

import plotly.graph_objects as go
from dash import Dash, dcc
from dash.dependencies import Input, Output, State

from .analysis import plot_positions, plot_returns
from .app.layout import get_layout
from .entities import SharePortfolio, ShareTransaction, apply_transactions
from .use_cases import (
    process_index_prices,
    process_indices,
    process_portfolios,
    process_transactions,
)

_APP = Dash("StockWatcher")
_PORTOS: tuple[SharePortfolio, ...] | None = None
_TRANSACTIONS: tuple[ShareTransaction, ...] | None = None
_INDICES: dict[str, dict[date, float]] | None = None


@_APP.callback(
    Output("portfolio-refresh", "n_clicks"),
    Input("portfolio-refresh-folder", "n_clicks"),
    State("folder-selected", "value"),
    State("portfolio-refresh", "n_clicks"),
    prevent_initial_callback=True,
)
def _update_portfolios(_clicks: int, folder: str, refresh_clicks: int) -> int:
    global _PORTOS
    global _TRANSACTIONS
    global _INDICES

    path = Path(folder)
    _PORTOS = process_portfolios(folder=path, rename=False)

    all_isins: set[str] = set()
    for porto in _PORTOS:
        all_isins.update(porto.all_isins())

    _TRANSACTIONS = process_transactions(isins=all_isins, folder=path, rename=False)
    apply_transactions(_TRANSACTIONS, _PORTOS)

    _INDICES = process_index_prices(path)

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
    State("folder-selected", "value"),
    prevent_initial_callback=True,
)
def _draw_portfolio_graph_total(_clicks: int, folder: str) -> dcc.Graph:
    if not _PORTOS:
        return go.Figure()

    if _INDICES is not None and _TRANSACTIONS is not None:
        index_positions = process_indices(
            _INDICES, _TRANSACTIONS, [x.portfolio_date for x in _PORTOS]
        )
    else:
        index_positions = []

    return plot_returns(_PORTOS, index_positions)


def run_blocking(folder: Path) -> None:
    _APP.layout = get_layout(folder)
    _APP.run_server(debug=True)
