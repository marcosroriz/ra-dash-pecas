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
from modules.entities_utils import *
# Imports específicos
from modules.home.home_service import HomeService
from modules.home.graficos import *
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
df_lista_pecas = get_pecas(pgEngine)
lista_todas_pecas = df_lista_pecas.to_dict(orient="records")
lista_todas_pecas.insert(0, {"LABEL": "TODAS"})


##############################################################################
# CALLBACKS ##################################################################
##############################################################################

##############################################################################
# Callbacks para os inputs ###################################################
##############################################################################


# Função para validar o input
def input_valido(datas, lista_modelos, lista_oficinas, lista_secaos, lista_pecas):
    if datas is None or not datas or None in datas:
        return False

    if lista_modelos is None or not lista_modelos or None in lista_modelos:
        return False

    if lista_oficinas is None or not lista_oficinas or None in lista_oficinas:
        return False

    if lista_secaos is None or not lista_secaos or None in lista_secaos:
        return False

    if lista_pecas is None or not lista_pecas or None in lista_pecas:
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
    [
        Output("input-select-pecas-visao-geral", "options"),
        Output("input-select-pecas-visao-geral", "value"),
    ],
    [
        Input("input-intervalo-datas-geral", "value"),
        Input("input-select-modelo-veiculos-visao-geral", "value"),
        Input("input-select-oficina-visao-geral", "value"),
        Input("input-select-secao-visao-geral", "value"),
        Input("input-select-pecas-visao-geral", "value"),
    ]
)
def corrige_input_pecas(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas):
    """
    Atualiza as opções e o valor selecionado do dropdown de peças com base nos filtros aplicados.

    Parâmetros:
        datas (str | list): Intervalo de datas selecionado.
        lista_modelos (list): Lista de modelos de veículos selecionados.
        lista_oficina (list): Lista de oficinas selecionadas.
        lista_secao (list): Lista de seções selecionadas.
        lista_pecas (list): Lista atual de peças selecionadas.

    Retorna:
        tuple:
            - options (list[dict]): Lista de opções para o dropdown no formato {"label": ..., "value": ...}.
            - value (list): Lista de valores corrigida para manter a seleção válida com base nos filtros.
    """
    df_lista_pecas_secao = df_lista_pecas

    if "TODAS" not in lista_secao:
        df_lista_pecas_secao = home_service.get_pecas(datas, lista_modelos, lista_oficina, lista_secao)

    lista_pecas_possiveis = df_lista_pecas_secao.to_dict(orient="records")
    lista_pecas_possiveis.insert(0, {"LABEL": "TODAS"})

    lista_options = [{"label": os["LABEL"], "value": os["LABEL"]} for os in lista_pecas_possiveis]

    if lista_pecas and "TODAS" not in lista_pecas:
        df_lista_pecas_atual = df_lista_pecas_secao[df_lista_pecas_secao["LABEL"].isin(lista_pecas)]
        lista_pecas_corrigida = df_lista_pecas_atual["LABEL"].tolist()
    else:
        lista_pecas_corrigida = lista_pecas

    return lista_options, corrige_input(lista_pecas_corrigida)




##############################################################################
# Callbacks para os gráficos #################################################
##############################################################################

@callback(
    Output("graph-visao-geral-gasto-troca-pecas-mensal", "figure"),
    [
        Input("input-intervalo-datas-geral", "value"),
        Input("input-select-modelo-veiculos-visao-geral", "value"),
        Input("input-select-oficina-visao-geral", "value"),
        Input("input-select-secao-visao-geral", "value"),
        Input("input-select-pecas-visao-geral", "value"),
    ],
)
def plota_grafico_linha_custo_mensal(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas):
    # Valida input
    if not input_valido(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas):
        return go.Figure()

    # Obtem os dados
    df_custo = home_service.get_custo_mensal_pecas(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas)
    df_quantidade = home_service.get_troca_pecas_mensal(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas)
    df_custo_retrabalho = home_service.get_custo_mensal_pecas_retrabalho(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas)

    # Gera o gráfico
    fig = grafico_custo_quantidade_mensal(df_custo, df_quantidade, df_custo_retrabalho)
    return fig


##############################################################################
# Callbacks para as tabelas ##################################################
##############################################################################


