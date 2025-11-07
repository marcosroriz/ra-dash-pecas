#!/usr/bin/env python
# coding: utf-8

# Dashboard de RETRABALHO para o projeto RA / CEIA-UFG
# Versão com autenticação de login/logout implementada usando dcc.Store.

##############################################################################
# 1. IMPORTAÇÕES #############################################################
##############################################################################

# Imports básicos
import os
import pandas as pd
import hashlib # Para fazer o hash da senha de forma segura (boa prática)

# Dotenv: Carrega variáveis de ambiente (ex: HOST, PORT, SECRET_KEY)
from dotenv import load_dotenv
load_dotenv()

# Importar bibliotecas do dash
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
# Componentes Dash essenciais para o roteamento e estado de sessão
from dash import Dash, _dash_renderer, html, dcc, callback, Input, Output, State, ALL 

# Graficos
import plotly.graph_objs as go
import plotly.io as pio

# Tema e Banco de Dados (imports locais)
import tema
from db import PostgresSingleton

# Profiler
from werkzeug.middleware.profiler import ProfilerMiddleware

##############################################################################
# 2. CONFIGURAÇÃO DE TEMAS, BANCO DE DADOS E VARIÁVEIS #######################
##############################################################################

# Conexão com os bancos
pgDB = PostgresSingleton.get_instance()
pgEngine = pgDB.get_engine()

# Versão do React (garante compatibilidade)
_dash_renderer._set_react_version("18.2.0")

# Configurações de cores e temas
TEMA = dbc.themes.LUMEN
pio.templates.default = "plotly"
pio.templates["plotly"]["layout"]["colorway"] = tema.PALETA_CORES

# Stylesheets do Mantine + Bootstrap
stylesheets = [
    TEMA, # Tema principal
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css",
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
]

# Scripts (para formatação de data e gráficos)
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
            size=tema.FONTE_TAMANHO,
        ),
        colorway=tema.PALETA_CORES,
    )
)
pio.templates.default = "tema"

##############################################################################
# 3. INICIALIZAÇÃO DO DASH APP ###############################################
##############################################################################

# Dash App
app = Dash(
    "Dashboard de OSs",
    external_stylesheets=stylesheets,
    external_scripts=scripts,
    use_pages=True, # Habilita o sistema de multi-páginas (pages/)
    suppress_callback_exceptions=True, # Essencial para layouts dinâmicos (login/dashboard)
)

# Servidor Flask subjacente
server = app.server

# Carrega os usuários do banco e cria um dicionário simples (username: password)
df_users = pd.read_sql("SELECT * FROM users_ra_dash", pgEngine)
dict_users = df_users.set_index("ra_username")["ra_password"].to_dict()

##############################################################################
# 4. DEFINIÇÃO DE COMPONENTES DE LAYOUT ######################################
##############################################################################

# Função que cria o Menu/Navbar (para Desktop e Mobile)
def criarMenu(dirVertical=True):
    return dbc.Nav(
        # Mapeia todas as páginas registradas no dash.page_registry
        [dbc.NavLink(page["name"], href=page["relative_path"], active="exact") for page in dash.page_registry.values()],
        vertical=dirVertical,
        pills=True,
    )

