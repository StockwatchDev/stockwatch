"""This module provides a dashboard for analysis of share portfolios.

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
from .entities import (
    SharePortfolio,
    ShareTransaction,
    apply_transactions,
    get_all_isins,
)
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
    global _PORTOS  # pylint: disable=global-statement
    global _TRANSACTIONS  # pylint: disable=global-statement
    global _INDICES  # pylint: disable=global-statement

    path = Path(folder)
    _PORTOS = process_portfolios(folder=path)

    _TRANSACTIONS = process_transactions(isins=get_all_isins(_PORTOS), folder=path)
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
    prevent_initial_callback=True,
)
def _draw_portfolio_graph_total(_clicks: int) -> dcc.Graph:
    if not _PORTOS:
        return go.Figure()

    index_positions = (
        process_indices(_INDICES, _TRANSACTIONS, [x.portfolio_date for x in _PORTOS])
        if _INDICES and _TRANSACTIONS
        else []
    )

    return plot_returns(_PORTOS, index_positions)


def run_blocking(folder: Path) -> None:
    """Run the dash application."""
    _APP.layout = get_layout(folder)
    _APP.run_server(debug=True)
