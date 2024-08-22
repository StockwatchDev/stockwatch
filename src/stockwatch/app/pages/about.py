"""The about page specification."""

import dash_bootstrap_components as dbc
from dash import dcc, html

_ABOUT_TEXT = """
# About
The stockwatch application, your tool for getting unpresidented returns and
insights into your investments on the DeGiro website.

# Contributors
* Jorik de Vries
* Robin de Vries
* Theo de Vries
"""


def _get_layout() -> html.Div:
    return html.Div(
        dbc.Container(
            dbc.Row(dbc.Col(dcc.Markdown(_ABOUT_TEXT))),
        ),
    )


layout = _get_layout()
