from pathlib import Path

from dash import dcc, html


def get_layout(folder: Path) -> html.Div:
    return html.Div(
        children=[
            html.Div(
                [
                    html.H1(children="Stockwatch"),
                    html.Div(children="Analysis of your DeGiro portfolio."),
                ],
                id="header",
            ),
            dcc.Input(id="folder-selected", type="text", value=f"{folder}"),
            html.Button("refresh", n_clicks=0, id="portfolio-refresh-folder"),
            html.Button("", n_clicks=0, id="portfolio-refresh", hidden=True),
            html.Div([
                html.Hr(),
                html.H2("Portfolio"),
                dcc.Graph(id="portfolio-graph", style={"width": "100%", "height": "700px"}),
                ],
            ),
            html.Div([
                html.Hr(),
                html.H2("Portfolio (Totals)"),
                dcc.Graph(id="portfolio-graph-total", style={"width": "100%", "height": "700px"}),
                ],
            ),
        ]
    )
