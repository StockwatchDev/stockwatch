import dash_bootstrap_components as dbc
from dash import dcc, html

from ..ids import HeaderIds, Pages


def _get_index_page() -> html.Div:
    """Get the layout of the stockwatch dash application."""
    return html.Div(
        [
            dbc.NavbarSimple(
                [
                    dbc.NavItem(
                        dbc.NavLink(
                            "Plots", id=HeaderIds.PLOTS, href=Pages.PLOTS, n_clicks=0
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Scraping", id=HeaderIds.SCRAPING, href=Pages.SCRAPING
                        )
                    ),
                    dbc.NavItem(dbc.NavLink("", disabled=True)),
                    dbc.NavItem(
                        dbc.NavLink("About", id=HeaderIds.ABOUT, href=Pages.ABOUT),
                        style={"marginRight": "10em", "marginLeft": "1em"},
                    ),
                ],
                brand="StockWatch",
                brand_href=Pages.PLOTS,
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