@callback(
    [
        Output("loading-overlay-visao-geral", "visible"),
        Output("tabela-ranking-de-pecas-mais-caras", "rowData"),
    ],
    [
        Input("input-intervalo-datas-geral", "value"),
        Input("input-select-modelo-veiculos-visao-geral", "value"),
        Input("input-select-oficina-visao-geral", "value"),
        Input("input-select-secao-visao-geral", "value"),
        Input("input-select-pecas-visao-geral", "value"),
    ],
)
def atualiza_tabela_rank_pecas(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas):
    # Valida input
    if not input_valido(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas):
        return False, []

    # Obtem dados
    df = home_service.get_rank_pecas(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas)

    return False, df.to_dict("records")

# Callback para atualizar o link de download quando o botão for clicado
@callback(
    Output("download-excel-tabela-rank-pecas", "data"),
    [
        Input("btn-exportar-rank-pecas", "n_clicks"),
        Input("input-intervalo-datas-geral", "value"),
        Input("input-select-modelo-veiculos-visao-geral", "value"),
        Input("input-select-oficina-visao-geral", "value"),
        Input("input-select-secao-visao-geral", "value"),
        Input("input-select-pecas-visao-geral", "value"),
    ],
    prevent_initial_call=True
)
def download_excel_tabela_top_rank_pecas(n_clicks, datas, lista_modelos, lista_oficina, lista_secao, lista_pecas):
    if not n_clicks or n_clicks <= 0: # Garantre que ao iniciar ou carregar a page, o arquivo não seja baixado
        return dash.no_update

    date_now = date.today().strftime('%d-%m-%Y')
    
    # Obtem os dados
    df = home_service.get_rank_pecas(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas)

    excel_data = gerar_excel(df=df)
    return dcc.send_bytes(excel_data, f"tabela_rank_pecas_{date_now}.xlsx")



@callback(
    Output("tabela-principais-pecas", "rowData"),
    [
        Input("input-intervalo-datas-geral", "value"),
        Input("input-select-modelo-veiculos-visao-geral", "value"),
        Input("input-select-oficina-visao-geral", "value"),
        Input("input-select-secao-visao-geral", "value"),
        Input("input-select-pecas-visao-geral", "value"),
    ],
)
def atualiza_tabela_principais_pecas(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas):
    # Valida input
    if not input_valido(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas):
        return []

    # Obtem dados
    df = home_service.get_principais_pecas(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas)

    return df.to_dict("records")

# Callback para atualizar o link de download quando o botão for clicado
@callback(
    Output("download-excel-tabela-principais-pecas", "data"),
    [
        Input("btn-exportar-tabela-principais-pecas", "n_clicks"),
        Input("input-intervalo-datas-geral", "value"),
        Input("input-select-modelo-veiculos-visao-geral", "value"),
        Input("input-select-oficina-visao-geral", "value"),
        Input("input-select-secao-visao-geral", "value"),
        Input("input-select-pecas-visao-geral", "value"),
    ],
    prevent_initial_call=True
)
def download_excel_principais_pecas(n_clicks, datas, lista_modelos, lista_oficina, lista_secao, lista_pecas):
    if not n_clicks or n_clicks <= 0: # Garantre que ao iniciar ou carregar a page, o arquivo não seja baixado
        return dash.no_update

    date_now = date.today().strftime('%d-%m-%Y')
    
    # Obtem os dados
    df = home_service.get_principais_pecas(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas)

    excel_data = gerar_excel(df=df)
    return dcc.send_bytes(excel_data, f"tabela_principais_pecas_{date_now}.xlsx")

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
            Input("input-select-modelo-veiculos-visao-geral", "value"),
            Input("input-select-oficina-visao-geral", "value"),
            Input("input-select-secao-visao-geral", "value"),
            Input("input-select-pecas-visao-geral", "value"),
        ],
    )
    def atualiza_labels_inputs(datas, lista_modelos, lista_oficina, lista_secao, lista_pecas):
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

        lista_oficinas_labels = []
        lista_secaos_labels = []
        lista_os_labels = []

        if lista_oficina is None or not lista_oficina or "TODAS" in lista_oficina:
            lista_oficinas_labels.append(dmc.Badge("Todas as oficinas", variant="outline"))
        else:
            for oficina in lista_oficina:
                lista_oficinas_labels.append(dmc.Badge(oficina, variant="dot"))

        if lista_secao is None or not lista_secao or "TODAS" in lista_secao:
            lista_secaos_labels.append(dmc.Badge("Todas as seções", variant="outline"))
        else:
            for secao in lista_secao:
                lista_secaos_labels.append(dmc.Badge(secao, variant="dot"))

        if lista_pecas is None or not lista_pecas or "TODAS" in lista_pecas:
            lista_os_labels.append(dmc.Badge("Todas as peças", variant="outline"))
        else:
            for pecas in lista_pecas:
                lista_os_labels.append(dmc.Badge(f"Peças: {pecas}", variant="dot"))

        return [dmc.Group(labels_antes + datas_label + lista_oficinas_labels + lista_os_labels)]

    # Cria o componente
    return dmc.Group(id=f"{campo}-labels", children=[])


