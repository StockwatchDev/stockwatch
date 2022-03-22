from .entities import *
from .adapters import *

import plotly.graph_objects as go


def plot_returns(share_portfolios: tuple[SharePortfolio, ...]) -> go.Figure:
    dates, investments, totals, returns = returns_plotdata(share_portfolios)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=investments,
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
            x=dates,
            y=totals,
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
            x=dates,
            y=returns,
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

    dates, sorted_isins_and_names_list, values_dict = positions_plotdata(
        share_portfolios
    )

    fig = go.Figure()
    for (isin, name) in sorted_isins_and_names_list:
        hovertemplate = f"<b>{name} - {isin}</b><br>value €%{{y:0.2f}}<br>date: %{{x}}<extra></extra>"
        # vertical axis to be the value of each position in the portfolio
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values_dict[isin],
                hovertemplate=hovertemplate,
                name=isin,
                mode="lines",
                line=dict(width=0.5),
                stackgroup="one",
            )
        )
    return fig