# Layout do Cabeçalho (Header)
header = dmc.Group(
    [
        # Grupo Esquerdo: Burger, Logo e Título
        dmc.Group(
            [
                dmc.Burger(id="burger-button", opened=False, hiddenFrom="md"),
                # MODIFICADO: Aplicando um estilo de altura explícito (60px) para garantir o dimensionamento correto da logo.
                html.Img(src=app.get_asset_url("logo.png"), style={'height': '60px', 'width': 'auto'}),
                dmc.Text(["Peças (RA-UFG)"], size="2.3rem", fw=700),
            ]
        ),
        # Grupo Direito: Menu de Navegação e Botão de Sair (Logout)
        dmc.Group(
            [
                criarMenu(dirVertical=False),
                # Botão de Logout adicionado (ID 'logout-button' é usado no callback)
                dbc.Button("Sair", id="logout-button", color="danger", className="ms-3", size="sm"),
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

# Layout do Dashboard (Componente Principal que só aparece se logado)
dashboard_layout = dmc.AppShell(
    [
        dmc.AppShellHeader(header, p=24, style={"backgroundColor": "#f8f9fa"}),
        dmc.AppShellNavbar(id="navbar", children=criarMenu(dirVertical=True), py="md", px=4),
        dmc.AppShellMain(
            dmc.DatesProvider(
                # dash.page_container é onde o conteúdo das páginas individuais é renderizado
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

# Layout da Página de Login (O que aparece para usuários deslogados)
login_layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            [ 
                # CARD PARA AS LOGOS (Fundo Branco em destaque)
                dbc.Card([
                    dbc.CardBody([
                        dmc.Group([
                            # Logo 1
                            html.Img(
                                src=app.get_asset_url("logo.png"),
                                style={
                                    "maxWidth": "45%", 
                                    "height": "80px",
                                    "objectFit": "contain",
                                    "marginRight": "10px"
                                }
                            ),
                            # Logo 2
                            html.Img(
                                src=app.get_asset_url("rpido_araguaia_logo.jpg"),
                                style={
                                    "maxWidth": "45%", 
                                    "height": "100px",
                                    "objectFit": "contain"
                                }
                            ),
                        ], justify="center", className="mb-0"),
                    ]),
                # Estilo: Fundo branco explícito para o card das logos.
                ], className="mb-4 shadow", style={"background-color": "white"}),
                
                # CARD PRINCIPAL DO LOGIN
                dbc.Card([
                    dbc.CardBody([
                        # Título CORRIGIDO: usa ta="center" em vez de align="center"
                        dmc.Title("Dashboard de Peças (RA-UFG)", order=2, ta="center", className="mb-1"),

                        html.Hr(className="mb-4"),

                        # Inputs com Mantine
                        dmc.TextInput(
                            id="username-input", 
                            placeholder="Usuário", 
                            label="Usuário",
                            size="md",
                            className="mb-3",
                            required=True
                        ),
                        dmc.PasswordInput(
                            id="password-input", 
                            placeholder="Senha", 
                            label="Senha", 
                            size="md",
                            className="mb-4",
                            required=True
                        ),

                        # Botão
                        dbc.Button(
                            "Entrar", 
                            id="login-button", 
                            color="primary", 
                            n_clicks=0, 
                            className="w-100",
                            size="lg"
                        ),
                        html.Div(id="login-alert", className="mt-4")
                    ])
                ], className="shadow"), 
            ],
            # Coluna com tamanho fixo para telas maiores, centralizando o formulário
            width=12, sm=10, md=8, lg=5, xl=4
        )
    ], justify="center", align="center", className="vh-100")
# Fundo: Adicionado um estilo com gradiente suave
], fluid=True, style={
    "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)", 
    "min-height": "100vh"
})

##############################################################################
# 5. LAYOUT PRINCIPAL E ELEMENTOS DE SESSÃO ##################################
##############################################################################

# O layout principal é apenas um contêiner para os componentes de roteamento e sessão
app.layout = dmc.MantineProvider([
    # dcc.Store: Armazena o estado de login no navegador. 'session' apaga ao fechar a aba.
    dcc.Store(id='session-store', storage_type='session'),
    
    # dcc.Location: Lê a URL atual para gerenciar o roteamento
    dcc.Location(id='url', refresh=False),
    
    # html.Div: É o "slot" onde o login_layout ou o dashboard_layout será renderizado
    html.Div(id='page-content')
])


##############################################################################
# 6. CALLBACKS DE INTERAÇÃO E AUTENTICAÇÃO ###################################
##############################################################################

# Callback para o Burger Button (Exibe/Oculta a Navbar em dispositivos móveis)
@callback(
    Output("app-shell", "navbar"),
    Input("burger-button", "opened"),
    State("app-shell", "navbar"),
)
def toggle_navbar(opened, navbar):
    # Lógica que muda a propriedade 'collapsed' da navbar
    navbar["collapsed"] = {"mobile": not opened, "desktop": True}
    return navbar


# Callback para Lógica de Login (Trata clique do botão e a tecla ENTER)
@callback(
    [Output('session-store', 'data'),
     Output('login-alert', 'children')],
    [Input('login-button', 'n_clicks'),
     Input('username-input', 'n_submit'),  # Dispara quando Enter é pressionado no campo Usuário
     Input('password-input', 'n_submit')], # Dispara quando Enter é pressionado no campo Senha
    [State('username-input', 'value'),
     State('password-input', 'value')]
)
def handle_login(n_clicks, n_submit_username, n_submit_password, username, password):
    # Usa dash.callback_context para saber qual componente ativou o callback
    ctx = dash.callback_context
    trigger_id = ctx.triggered_id if ctx.triggered else None

    # 1. Primeira verificação: se não foi acionado por um input relevante, sai
    if not trigger_id:
        return dash.no_update, ""
    
    # 2. Verifica se os campos estão vazios
    if not username or not password:
        alert = dbc.Alert("Preencha o nome de usuário e a senha.", color="warning", dismissable=True)
        return dash.no_update, alert

    # 3. Lógica de Autenticação (Aqui você usaria um sistema de hash mais robusto)
    if username in dict_users and dict_users[username] == password:
        # Login bem-sucedido: Salva o estado de logado e o username na sessão
        session_data = {'is_logged_in': True, 'username': username}
        return session_data, ""
    else:
        # Login falhou
        alert = dbc.Alert("Usuário ou senha inválidos.", color="danger", dismissable=True)
        return dash.no_update, alert


# Callback para Lógica de Logout
@callback(
    # Usamos allow_duplicate=True porque o Output('session-store', 'data') também é um Output do handle_login
    [Output('session-store', 'data', allow_duplicate=True),
     Output('url', 'pathname', allow_duplicate=True)], # Força o roteador a recarregar o conteúdo
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """
    Limpa o dcc.Store de sessão (deslogando o usuário) e o redireciona.
    """
    if n_clicks and n_clicks > 0:
        # 1. Limpa o store da sessão (setando para None)
        # 2. Força o redirecionamento para a página inicial ('/')
        return None, '/'
    
    return dash.no_update, dash.no_update


# Callback ROTEADOR CENTRAL (O Porteiro): Decide se mostra o Login ou o Dashboard
@callback(
    Output('page-content', 'children'),
    [Input('session-store', 'data'), # Monitora o estado de login
     Input('url', 'pathname')]        # Monitora qual URL o usuário está tentando acessar
)
def display_page(session_data, pathname):
    
    # 1. VERIFICAÇÃO DE SEGURANÇA: Se não há dados de sessão válidos, exibe o login
    if not session_data or not session_data.get('is_logged_in'):
        # Independentemente da URL, o usuário vê a página de login
        return login_layout
    
    # 2. VERIFICAÇÃO DE REDIRECIONAMENTO: Se o usuário está logado, mas tenta ir para /login, redireciona para a home
    if pathname == '/login':
        return dcc.Location(pathname='/', id='redirect-to-home')
    
    # 3. CONTEÚDO LIBERADO: Se o usuário está logado, exibe o dashboard completo
    return dashboard_layout

##############################################################################
# 7. EXECUÇÃO PRINCIPAL ######################################################
##############################################################################

if __name__ == "__main__":
    APP_HOST = os.getenv("HOST", "0.0.0.0")
    APP_DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    APP_PORT = os.getenv("PORT", 10000)
    PROFILE = os.getenv("PROFILE", "False").lower() in ("true", "1", "yes")
    PROF_DIR = os.getenv("PROFILE_DIR", "profile")

    if PROFILE:
        # Configuração opcional do Profiler Middleware (para análise de desempenho)
        app.server.config["PROFILE"] = True
        app.server.wsgi_app = ProfilerMiddleware(
            app.server.wsgi_app,
            sort_by=["cumtime"],
            restrictions=[50],
            stream=None,
            profile_dir=PROF_DIR,
        )
    
    app.run(host=APP_HOST, debug=APP_DEBUG, port=APP_PORT)
