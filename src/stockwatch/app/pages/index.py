"""Dash app callbacks for the index/home page."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from stockwatch.app.ids import HeaderIds, PageIds


def _get_index_page() -> html.Div:
    """Get the layout of the stockwatch dash application."""
    return html.Div(
        [
            dbc.NavbarSimple(
                [
                    dbc.NavItem(
                        dbc.NavLink(
                            "Portfolio",
                            id=HeaderIds.PORTFOLIO,
                            href=PageIds.PORTFOLIO,
                            n_clicks=0,
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Returns",
                            id=HeaderIds.RETURNS,
                            href=PageIds.RETURNS,
                            n_clicks=0,
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Scraping", id=HeaderIds.SCRAPING, href=PageIds.SCRAPING
                        )
                    ),
                    dbc.NavItem(dbc.NavLink("", disabled=True)),
                    dbc.NavItem(
                        dbc.NavLink("About", id=HeaderIds.ABOUT, href=PageIds.ABOUT),
                        style={"marginRight": "10em", "marginLeft": "1em"},
                    ),
                ],
                brand="StockWatch",
                brand_href=PageIds.PORTFOLIO,
                color="dark",
                dark=True,
                fluid=False,
                sticky="top",
                style={"marginBottom": "2em"},
            ),
            dcc.Location(id=HeaderIds.LOCATION, refresh=False),
            html.Div(id=HeaderIds.CONTENT),
        ]
    )


layout = _get_index_page()
