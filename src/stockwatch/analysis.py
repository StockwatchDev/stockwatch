"""This module provides methods for visualizing various aspects of share portfolios.

This package has a clean architecture. This module should not contain any business- or
application logic, nor any adapters.
"""

import datetime

import plotly.graph_objects as go

from .adapters import PositionsData, ReturnsData
from .entities.shares import SharePortfolio, SharePosition, get_all_isins


_SECONDS_IN_DAY = 60 * 60 * 24
_MARKET_DAYS_PER_YEAR = 260


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
    start_date: datetime.date = datetime.date.today() - datetime.timedelta(weeks=52),
    end_date: datetime.date = datetime.date.today(),
    period_1: datetime.timedelta = datetime.timedelta(weeks=52),
    period_2: datetime.timedelta = datetime.timedelta(weeks=4),
) -> go.Figure:
    """Plot the returns of a portfolio."""
    long_period = max(period_1, period_2)
    weeks_long_period = long_period.total_seconds() / (_SECONDS_IN_DAY * 7)
    short_period = min(period_1, period_2)
    weeks_short_period = short_period.total_seconds() / (_SECONDS_IN_DAY * 7)
    start_date_long = start_date - long_period - datetime.timedelta(days=1)

    _all_isins = get_all_isins(share_portfolios, start_date, end_date)

    long_pf_it = iter(share_portfolios)
    while (start_date_long_act := next(long_pf_it).portfolio_date) < start_date_long:
        pass

    start_date_act = start_date_long_act + long_period
    start_date_short_act = start_date_act - short_period

    short_pf_it = iter(share_portfolios)
    while next(short_pf_it).portfolio_date < start_date_short_act:
        pass

    current_pf_it = iter(share_portfolios)
    while next(current_pf_it).portfolio_date < start_date_act:
        pass

    fig_dict = {"data": [], "layout": {}, "frames": []}

    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [
                        None,
                        {
                            "frame": {"duration": 500, "redraw": False},
                            "fromcurrent": True,
                            "transition": {
                                "duration": 400,
                                "easing": "linear",
                            },
                            "easing": "linear",
                            "mode": "next",
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
            "prefix": "Date: ",
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
            max_marker_size = max(
                [i.value.value for i in pf.share_positions if i.isin in _all_isins]
            )
            break
    else:
        max_marker_size = max(
            i.value.value
            for i in share_portfolios[-1].share_positions
            if i.isin in _all_isins
        )

    size_ref = 2 * max_marker_size / (60**2)

    min_long, min_short, max_long, max_short = (
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

        if current_pf.portfolio_date.weekday() in (5, 6):
            continue

        frame = {"data": [], "name": f"{current_pf.portfolio_date}"}
        # for current_pos in current_pf.share_positions:
        for isin in _all_isins:
            current_pos = current_pf.get_position(isin)
            long_pos = long_pf.get_position(current_pos.isin)
            short_pos = short_pf.get_position(current_pos.isin)

            if current_pos.is_empty or long_pos.is_empty or short_pos.is_empty:
                short_val = -10000.0
                long_val = -10000.0
                marker_size = 40
                marker_opacity = 0.0
            else:
                # investment-based:
                short_investment = current_pos.investment + short_pos.unrealized
                short_val = (
                    100.0
                    * 52
                    * (current_pos.value.value_exact - short_investment.value_exact)
                    / (short_investment.value_exact * weeks_short_period)
                )
                # market-based:
                # short_val = (
                #     100.0
                #     * 52
                #     * (current_pos.price.value_exact - short_pos.price.value_exact)
                #     / (short_pos.price.value_exact * weeks_short_period)
                # )
                min_short = min(min_short, short_val)
                max_short = max(max_short, short_val)
                # investment-based:
                long_investment = current_pos.investment + long_pos.unrealized
                long_val = (
                    100.0
                    * 52
                    * (current_pos.value.value_exact - long_investment.value_exact)
                    / (long_investment.value_exact * weeks_long_period)
                )
                # market-based:
                # long_val = (
                #     100.0
                #     * 52
                #     * (current_pos.price.value_exact - long_pos.price.value_exact)
                #     / (long_pos.price.value_exact * weeks_long_period)
                # )
                min_long = min(min_long, long_val)
                max_long = max(max_long, long_val)
                marker_size = current_pos.value.value_exact
                marker_opacity = 0.6

            hovertemplate = (
                f"<b>{current_pos.name} - {current_pos.isin}</b><br>returns short: %{{x:0.2f}}<br>"
                f"returns long: %{{y:0.2f}}<extra></extra>"
            )
            data_dict = {
                "y": [long_val],
                "x": [short_val],
                "mode": "markers",
                "marker": {
                    "size": [marker_size],
                    "sizemode": "area",
                    "sizeref": size_ref,
                    "sizemin": 4,
                    "opacity": [marker_opacity],
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

    # set the data for the initial display to that of the initial frame
    fig_dict["data"] = fig_dict["frames"][0]["data"].copy()

    # fill in most of layout
    fig_dict["layout"]["sliders"] = [sliders_dict]
    fig_dict["layout"]["yaxis_scaleanchor"] = "x"
    long_range_extra = 0.05 * (max_long - min_long)
    short_range_extra = 0.05 * (max_short - min_short)
    fig_dict["layout"]["xaxis"] = {
        "title": f"Annualized returns [%] in {short_period.days} days",
        "range": [min_short - short_range_extra, max_short + short_range_extra],
    }
    fig_dict["layout"]["yaxis"] = {
        "title": f"Annualized returns [%] in {long_period.days} days",
        "range": [min_long - long_range_extra, max_long + long_range_extra],
    }

    fig = go.Figure(fig_dict)

    return fig
