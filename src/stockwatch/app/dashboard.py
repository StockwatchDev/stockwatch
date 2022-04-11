"""This module provides a dashboard for analysis of share portfolios.

The dashboard is defined by connecting widgets, events, etc. as defined in layout
to methods provided by analysis and use_cases.

This package has a clean architecture. This module should not contain any business- or
application logic, nor any adapters.
"""
from pathlib import Path

import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy, MultiplexerTransform

from . import layout, plotting, scraping


def run_blocking(folder: Path) -> None:
    """Run the dash application."""
    app = DashProxy(
        __name__,
        external_stylesheets=[dbc.themes.SIMPLEX],
        transforms=[MultiplexerTransform()],
    )
    app.layout = layout.get_layout(folder)

    scraping.init_app(app)
    plotting.init_app(app)

    app.run_server(debug=True)
