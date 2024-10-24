"""This module provides a dashboard for analysis of share portfolios.

The dashboard is defined by connecting widgets, events, etc. as defined in layout
to methods provided by analysis and use_cases.

This package has a clean architecture. This module should not contain any business- or
application logic, nor any adapters.
"""

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, callback, html

from . import pages
from .ids import HeaderIds, PageIds
from stockwatch.use_cases.configuring import DashServerConfig


@callback(Output(HeaderIds.CONTENT, "children"), Input(HeaderIds.LOCATION, "pathname"))
def _switch_page(pathname: str) -> html.Div:
    match pathname:
        case PageIds.PLOTS:
            return pages.plots.layout
        case PageIds.SCRAPING:
            return pages.scraping.layout
        case PageIds.ABOUT:
            return pages.about.layout
        case _:
            return pages.plots.layout


def run_blocking() -> None:
    """Run the dash application."""
    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.SIMPLEX],
        prevent_initial_callbacks=True,
    )
    pages.scraping.init_layout()

    app.layout = pages.index.layout
    app.validation_layout = html.Div(
        [
            pages.index.layout,
            pages.scraping.layout,
            pages.plots.layout,
            pages.about.layout,
        ],
    )

    # Dash uses werkzeug and the reloader functionality causes the application to be
    # started twice, see https://stackoverflow.com/questions/25504149/why-does-running-the-flask-dev-server-run-itself-twice
    # Disable reloading via the config if you want to prevent that
    app.run(
        debug=DashServerConfig.get().debug,
        use_reloader=DashServerConfig.get().use_reloader,
    )
