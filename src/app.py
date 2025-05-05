#!/usr/bin/env python
# coding: utf-8
# Dashboard de RETRABALHO para o projeto RA / CEIA-UFG

# Imports básicos
import os
import pandas as pd

# Dotenv
from dotenv import load_dotenv

# Carrega variáveis de ambiente
# env_path="/var/www/ra-retrabalho/src/.env"
# load_dotenv(env_path)
load_dotenv()

# Importar bibliotecas do dash
import dash
import dash_bootstrap_components as dbc
import dash_auth
import dash_mantine_components as dmc
from dash import Dash, _dash_renderer, html, callback, Input, Output, State

# Graficos
import plotly.graph_objs as go
import plotly.io as pio

# Tema
import tema

# Banco de Dados
from db import PostgresSingleton

# Profiler
from werkzeug.middleware.profiler import ProfilerMiddleware

##############################################################################
# CONFIGURAÇÕES BÁSICAS ######################################################
##############################################################################
# Conexão com os bancos
pgDB = PostgresSingleton.get_instance()
pgEngine = pgDB.get_engine()

# Versão do React
_dash_renderer._set_react_version("18.2.0")

# Configurações de cores e temas
TEMA = dbc.themes.LUMEN
pio.templates.default = "plotly"
pio.templates["plotly"]["layout"]["colorway"] = tema.PALETA_CORES

# Stylesheets do Mantine + nosso tema
stylesheets = [
    TEMA,
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css",
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
]

# Scripts
scripts = [
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/dayjs.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/locale/pt.min.js",
    "https://cdn.plot.ly/plotly-locale-pt-br-latest.js",
]

# Seta o tema padrão do plotly
pio.templates["tema"] = go.layout.Template(
    layout=go.Layout(
        font=dict(
            family=tema.FONTE_GRAFICOS,
            size=tema.FONTE_TAMANHO,  # Default font size
        ),
        colorway=tema.PALETA_CORES,
    )
)

# Seta o tema
pio.templates.default = "tema"

##############################################################################
# DASH #######################################################################
##############################################################################

# Dash
app = Dash(
    "Dashboard de OSs",
    # assets_folder="/var/www/ra-retrabalho/src/assets",
    # pages_folder="/var/www/ra-retrabalho/src/pages",
    external_stylesheets=stylesheets,
    external_scripts=scripts,
    use_pages=True,
    suppress_callback_exceptions=True,
)

# Server
server = app.server


# Menu / Navbar
def criarMenu(dirVertical=True):
    return dbc.Nav(
        [dbc.NavLink(page["name"], href=page["relative_path"], active="exact") for page in dash.page_registry.values()],
        vertical=dirVertical,
        pills=True,
    )


# Cabeçalho
header = dmc.Group(
    [
        dmc.Group(
            [
                dmc.Burger(id="burger-button", opened=False, hiddenFrom="md"),
                html.Img(src=app.get_asset_url("logo.png"), height=40),
                dmc.Text(["Peças (RA-UFG)"], size="2.3rem", fw=700),
            ]
        ),
        dmc.Group(
            [
                criarMenu(dirVertical=False),
            ],
            ml="xl",
            gap=0,
            visibleFrom="sm",
        ),
    ],
    justify="space-between",
    style={"flex": 1},
    h="100%",
    px="md",
)

# Corpo do app
app_shell = dmc.AppShell(
    [
        dmc.AppShellHeader(header, p=24, style={"backgroundColor": "#f8f9fa"}),
        dmc.AppShellNavbar(id="navbar", children=criarMenu(dirVertical=True), py="md", px=4),
        dmc.AppShellMain(
            dmc.DatesProvider(
                children=dbc.Container([dash.page_container], fluid=True, className="dbc dbc-ag-grid"),
                settings={"locale": "pt"},
            ),
        ),
    ],
    header={"height": 90},
    navbar={
        "width": 300,
        "breakpoint": "sm",
        "collapsed": {"desktop": True, "mobile": True},
    },
    padding="md",
    id="app-shell",
)

app.layout = dmc.MantineProvider(app_shell)


@callback(
    Output("app-shell", "navbar"),
    Input("burger-button", "opened"),
    State("app-shell", "navbar"),
)
def toggle_navbar(opened, navbar):
    navbar["collapsed"] = {"mobile": not opened, "desktop": True}
    return navbar


##############################################################################
# Auth #######################################################################
##############################################################################
df_users = pd.read_sql("SELECT * FROM users_ra_dash", pgEngine)
dict_users = df_users.set_index("ra_username")["ra_password"].to_dict()
SECRET_KEY = os.getenv("SECRET_KEY")

auth = dash_auth.BasicAuth(app, dict_users, secret_key=SECRET_KEY)

##############################################################################
# MAIN #######################################################################
##############################################################################
if __name__ == "__main__":
    APP_HOST = os.getenv("HOST", "0.0.0.0")
    APP_DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    APP_PORT = os.getenv("PORT", 10000)

    PROFILE = os.getenv("PROFILE", "False").lower() in ("true", "1", "yes")
    PROF_DIR = os.getenv("PROFILE_DIR", "profile")

    if PROFILE:
        app.server.config["PROFILE"] = True
        app.server.wsgi_app = ProfilerMiddleware(
            app.server.wsgi_app,
            sort_by=["cumtime"],
            restrictions=[50],
            stream=None,
            profile_dir=PROF_DIR,
        )

    app.run(host=APP_HOST, debug=APP_DEBUG, port=APP_PORT)
