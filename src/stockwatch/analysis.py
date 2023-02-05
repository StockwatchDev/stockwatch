"""This module provides methods for visualizing various aspects of share portfolios.

This package has a clean architecture. This module should not contain any business- or
application logic, nor any adapters.
"""
import datetime

import plotly.graph_objects as go

from .adapters import PositionsData, ReturnsData
from .entities.shares import SharePortfolio, SharePosition


def _create_figure() -> go.Figure:
    return go.Figure(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin={"l": 50, "r": 50, "b": 50, "t": 50, "pad": 4},
            legend={
                "yanchor": "top",
                "y": 0.99,
                "xanchor": "left",
                "x": 0.01,
                "bgcolor": "white",
            },
        ),
    )


def _add_plot_returns_line(
    fig: go.Figure,
    dates: list[datetime.date],
    data: list[float],
    title: str,
    color: str,
) -> None:
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[i - data[0] for i in data],
            hovertemplate=f"<b>{title}: </b>€%{{y:0.2f}}<extra></extra>",
            name=title,
            line={"color": color, "width": 2.0},
            legendrank=2,
            legendgroup="indexes",
            legendgrouptitle_text="Returns",
        )
    )


def plot_returns(
    share_portfolios: tuple[SharePortfolio, ...],
    indices: list[tuple[SharePosition, ...]] | None = None,
) -> go.Figure:
    """Plot the returns of a portfolio."""
    returns_data = ReturnsData.from_portfolios(share_portfolios)

    fig = _create_figure()
    fig.update_layout(hovermode="x unified")

    fig.add_trace(
        go.Scatter(
            x=returns_data.dates,
            y=returns_data.investments,
            hovertemplate="<b>invested: </b>€%{y:0.2f}<extra></extra>",
            name="Investments",
            mode="none",
            fill="tozeroy",
            line={"width": 0.5},
            legendrank=2,
            legendgroup="portfolio",
            legendgrouptitle_text="Portfolio",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=returns_data.dates,
            y=returns_data.totals,
            hovertemplate="<b>total: </b>€%{y:0.2f}<extra></extra>",
            name="Totals",
            mode="none",
            fill="tonexty",
            line={"width": 0.5},
            legendrank=3,
            legendgroup="portfolio",
            legendgrouptitle_text="Portfolio",
        )
    )
    _add_plot_returns_line(
        fig, returns_data.dates, returns_data.realized_returns, "Realized", "green"
    )
    _add_plot_returns_line(
        fig, returns_data.dates, returns_data.unrealized_returns, "Unrealized", "blue"
    )
    _add_plot_returns_line(
        fig, returns_data.dates, returns_data.returns, "Returns", "black"
    )

    if indices:
        for index in indices:
            index_name = index[0].name
            fig.add_trace(
                go.Scatter(
                    x=[x.position_date for x in index],
                    y=[p.value - p.investment for p in index],
                    hovertemplate=f"<b>{index_name}: </b>€%{{y:0.2f}}<extra></extra>",
                    name=index_name,
                    line={"width": 2.0},
                    legendrank=1,
                    legendgroup="indexes",
                    legendgrouptitle_text="Indexes",
                )
            )

    return fig


def plot_positions(share_portfolios: tuple[SharePortfolio, ...]) -> go.Figure:
    """Plot the value of all positions in the portfolios through time."""

    positions_data = PositionsData.from_portfolios(share_portfolios)

    fig = _create_figure()
    for (isin, name) in positions_data.isins_and_names:
        hovertemplate = (
            f"<b>{name} - {isin}</b><br>value €%{{y:0.2f}}<br>"
            f"date: %{{x}}<extra></extra>"
        )
        # vertical axis to be the value of each position in the portfolio
        fig.add_trace(
            go.Scatter(
                x=positions_data.dates,
                y=positions_data.isins_and_values[isin],
                hovertemplate=hovertemplate,
                name=isin,
                mode="lines",
                line={"width": 0.5},
                stackgroup="one",
            )
        )
    return fig
