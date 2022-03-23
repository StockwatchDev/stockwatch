"""
This module provides methods for visualizing various aspects of share portfolios.

This package has a clean architecture. This module should not contain any business- or 
application logic, nor any adapters.
"""
from .entities import SharePortfolio
from .adapters import returns_plotdata, positions_plotdata

import plotly.graph_objects as go


def plot_returns(share_portfolios: tuple[SharePortfolio, ...]) -> go.Figure:
    returns_data = returns_plotdata(share_portfolios)

    fig = go.Figure()
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
        )
    )
    fig.add_trace(
        go.Scatter(
            x=returns_data.dates,
            y=returns_data.returns,
            hovertemplate="<b>returns: </b>€%{y:0.2f}<extra></extra>",
            name="Returns",
            line=dict(color="black", width=2.0),
            legendrank=1,
        )
    )
    fig.update_layout(hovermode="x unified")
    return fig


def plot_positions(share_portfolios: tuple[SharePortfolio, ...]) -> go.Figure:
    """
    Plot the value of all positions in the portfolios through time
    """

    positions_data = positions_plotdata(share_portfolios)

    fig = go.Figure()
    for (isin, name) in positions_data.isins_and_names:
        hovertemplate = f"<b>{name} - {isin}</b><br>value €%{{y:0.2f}}<br>date: %{{x}}<extra></extra>"
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
