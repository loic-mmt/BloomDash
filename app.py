import dash
from dash import html, dcc

app = dash.Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.H1("BloomDash"),
    # Barre de navigation manuelle entre les pages enregistrées.
    html.Div([
        dcc.Link("Accueil", href="/home"),
        " | ",
        dcc.Link("Markets", href="/markets"),
        " | ",
        dcc.Link("Instrument", href="/instrument"),
        " | ",
        dcc.Link("Screener", href="/screener"),
        " | ",
        dcc.Link("Factor Lab", href="/factor_lab"),
        " | ",
        dcc.Link("Backtester", href="/backtester"),
        " | ",
        dcc.Link("Portfolio", href="/portfolio"),
        " | ",
        dcc.Link("Screener", href="/screener"),
        " | ",
        dcc.Link("Macro", href="/macro"),
        " | ",
        dcc.Link("News", href="/news"),
        " | ",
        dcc.Link("Watchlists", href="/watchlists"),
        " | ",
        dcc.Link("Admin", href="/admin"),
        " | ",
        dcc.Link("Page not found", href="/not_found"),
    ], className="nav-links"),
    html.Hr(),
    # Emplacement où Dash rend la page correspondant à l'URL courante.
    dash.page_container
])

if __name__ == "__main__":
    # debug=True active le rechargement automatique en développement.
    app.run(debug=True)