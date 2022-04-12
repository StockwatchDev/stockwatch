"""The plotting dashboard methods."""
from datetime import date
from pathlib import Path

import dash
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

from ..analysis import plot_positions, plot_returns
from ..entities import (
    SharePortfolio,
    ShareTransaction,
    apply_transactions,
    get_all_isins,
)
from ..use_cases import (
    process_index_prices,
    process_indices,
    process_portfolios,
    process_transactions,
)
from . import ids

_PORTOS: tuple[SharePortfolio, ...] | None = None
_TRANSACTIONS: tuple[ShareTransaction, ...] | None = None
_INDICES: dict[str, dict[date, float]] | None = None


def _update_portfolios(
    is_open: bool, folder: str, refresh_clicks: int
) -> int | dash._callback.NoUpdate:
    global _PORTOS  # pylint: disable=global-statement
    global _TRANSACTIONS  # pylint: disable=global-statement
    global _INDICES  # pylint: disable=global-statement
    if is_open:
        return dash.no_update

    path = Path(folder)
    _PORTOS = process_portfolios(folder=path)

    _TRANSACTIONS = process_transactions(isins=get_all_isins(_PORTOS), folder=path)
    apply_transactions(_TRANSACTIONS, _PORTOS)

    _INDICES = process_index_prices(path)

    return refresh_clicks + 1


def _draw_portfolio_graph(_clicks: int) -> dash.dcc.Graph:
    if not _PORTOS:
        return go.Figure()
    return plot_positions(_PORTOS)


def _draw_portfolio_graph_total(_clicks: int) -> dash.dcc.Graph:
    if not _PORTOS:
        return go.Figure()

    index_positions = (
        process_indices(_INDICES, _TRANSACTIONS, [x.portfolio_date for x in _PORTOS])
        if _INDICES and _TRANSACTIONS
        else []
    )

    return plot_returns(_PORTOS, index_positions)


def init_app(app: dash.Dash) -> None:
    """Initialize the application with all plotting callbacks."""
    app.callback(
        Output(ids.PlottingId.GRAPH_TOTAL, "figure"),
        Input(ids.PlottingId.REFRESH, "n_clicks"),
    )(_draw_portfolio_graph_total)

    app.callback(
        Output(ids.PlottingId.GRAPH_RESULT, "figure"),
        Input(ids.PlottingId.REFRESH, "n_clicks"),
    )(_draw_portfolio_graph)

    app.callback(
        Output(ids.PlottingId.REFRESH, "n_clicks"),
        Input(ids.ScrapingId.MODAL, "is_open"),
        State(ids.ScrapingId.FOLDER, "value"),
        State(ids.PlottingId.REFRESH, "n_clicks"),
        prevent_initial_call=False,
    )(_update_portfolios)
