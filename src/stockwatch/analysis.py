"""This module provides methods for visualizing various aspects of share portfolios.

This package has a clean architecture. This module should not contain any business- or
application logic, nor any adapters.
"""
import plotly.graph_objects as go

from .adapters import positions_plotdata, returns_plotdata
from .entities import SharePortfolio, SharePosition


def _create_figure() -> go.Figure:
    return go.Figure(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=50, r=50, b=50, t=50, pad=4),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="white"),
        ),
    )


def plot_returns(
    share_portfolios: tuple[SharePortfolio, ...],
    indices: list[tuple[SharePosition, ...]] | None = None,
) -> go.Figure:
    """Plot the returns of a portfolio."""
    returns_data = returns_plotdata(share_portfolios)

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
            line=dict(width=0.5),
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
            line=dict(width=0.5),
            legendrank=3,
            legendgroup="portfolio",
            legendgrouptitle_text="Portfolio",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=returns_data.dates,
            y=returns_data.returns,
            hovertemplate="<b>returns: </b>€%{y:0.2f}<extra></extra>",
            name="Returns",
            line=dict(color="black", width=2.0),
            legendrank=2,
            legendgroup="indexes",
            legendgrouptitle_text="Returns",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=returns_data.dates,
            y=returns_data.unrealized_returns,
            hovertemplate="<b>unrealized: </b>€%{y:0.2f}<extra></extra>",
            name="Unrealized returns",
            line=dict(color="blue", width=2.0),
            legendrank=2,
            legendgroup="indexes",
            legendgrouptitle_text="Returns",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=returns_data.dates,
            y=returns_data.realized_returns,
            hovertemplate="<b>realized: </b>€%{y:0.2f}<extra></extra>",
            name="Realized returns",
            line=dict(color="green", width=2.0),
            legendrank=2,
            legendgroup="indexes",
            legendgrouptitle_text="Returns",
        )
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
                    line=dict(width=2.0),
                    legendrank=1,
                    legendgroup="indexes",
                    legendgrouptitle_text="Indexes",
                )
            )

    return fig


def plot_positions(share_portfolios: tuple[SharePortfolio, ...]) -> go.Figure:
    """Plot the value of all positions in the portfolios through time."""

    positions_data = positions_plotdata(share_portfolios)

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
                line=dict(width=0.5),
                stackgroup="one",
            )
        )
    return fig
