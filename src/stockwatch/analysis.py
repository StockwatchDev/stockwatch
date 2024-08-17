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
    for isin, name in positions_data.isins_and_names:
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


def plot_returns_comparison(
    share_portfolios: tuple[SharePortfolio, ...],
    _indices: list[tuple[SharePosition, ...]] | None = None,
    end_date: datetime.date = datetime.date.today(),
) -> go.Figure:
    """Plot the returns of a portfolio."""
    start_date = end_date - datetime.timedelta(weeks=52)
    start_date_long = start_date - datetime.timedelta(weeks=52)
    start_date_short = start_date - datetime.timedelta(weeks=4)

    long_pf_it = iter(share_portfolios)
    while next(long_pf_it).portfolio_date < start_date_long:
        pass

    short_pf_it = iter(share_portfolios)
    while next(short_pf_it).portfolio_date < start_date_short:
        pass

    current_pf_it = iter(share_portfolios)
    while next(current_pf_it).portfolio_date < start_date:
        pass

    fig_dict = {"data": [], "layout": {}, "frames": []}

    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [
                        None,
                        {
                            "frame": {"duration": 1, "redraw": False},
                            "fromcurrent": True,
                            "transition": {
                                "duration": 50,
                                "easing": "quadratic-in-out",
                            },
                        },
                    ],
                    "label": "Play",
                    "method": "animate",
                },
                {
                    "args": [
                        [None],
                        {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0},
                        },
                    ],
                    "label": "Pause",
                    "method": "animate",
                },
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top",
        }
    ]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Date:",
            "visible": True,
            "xanchor": "right",
        },
        "transition": {"duration": 50, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": [],
    }

    for pf in share_portfolios:
        if pf.portfolio_date >= end_date:
            max_marker_size = max([i.value.value for i in pf.share_positions])
            break
    else:
        max_marker_size = max(
            i.value.value for i in share_portfolios[-1].share_positions
        )

    size_ref = 2 * max_marker_size / (60**2)

    min_x, min_y, max_x, max_y = (
        float("inf"),
        float("inf"),
        float("-inf"),
        float("-inf"),
    )

    while True:
        current_pf = next(current_pf_it, None)
        long_pf = next(long_pf_it)
        short_pf = next(short_pf_it)
        if current_pf is None or current_pf.portfolio_date > end_date:
            break

        frame = {"data": [], "name": f"{current_pf.portfolio_date}"}
        for current_pos in current_pf.share_positions:
            long_pos = long_pf.get_position(current_pos.isin)
            if long_pos.is_empty:
                continue
            short_pos = short_pf.get_position(current_pos.isin)
            if short_pos.is_empty:
                continue

            short_val = (
                100.0
                * (current_pos.price.value_exact - short_pos.price.value_exact)
                / short_pos.price.value_exact
            )
            min_y = min(min_y, short_val)
            max_y = max(max_y, short_val)
            long_val = (
                100.0
                * (current_pos.price.value_exact - long_pos.price.value_exact)
                / long_pos.price.value_exact
            )
            min_x = min(min_x, long_val)
            max_x = max(max_x, long_val)

            hovertemplate = (
                f"<b>{current_pos.name} - {current_pos.isin}</b><br>returns short: %{{y:0.2f}}<br>"
                f"returns long: %{{x:0.2f}}<extra></extra>"
            )
            data_dict = {
                "x": [long_val],
                "y": [short_val],
                "mode": "markers",
                "marker": {
                    "size": [current_pos.value.value_exact],
                    "sizemode": "area",
                    "sizeref": size_ref,
                    "sizemin": 4,
                },
                "name": current_pos.isin,
                "hovertemplate": hovertemplate,
            }
            frame["data"].append(data_dict)

        fig_dict["frames"].append(frame)

        slider_step = {
            "args": [
                [current_pf.portfolio_date],
                {
                    "frame": {"duration": 1, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 1},
                },
            ],
            "label": f"{current_pf.portfolio_date}",
            "method": "animate",
        }
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]

    # short = []
    # long = []
    # marker_sizes = []
    # names = []
    # isins = []
    # long_portfolio = None
    # short_portfolio = None
    # current_portfolio = share_portfolios[-1]

    # for portfolio in share_portfolios:
    #     if portfolio.portfolio_date == start_date_long:
    #         long_portfolio = portfolio

    #     if portfolio.portfolio_date == start_date_short:
    #         short_portfolio = portfolio

    # if long_portfolio is None or short_portfolio is None:
    #     return go.Figure()

    # for long_pos in long_portfolio.share_positions:
    #     short_pos = short_portfolio.get_position(long_pos.isin)
    #     current_pos = current_portfolio.get_position(long_pos.isin)

    #     if short_pos.is_empty or current_pos.is_empty:
    #         continue

    #     short_val = (
    #         100.0
    #         * (current_pos.price.value_exact - short_pos.price.value_exact)
    #         / short_pos.price.value_exact
    #     )
    #     long_val = (
    #         100.0
    #         * (current_pos.price.value_exact - long_pos.price.value_exact)
    #         / long_pos.price.value_exact
    #     )

    #     marker_sizes.append(current_pos.value.value_exact)
    #     short.append(short_val)
    #     long.append(long_val)
    #     isins.append(long_pos.isin)
    #     names.append(long_pos.name)

    # size_ref = 2 * max(marker_sizes) / (60**2)

    # # make data
    # for x, y, marker_size, isin, name in zip(long, short, marker_sizes, isins, names):
    #     hovertemplate = (
    #         f"<b>{name} - {isin}</b><br>returns short: %{{y:0.2f}}<br>"
    #         f"returns long: %{{x:0.2f}}<extra></extra>"
    #     )
    #     data_dict = {
    #         "x": [x],
    #         "y": [y],
    #         "mode": "markers",
    #         "marker": {
    #             "size": [marker_size],
    #             "sizemode": "area",
    #             "sizeref": size_ref,
    #             "sizemin": 4,
    #         },
    #         "name": isin,
    #         "hovertemplate": hovertemplate,
    #     }

    fig_dict["data"] = fig_dict["frames"][0]["data"].copy()

    # fill in most of layout
    fig_dict["layout"]["xaxis"] = {
        "title": "Returns [%] in 52 weeks",
        "range": [min_x - 1, max_x + 1],
    }
    fig_dict["layout"]["yaxis"] = {
        "title": "Returns [%] in 4 weeks",
        "range": [min_y - 1, max_y + 1],
    }

    fig = go.Figure(fig_dict)

    return fig

    # fig.add_trace(
