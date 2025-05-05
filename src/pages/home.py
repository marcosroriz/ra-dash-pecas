#!/usr/bin/env python
# coding: utf-8

# Dashboard que lista o retrabalho de uma ou mais OS

##############################################################################
# IMPORTS ####################################################################
##############################################################################
# Bibliotecas básicas
import datetime 
from datetime import date
import pandas as pd

# Importar bibliotecas do dash básicas e plotly
import dash
from dash import Dash, html, dcc, callback, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

# Importar bibliotecas do bootstrap e ag-grid
import dash_bootstrap_components as dbc
import dash_ag_grid as dag

# Dash componentes Mantine e icones
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# Importar nossas constantes e funções utilitárias
import locale_utils

# Banco de Dados
from db import PostgresSingleton

# Imports gerais
from modules.entities_utils import get_mecanicos, get_lista_os, get_oficinas, get_secoes, get_modelos, gerar_excel
# Imports específicos
from modules.home.home_service import HomeService
import modules.home.graficos as home_graficos
import modules.home.tabelas as home_tabelas

##############################################################################
# LEITURA DE DADOS ###########################################################
##############################################################################
# Conexão com os bancos
pgDB = PostgresSingleton.get_instance()
pgEngine = pgDB.get_engine()

# Cria o serviço
home_service = HomeService(pgEngine)

# Modelos de veículos
df_modelos_veiculos = get_modelos(pgEngine)
lista_todos_modelos_veiculos = df_modelos_veiculos.to_dict(orient="records")
lista_todos_modelos_veiculos.insert(0, {"MODELO": "TODOS"})

# Obtem a lista de Oficinas
df_oficinas = get_oficinas(pgEngine)
lista_todas_oficinas = df_oficinas.to_dict(orient="records")
lista_todas_oficinas.insert(0, {"LABEL": "TODAS"})

# Obtem a lista de Seções
df_secoes = get_secoes(pgEngine)
lista_todas_secoes = df_secoes.to_dict(orient="records")
lista_todas_secoes.insert(0, {"LABEL": "TODAS"})

# Colaboradores / Mecânicos
df_mecanicos = get_mecanicos(pgEngine)

# Obtem a lista de OS
df_lista_os = get_lista_os(pgEngine)
lista_todas_os = df_lista_os.to_dict(orient="records")
lista_todas_os.insert(0, {"LABEL": "TODAS"})


##############################################################################
# CALLBACKS ##################################################################
##############################################################################

##############################################################################
# Callbacks para os inputs ###################################################
##############################################################################