##############################################################################
# Layout #####################################################################
##############################################################################
layout = dbc.Container(
    [
        # Loading
        dmc.LoadingOverlay(
            visible=True,
            id="loading-overlay-visao-geral",
            loaderProps={"size": "xl"},
            overlayProps={
                "radius": "lg",
                "blur": 2,
                "style": {
                    "top": 0,  # Start from the top of the viewport
                    "left": 0,  # Start from the left of the viewport
                    "width": "100vw",  # Cover the entire width of the viewport
                    "height": "100vh",  # Cover the entire height of the viewport
                },
            },
            zIndex=10,
        ),
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
                                    md=6,
                                ),
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
                                    md=6,
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
                                                        id="input-select-pecas-visao-geral",
                                                        options=[{"label": pecas["LABEL"], "value": pecas["LABEL"]} for pecas in lista_todas_pecas],
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
                ),
            ]
        ),
        #### ALterar graficos para dados de peças
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
        dcc.Graph(id="graph-visao-geral-gasto-troca-pecas-mensal"),
        dmc.Space(h=40),
        # Tabela com as estatísticas gerais de Retrabalho
        dbc.Row(
            [
                dbc.Col(DashIconify(icon="mdi:trophy", width=45), width="auto"),
                dbc.Col(
                    dbc.Row(
                        [
                            html.H4(
                                "PRINCIPAIS PEÇAS",
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
                                                    id="btn-exportar-rank-pecas",
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
                                                dcc.Download(id="download-excel-tabela-rank-pecas"),
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
        # dag.AgGrid(
        #     # enableEnterpriseModules=True,
        #     id="tabela-ranking-de-pecas-mais-caras",
        #     columnDefs=home_tabelas.tbl_ranking_de_pecas_mais_trocadas,
        #     rowData=[],
        #     defaultColDef={"filter": True, "floatingFilter": True},
        #     columnSize="autoSize",
        #     dashGridOptions={
        #         "localeText": locale_utils.AG_GRID_LOCALE_BR,
        #     },
        #     # Permite resize --> https://community.plotly.com/t/anyone-have-better-ag-grid-resizing-scheme/78398/5
        #     style={"height": 400, "resize": "vertical", "overflow": "hidden"},
        # ),
        dag.AgGrid(
        id="tabela-ranking-de-pecas-mais-caras",
        columnDefs=home_tabelas.tbl_ranking_de_pecas_mais_trocadas,
        rowData=[],  # suas 2000 linhas
        defaultColDef={"filter": True, "floatingFilter": True},
        # Remova columnSize="autoSize" se estiver lento
        dashGridOptions={
            "localeText": locale_utils.AG_GRID_LOCALE_BR,
            "pagination": True,            # habilita paginação
            "paginationPageSize": 50       # mostra 50 linhas por página (ajuste conforme quiser)
        },
        style={"height": 400, "overflow": "hidden"},
        ),
        dmc.Space(h=40),
        # Tabela com as estatísticas gerais por Colaborador
        # dbc.Row(
        #     [
        #         dbc.Col(DashIconify(icon="mdi:bus-wrench", width=45), width="auto"),
        #         dbc.Col(
        #             dbc.Row(
        #                 [
        #                     html.H4(
        #                         "PRINCIPAIS PEÇAS",
        #                         className="align-self-center",
        #                     ),
        #                     dmc.Space(h=5),
        #                     dbc.Row(
        #                         [
        #                             dbc.Col(gera_labels_inputs("visao-geral-tabela-principais-pecas"), width=True),
        #                             dbc.Col(
        #                                 html.Div(
        #                                     [
        #                                         html.Button(
        #                                             "Exportar para Excel",
        #                                             id="btn-exportar-tabela-principais-pecas",
        #                                             n_clicks=0,
        #                                             style={
        #                                                 "background-color": "#007bff",  # Azul
        #                                                 "color": "white",
        #                                                 "border": "none",
        #                                                 "padding": "10px 20px",
        #                                                 "border-radius": "8px",
        #                                                 "cursor": "pointer",
        #                                                 "font-size": "16px",
        #                                                 "font-weight": "bold",
        #                                             },
        #                                         ),
        #                                         dcc.Download(id="download-excel-tabela-principais-pecas"),
        #                                     ],
        #                                     style={"text-align": "right"},
        #                                 ),
        #                                 width="auto",
        #                             ),
        #                         ],
        #                         align="center",
        #                         justify="between",  # Deixa os itens espaçados
        #                     ),
        #                 ]
        #             ),
        #             width=True,
        #         ),
        #     ],
        #     align="center",
        # ),

        # dmc.Space(h=20),
        # dag.AgGrid(
        #     id="tabela-principais-pecas",
        #     columnDefs=home_tabelas.tbl_pincipais_pecas,
        #     rowData=[],
        #     defaultColDef={
        #     "filter": True,
        #     "floatingFilter": True,
        #     "resizable": True,
        #     "autoSize": True,  # <- aqui já resolve para todas
        #     },
        #     columnSize="responsiveSizeToFit",  # Corrigido aqui
        #     dashGridOptions={
        #         "localeText": locale_utils.AG_GRID_LOCALE_BR,
        #     },
        #     style={"height": 400, "resize": "vertical", "overflow": "hidden"},
        # ),
        dmc.Space(h=40),
                # dmc.Space(h=20),
        # dag.AgGrid(
        #     id="tabela-veiculos-que-mais-trocam-pecas",
        #     columnDefs=home_tabelas.tbl_veiculos_que_mais_trocam_pecas,
        #     rowData=[],
        #     defaultColDef={"filter": True, "floatingFilter": True},
        #     columnSize="autoSize",
        #     dashGridOptions={
        #         "localeText": locale_utils.AG_GRID_LOCALE_BR,
        #     },
        #     # Permite resize --> https://community.plotly.com/t/anyone-have-better-ag-grid-resizing-scheme/78398/5
        #     style={"height": 400, "resize": "vertical", "overflow": "hidden"},
        # ),
        # dmc.Space(h=40),
        # # Tabela com as estatísticas gerais por Veículo
        # dbc.Row(
        #     [
        #         dbc.Col(DashIconify(icon="mdi:bus-wrench", width=45), width="auto"),
        #         dbc.Col(
        #             dbc.Row(
        #                 [
        #                     html.H4(
        #                         "Tabela principais peças",
        #                         className="align-self-center",
        #                     ),
        #                     dmc.Space(h=5),
        #                     dbc.Row(
        #                         [
        #                             dbc.Col(gera_labels_inputs("visao-geral-tabela-principais-pecas"), width=True),
        #                             dbc.Col(
        #                                 html.Div(
        #                                     [
        #                                         html.Button(
        #                                             "Exportar para Excel",
        #                                             id="btn-exportar-tabela-veiculo",
        #                                             n_clicks=0,
        #                                             style={
        #                                                 "background-color": "#007bff",  # Azul
        #                                                 "color": "white",
        #                                                 "border": "none",
        #                                                 "padding": "10px 20px",
        #                                                 "border-radius": "8px",
        #                                                 "cursor": "pointer",
        #                                                 "font-size": "16px",
        #                                                 "font-weight": "bold",
        #                                             },
        #                                         ),
        #                                         dcc.Download(id="download-excel-mais-trocam-pecas"),
        #                                     ],
        #                                     style={"text-align": "right"},
        #                                 ),
        #                                 width="auto",
        #                             ),
        #                         ],
        #                         align="center",
        #                         justify="between",  # Deixa os itens espaçados
        #                     ),
        #                 ]
        #             ),
        #             width=True,
        #         ),
        #     ],
        #     align="center",
        # ),
    ]
)


##############################################################################
# Registro da página #########################################################
##############################################################################
dash.register_page(__name__, name="Visão Geral", path="/", icon="mdi:bus-alert")