# Função para validar o input
def input_valido(datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
    if datas is None or not datas or None in datas or min_dias is None:
        return False

    if lista_modelos is None or not lista_modelos or None in lista_modelos:
        return False

    if lista_oficinas is None or not lista_oficinas or None in lista_oficinas:
        return False

    if lista_secaos is None or not lista_secaos or None in lista_secaos:
        return False

    if lista_os is None or not lista_os or None in lista_os:
        return False

    return True


# Corrige o input para garantir que o termo para todas ("TODAS") não seja selecionado junto com outras opções
def corrige_input(lista, termo_all="TODAS"):
    # Caso 1: Nenhuma opcao é selecionada, reseta para "TODAS"
    if not lista:
        return [termo_all]

    # Caso 2: Se "TODAS" foi selecionado após outras opções, reseta para "TODAS"
    if len(lista) > 1 and termo_all in lista[1:]:
        return [termo_all]

    # Caso 3: Se alguma opção foi selecionada após "TODAS", remove "TODAS"
    if termo_all in lista and len(lista) > 1:
        return [value for value in lista if value != termo_all]

    # Por fim, se não caiu em nenhum caso, retorna o valor original
    return lista


@callback(
    Output("input-select-modelo-veiculos-visao-geral", "value"),
    Input("input-select-modelo-veiculos-visao-geral", "value"),
)
def corrige_input_modelos(lista_modelos):
    return corrige_input(lista_modelos, "TODOS")


@callback(
    Output("input-select-oficina-visao-geral", "value"),
    Input("input-select-oficina-visao-geral", "value"),
)
def corrige_input_oficina(lista_oficinas):
    return corrige_input(lista_oficinas)


@callback(
    Output("input-select-secao-visao-geral", "value"),
    Input("input-select-secao-visao-geral", "value"),
)
def corrige_input_secao(lista_secaos):
    return corrige_input(lista_secaos)


@callback(
    [
        Output("input-select-ordens-servico-visao-geral", "options"),
        Output("input-select-ordens-servico-visao-geral", "value"),
    ],
    [
        Input("input-select-ordens-servico-visao-geral", "value"),
        Input("input-select-secao-visao-geral", "value"),
    ],
)
def corrige_input_ordem_servico(lista_os, lista_secaos):
    # Vamos pegar as OS possíveis para as seções selecionadas
    df_lista_os_secao = df_lista_os

    if "TODAS" not in lista_secaos:
        df_lista_os_secao = df_lista_os_secao[df_lista_os_secao["SECAO"].isin(lista_secaos)]

    # Essa rotina garante que, ao alterar a seleção de oficinas ou seções, a lista de ordens de serviço seja coerente
    lista_os_possiveis = df_lista_os_secao.to_dict(orient="records")
    lista_os_possiveis.insert(0, {"LABEL": "TODAS"})

    lista_options = [{"label": os["LABEL"], "value": os["LABEL"]} for os in lista_os_possiveis]

    # OK, algor vamos remover as OS que não são possíveis para as seções selecionadas
    if "TODAS" not in lista_os:
        df_lista_os_atual = df_lista_os_secao[df_lista_os_secao["LABEL"].isin(lista_os)]
        lista_os = df_lista_os_atual["LABEL"].tolist()

    return lista_options, corrige_input(lista_os)


##############################################################################
# Callbacks para os gráficos #################################################
##############################################################################



##############################################################################
# Callbacks para as tabelas ##################################################
##############################################################################



# Callback para atualizar o link de download quando o botão for clicado
@callback(
    Output("download-excel-tipo-os", "data"),
    [
        Input("btn-exportar-tipo-os", "n_clicks"),
        Input("input-intervalo-datas-geral", "value"),
        Input("input-select-dias-geral-retrabalho", "value"),
        Input("input-select-modelo-veiculos-visao-geral", "value"),
        Input("input-select-oficina-visao-geral", "value"),
        Input("input-select-secao-visao-geral", "value"),
        Input("input-select-ordens-servico-visao-geral", "value"),
    ],
    prevent_initial_call=True
)
def download_excel_tabela_top_os(n_clicks, datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
    if not n_clicks or n_clicks <= 0: # Garantre que ao iniciar ou carregar a page, o arquivo não seja baixado
        return dash.no_update

    date_now = date.today().strftime('%d-%m-%Y')
    
    # Obtem os dados
    df = home_service.get_top_os_geral_retrabalho(datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os)

    excel_data = gerar_excel(df=df)
    return dcc.send_bytes(excel_data, f"tabela_tipo_os_{date_now}.xlsx")


@callback(
    Output("download-excel-tabela-colaborador", "data"),
    [
        Input("btn-exportar-tabela-colaborador", "n_clicks"),
        Input("input-intervalo-datas-geral", "value"),
        Input("input-select-dias-geral-retrabalho", "value"),
        Input("input-select-modelo-veiculos-visao-geral", "value"),
        Input("input-select-oficina-visao-geral", "value"),
        Input("input-select-secao-visao-geral", "value"),
        Input("input-select-ordens-servico-visao-geral", "value"),
    ],
    prevent_initial_call=True
)
def download_excel_tabela_colaborador(n_clicks, datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
    if not n_clicks or n_clicks <= 0: # Garantre que ao iniciar ou carregar a page, o arquivo não seja baixado
        return dash.no_update

    date_now = date.today().strftime('%d-%m-%Y')
    
    # Obtem os dados
    df = home_service.get_top_os_colaboradores(datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os)

    excel_data = gerar_excel(df=df)
    return dcc.send_bytes(excel_data, f"tabela_colaboradores_{date_now}.xlsx")



@callback(
    Output("download-excel-tabela-veiculo", "data"),
    [
        Input("btn-exportar-tabela-veiculo", "n_clicks"),
        Input("input-intervalo-datas-geral", "value"),
        Input("input-select-dias-geral-retrabalho", "value"),
        Input("input-select-modelo-veiculos-visao-geral", "value"),
        Input("input-select-oficina-visao-geral", "value"),
        Input("input-select-secao-visao-geral", "value"),
        Input("input-select-ordens-servico-visao-geral", "value"),
    ],
    prevent_initial_call=True
)
def download_excel_tabela_colaborador(n_clicks, datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
    if not n_clicks or n_clicks <= 0: # Garantre que ao iniciar ou carregar a page, o arquivo não seja baixado
        return dash.no_update

    date_now = date.today().strftime('%d-%m-%Y')
    
    # Obtem os dados
    df = home_service.get_top_veiculos(datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os)

    excel_data = gerar_excel(df=df)
    return dcc.send_bytes(excel_data, f"tabela_veiculo_{date_now}.xlsx")

##############################################################################
### Callbacks para os labels #################################################
##############################################################################


def gera_labels_inputs(campo):
    # Cria o callback
    @callback(
        [
            Output(component_id=f"{campo}-labels", component_property="children"),
        ],
        [
            Input("input-intervalo-datas-geral", "value"),
            Input("input-select-dias-geral-retrabalho", "value"),
            Input("input-select-oficina-visao-geral", "value"),
            Input("input-select-secao-visao-geral", "value"),
            Input("input-select-ordens-servico-visao-geral", "value"),
        ],
    )
    def atualiza_labels_inputs(datas, min_dias, lista_oficinas, lista_secaos, lista_os):
        labels_antes = [
            # DashIconify(icon="material-symbols:filter-arrow-right", width=20),
            dmc.Badge("Filtro", color="gray", variant="outline"),
        ]

        datas_label = []
        if not (datas is None or not datas) and datas[0] is not None and datas[1] is not None:
            # Formata as datas
            data_inicio_str = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim_str = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            datas_label = [dmc.Badge(f"{data_inicio_str} a {data_fim_str}", variant="outline")]

        min_dias_label = [dmc.Badge(f"{min_dias} dias", variant="outline")]
        lista_oficinas_labels = []
        lista_secaos_labels = []
        lista_os_labels = []

        if lista_oficinas is None or not lista_oficinas or "TODAS" in lista_oficinas:
            lista_oficinas_labels.append(dmc.Badge("Todas as oficinas", variant="outline"))
        else:
            for oficina in lista_oficinas:
                lista_oficinas_labels.append(dmc.Badge(oficina, variant="dot"))

        if lista_secaos is None or not lista_secaos or "TODAS" in lista_secaos:
            lista_secaos_labels.append(dmc.Badge("Todas as seções", variant="outline"))
        else:
            for secao in lista_secaos:
                lista_secaos_labels.append(dmc.Badge(secao, variant="dot"))

        if lista_os is None or not lista_os or "TODAS" in lista_os:
            lista_os_labels.append(dmc.Badge("Todas as ordens de serviço", variant="outline"))
        else:
            for os in lista_os:
                lista_os_labels.append(dmc.Badge(f"OS: {os}", variant="dot"))

        return [dmc.Group(labels_antes + datas_label + min_dias_label + lista_oficinas_labels + lista_os_labels)]

    # Cria o componente
    return dmc.Group(id=f"{campo}-labels", children=[])


##############################################################################
# Layout #####################################################################
##############################################################################
layout = dbc.Container(
    [
        # Loading
        # dmc.LoadingOverlay(
        #     visible=True,
        #     id="loading-overlay-guia-geral",
        #     loaderProps={"size": "xl"},
        #     overlayProps={
        #         "radius": "lg",
        #         "blur": 2,
        #         "style": {
        #             "top": 0,  # Start from the top of the viewport
        #             "left": 0,  # Start from the left of the viewport
        #             "width": "100vw",  # Cover the entire width of the viewport
        #             "height": "100vh",  # Cover the entire height of the viewport
        #         },
        #     },
        #     zIndex=10,
        # ),
        # Cabeçalho
        dbc.Row(
            [
                dbc.Col(
                    [
                        # Cabeçalho e Inputs
                        dbc.Row(
                            [
                                html.Hr(),
                                dbc.Row(
                                    [
                                        dbc.Col(DashIconify(icon="mdi:tools", width=45), width="auto"),
                                        dbc.Col(
                                            html.H1(
                                                [
                                                    "Visão geral das\u00a0",
                                                    html.Strong("peças"),
                                                ],
                                                className="align-self-center",
                                            ),
                                            width=True,
                                        ),
                                    ],
                                    align="center",
                                ),
                                dmc.Space(h=15),
                                html.Hr(),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            html.Div(
                                                [
                                                    dbc.Label("Data (intervalo) de análise"),
                                                    dmc.DatePicker(
                                                        id="input-intervalo-datas-geral",
                                                        allowSingleDateInRange=True,
                                                        type="range",
                                                        minDate=date(2024, 8, 1),
                                                        maxDate=date.today(),
                                                        value=[date(2024, 8, 1), date.today()],
                                                    ),
                                                ],
                                                className="dash-bootstrap",
                                            ),
                                        ],
                                        body=True,
                                    ),
                                    md=12,
                                ),
                                dmc.Space(h=10),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            html.Div(
                                                [
                                                    dbc.Label("Modelos de Veículos"),
                                                    dcc.Dropdown(
                                                        id="input-select-modelo-veiculos-visao-geral",
                                                        options=[
                                                            {
                                                                "label": os["MODELO"],
                                                                "value": os["MODELO"],
                                                            }
                                                            for os in lista_todos_modelos_veiculos
                                                        ],
                                                        multi=True,
                                                        value=["TODOS"],
                                                        placeholder="Selecione um ou mais modelos...",
                                                    ),
                                                ],
                                                className="dash-bootstrap",
                                            ),
                                        ],
                                        body=True,
                                    ),
                                    md=12,
                                ),
                                dmc.Space(h=10),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            html.Div(
                                                [
                                                    dbc.Label("Oficinas"),
                                                    dcc.Dropdown(
                                                        id="input-select-oficina-visao-geral",
                                                        options=[{"label": os["LABEL"], "value": os["LABEL"]} for os in lista_todas_oficinas],
                                                        multi=True,
                                                        value=["TODAS"],
                                                        placeholder="Selecione uma ou mais oficinas...",
                                                    ),
                                                ],
                                                className="dash-bootstrap",
                                            ),
                                        ],
                                        body=True,
                                    ),
                                    md=6,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            html.Div(
                                                [
                                                    dbc.Label("Seções (categorias) de manutenção"),
                                                    dcc.Dropdown(
                                                        id="input-select-secao-visao-geral",
                                                        options=[
                                                            # {"label": "TODAS", "value": "TODAS"},
                                                            # {
                                                            #     "label": "BORRACHARIA",
                                                            #     "value": "MANUTENCAO BORRACHARIA",
                                                            # },
                                                            {
                                                                "label": "ELETRICA",
                                                                "value": "MANUTENCAO ELETRICA",
                                                            },
                                                            # {"label": "GARAGEM", "value": "MANUTENÇÃO GARAGEM"},
                                                            # {
                                                            #     "label": "LANTERNAGEM",
                                                            #     "value": "MANUTENCAO LANTERNAGEM",
                                                            # },
                                                            # {"label": "LUBRIFICAÇÃO", "value": "LUBRIFICAÇÃO"},
                                                            {
                                                                "label": "MECANICA",
                                                                "value": "MANUTENCAO MECANICA",
                                                            },
                                                            # {"label": "PINTURA", "value": "MANUTENCAO PINTURA"},
                                                            # {
                                                            #     "label": "SERVIÇOS DE TERCEIROS",
                                                            #     "value": "SERVIÇOS DE TERCEIROS",
                                                            # },
                                                            # {
                                                            #     "label": "SETOR DE ALINHAMENTO",
                                                            #     "value": "SETOR DE ALINHAMENTO",
                                                            # },
                                                            # {
                                                            #     "label": "SETOR DE POLIMENTO",
                                                            #     "value": "SETOR DE POLIMENTO",
                                                            # },
                                                        ],
                                                        multi=True,
                                                        value=["MANUTENCAO ELETRICA", "MANUTENCAO MECANICA"],
                                                        placeholder="Selecione uma ou mais seções...",
                                                    ),
                                                ],
                                                # className="dash-bootstrap",
                                            ),
                                        ],
                                        body=True,
                                    ),
                                    md=6,
                                ),
                                dmc.Space(h=10),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            html.Div(
                                                [
                                                    dbc.Label("Peça específica"),
                                                    dcc.Dropdown(
                                                        id="input-select-ordens-servico-visao-geral",
                                                        options=[{"label": os["LABEL"], "value": os["LABEL"]} for os in lista_todas_os],
                                                        multi=True,
                                                        value=["TODAS"],
                                                        placeholder="Selecione uma ou mais peças específicas...",
                                                    ),
                                                ],
                                                className="dash-bootstrap",
                                            ),
                                        ],
                                        body=True,
                                    ),
                                    md=12,
                                ),
                            ]
                        ),
                    ],
                    md=12,
                ),
            ]
        ),
        # Gráfico de Retrabalho por Modelo
        dmc.Space(h=30),
        dbc.Row(
            [
                dbc.Col(DashIconify(icon="mdi:chart-line", width=45), width="auto"),
                dbc.Col(
                    dbc.Row(
                        [
                            html.H4(
                                "Gráfico do custo gasto com peças por mês",
                                className="align-self-center",
                            ),
                            dmc.Space(h=5),
                            gera_labels_inputs("visao-geral-quanti-frota"),
                        ]
                    ),
                    width=True,
                ),
            ],
            align="center",
        ),
        dcc.Graph(id="graph-gasto-por-mês"),
        dmc.Space(h=40),
        # Grafico de Evolução do Retrabalho por Modelo
        dbc.Row(
            [
                dbc.Col(DashIconify(icon="fluent:arrow-trending-settings-20-filled", width=45), width="auto"),
                dbc.Col(
                    dbc.Row(
                        [
                            html.H4(
                                "Gráfico de peças trocadas por mês",
                                className="align-self-center",
                            ),
                            dmc.Space(h=5),
                            gera_labels_inputs("visao-geral-evolucao-por-modelo"),
                        ]
                    ),
                    width=True,
                ),
            ],
            align="center",
        ),
        dcc.Graph(id="graph-de-pecas-trocadas-por-mes"),
        dmc.Space(h=40),
        # Tabela com as estatísticas gerais de Retrabalho
        dbc.Row(
            [
                dbc.Col(DashIconify(icon="mdi:trophy", width=45), width="auto"),
                dbc.Col(
                    dbc.Row(
                        [
                            html.H4(
                                "RANKING DE PEÇAS MAIS CARAS",
                                className="align-self-center",
                            ),
                            dmc.Space(h=5),
                            dbc.Row(
                                [
                                    dbc.Col(gera_labels_inputs("visao-geral-tabela-tipo-os"), width=True),
                                    dbc.Col(
                                        html.Div(
                                            [
                                                html.Button(
                                                    "Exportar para Excel",
                                                    id="btn-exportar-tipo-os",
                                                    n_clicks=0,
                                                    style={
                                                        "background-color": "#007bff",  # Azul
                                                        "color": "white",
                                                        "border": "none",
                                                        "padding": "10px 20px",
                                                        "border-radius": "8px",
                                                        "cursor": "pointer",
                                                        "font-size": "16px",
                                                        "font-weight": "bold",
                                                    },
                                                ),
                                                dcc.Download(id="download-excel-tipo-os"),
                                            ],
                                            style={"text-align": "right"},
                                        ),
                                        width="auto",
                                    ),
                                ],
                                align="center",
                                justify="between",  # Deixa os itens espaçados
                            ),
                        ]
                    ),
                    width=True,
                ),
            ],
            align="center",
        ),
        dmc.Space(h=20),
        dag.AgGrid(
            # enableEnterpriseModules=True,
            id="tabela-ranking-de-pecas-mais-caras",
            columnDefs=home_tabelas.tbl_ranking_de_pecas_mais_trocadas,
            rowData=[],
            defaultColDef={"filter": True, "floatingFilter": True},
            columnSize="autoSize",
            dashGridOptions={
                "localeText": locale_utils.AG_GRID_LOCALE_BR,
            },
            # Permite resize --> https://community.plotly.com/t/anyone-have-better-ag-grid-resizing-scheme/78398/5
            style={"height": 400, "resize": "vertical", "overflow": "hidden"},
        ),
        dmc.Space(h=40),
        # Tabela com as estatísticas gerais por Colaborador
        dbc.Row(
            [
                dbc.Col(DashIconify(icon="mdi:bus-wrench", width=45), width="auto"),
                dbc.Col(
                    dbc.Row(
                        [
                            html.H4(
                                "Veículos que mais trocaram peças",
                                className="align-self-center",
                            ),
                            dmc.Space(h=5),
                            dbc.Row(
                                [
                                    dbc.Col(gera_labels_inputs("visao-geral-tabela-colaborador-os"), width=True),
                                    dbc.Col(
                                        html.Div(
                                            [
                                                html.Button(
                                                    "Exportar para Excel",
                                                    id="btn-exportar-tabela-colaborador",
                                                    n_clicks=0,
                                                    style={
                                                        "background-color": "#007bff",  # Azul
                                                        "color": "white",
                                                        "border": "none",
                                                        "padding": "10px 20px",
                                                        "border-radius": "8px",
                                                        "cursor": "pointer",
                                                        "font-size": "16px",
                                                        "font-weight": "bold",
                                                    },
                                                ),
                                                dcc.Download(id="download-excel-tabela-colaborador"),
                                            ],
                                            style={"text-align": "right"},
                                        ),
                                        width="auto",
                                    ),
                                ],
                                align="center",
                                justify="between",  # Deixa os itens espaçados
                            ),
                        ]
                    ),
                    width=True,
                ),
            ],
            align="center",
        ),
        dmc.Space(h=20),
        dag.AgGrid(
            id="tabela-veiculos-que-mais-trocam-pecas",
            columnDefs=home_tabelas.tbl_veiculos_que_mais_trocam_pecas,
            rowData=[],
            defaultColDef={"filter": True, "floatingFilter": True},
            columnSize="autoSize",
            dashGridOptions={
                "localeText": locale_utils.AG_GRID_LOCALE_BR,
            },
            # Permite resize --> https://community.plotly.com/t/anyone-have-better-ag-grid-resizing-scheme/78398/5
            style={"height": 400, "resize": "vertical", "overflow": "hidden"},
        ),
        dmc.Space(h=40),
        # Tabela com as estatísticas gerais por Veículo
        dbc.Row(
            [
                dbc.Col(DashIconify(icon="mdi:bus-wrench", width=45), width="auto"),
                dbc.Col(
                    dbc.Row(
                        [
                            html.H4(
                                "Tabela principais peças",
                                className="align-self-center",
                            ),
                            dmc.Space(h=5),
                            dbc.Row(
                                [
                                    dbc.Col(gera_labels_inputs("visao-geral-tabela-veiculo"), width=True),
                                    dbc.Col(
                                        html.Div(
                                            [
                                                html.Button(
                                                    "Exportar para Excel",
                                                    id="btn-exportar-tabela-veiculo",
                                                    n_clicks=0,
                                                    style={
                                                        "background-color": "#007bff",  # Azul
                                                        "color": "white",
                                                        "border": "none",
                                                        "padding": "10px 20px",
                                                        "border-radius": "8px",
                                                        "cursor": "pointer",
                                                        "font-size": "16px",
                                                        "font-weight": "bold",
                                                    },
                                                ),
                                                dcc.Download(id="download-excel-tabela-veiculo"),
                                            ],
                                            style={"text-align": "right"},
                                        ),
                                        width="auto",
                                    ),
                                ],
                                align="center",
                                justify="between",  # Deixa os itens espaçados
                            ),
                        ]
                    ),
                    width=True,
                ),
            ],
            align="center",
        ),
        dmc.Space(h=20),
        dag.AgGrid(
            id="tabela-principais-pecas",
            columnDefs=home_tabelas.tbl_pincipais_pecas,
            rowData=[],
            defaultColDef={"filter": True, "floatingFilter": True},
            columnSize="autoSize",
            dashGridOptions={
                "localeText": locale_utils.AG_GRID_LOCALE_BR,
            },
            # Permite resize --> https://community.plotly.com/t/anyone-have-better-ag-grid-resizing-scheme/78398/5
            style={"height": 400, "resize": "vertical", "overflow": "hidden"},
        ),
        dmc.Space(h=40),
    ]
)


##############################################################################
# Registro da página #########################################################
##############################################################################
dash.register_page(__name__, name="Visão Geral", path="/", icon="mdi:bus-alert")
