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
from modules.veiculos.tabelas import *
# Imports específicos
from modules.veiculos.veiculos_service import VeiculosService

##############################################################################
# LEITURA DE DADOS ###########################################################
##############################################################################
# Conexão com os bancos
pgDB = PostgresSingleton.get_instance()
pgEngine = pgDB.get_engine()

veiculo_service = VeiculosService(pgEngine)

# Modelos de veículos
df_modelos_veiculos = get_modelos(pgEngine)
lista_todos_modelos_veiculos = df_modelos_veiculos.to_dict(orient="records")
lista_todos_modelos_veiculos.insert(0, {"MODELO": "TODOS"})


# Obtem a lista de Seções
df_secoes = get_secoes(pgEngine)
lista_todas_secoes = df_secoes.to_dict(orient="records")
lista_todas_secoes.insert(0, {"LABEL": "TODAS"})

# Colaboradores / Mecânicos
df_mecanicos = get_mecanicos(pgEngine)

# Obtem a lista de OS
df_lista_veiculos = get_lista_veiculos(pgEngine)
lista_todas_os = df_lista_veiculos.to_dict(orient="records")



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


# Corrige o input para garantir que o termo para todas ("TODAS") não seja selecionado junto com outras opções
def corrige_input_pecas_veiculos(lista):
    # Caso 1: Nenhuma opcao é selecionada, reseta para "TODAS"
    if not lista:
        return []

   
    if len(lista) > 1 :
        return lista[1:]


    # Por fim, se não caiu em nenhum caso, retorna o valor original
    return lista


@callback(
    Output("input-select-modelo-veiculo", "value"),
    Input("input-select-modelo-veiculo", "value"),
)
def corrige_input_modelos(lista_modelos):
    return corrige_input(lista_modelos, "TODOS")

@callback(
    [
        Output("input-select-veiculo", "options"),
        Output("input-select-veiculo", "value"),
    ],
    [
        Input("input-intervalo-datas-veiculos", "value"),
        Input("input-select-modelo-veiculo", "value"),
        Input("input-select-veiculo", "value"),

    ]
)
def corrige_input_pecas(datas, lista_modelos, veiculo):

    df_lista_os_secao = df_lista_veiculos

    
    df_lista_os_secao = veiculo_service.get_veiculos(datas, lista_modelos)

    lista_os_possiveis = df_lista_os_secao.to_dict(orient="records")

    lista_options = [{"label": os["LABEL"], "value": os["LABEL"]} for os in lista_os_possiveis]

    if veiculo and "50196" not in veiculo:
        df_lista_os_atual = df_lista_os_secao[df_lista_os_secao["LABEL"].isin(veiculo)]
        lista_os_corrigida = df_lista_os_atual["LABEL"].tolist()
    else:
        lista_os_corrigida = veiculo

    return lista_options, corrige_input_pecas_veiculos(lista_os_corrigida)

##############################################################################
# Callbacks para os gráficos #################################################
##############################################################################



##############################################################################
# Callbacks para as tabelas ##################################################
##############################################################################

@callback(
    [
        # Output("loading-overlay-visao-geral", "visible"),
        Output("tabela-principais-pecas", "rowData"),
    ],
    [
        Input("input-intervalo-datas-veiculos", "value"),
        Input("input-select-veiculo", "value"),

    ],
)
def atualiza_tabela_rank_pecas(datas, veiculo):

    # Obtem dados
    df = veiculo_service.get_table_pecas(datas, veiculo)

    return [df.to_dict("records")] 

# Callback para atualizar o link de download quando o botão for clicado
@callback(
    Output("download-excel-tabela-pecas-veiculos", "data"),
    [
        Input("btn-exportar-tabela-pecas-veiculos", "n_clicks"),
        Input("input-intervalo-datas-veiculos", "value"),
        Input("input-select-veiculo", "value"),
    ],
    prevent_initial_call=True
)
def download_excel_principais_pecas(n_clicks, datas, veiculo):
    if not n_clicks or n_clicks <= 0: # Garantre que ao iniciar ou carregar a page, o arquivo não seja baixado
        return dash.no_update

    date_now = date.today().strftime('%d-%m-%Y')
    
    # Obtem os dados
    df = veiculo_service.get_principais_pecas(datas, veiculo)

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
            Input("input-intervalo-datas-veiculos", "value"),
            Input("input-select-modelo-veiculo", "value"),
            Input("input-select-veiculo", "value"),
        ],
    )
    def atualiza_labels_inputs(datas, lista_modelo, veiculo):
        labels_antes = [
            # DashIconify(icon="material-symbols:filter-arrow-right", width=20),
            dmc.Badge("Filtro", color="gray", variant="outline"),
        ]

        datas_label = []
        lista_modelos_labels = []

        if not (datas is None or not datas) and datas[0] is not None and datas[1] is not None:
            # Formata as datas
            data_inicio_str = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim_str = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            datas_label = [dmc.Badge(f"{data_inicio_str} a {data_fim_str}", variant="outline")]

        if lista_modelo is None or not lista_modelo or "TODAS" in lista_modelo:
            lista_modelos_labels.append(dmc.Badge("Todos os modelos", variant="outline"))
        else:
            for modelo in lista_modelo:
                lista_modelos_labels.append(dmc.Badge(modelo, variant="dot"))

        veiculo_selecionado = dmc.Badge(veiculo, variant="dot")


        return [dmc.Group(labels_antes + datas_label + lista_modelos_labels + [veiculo_selecionado])]

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
                                                    "Visão das Peças por",
                                                    html.Strong("Veiculos"),
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
                                                        id="input-intervalo-datas-veiculos",
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
                                                        id="input-select-modelo-veiculo",
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
                                                    dbc.Label("Veiculo"),
                                                    dcc.Dropdown(
                                                        id="input-select-veiculo",
                                                        options=[{"label": os["LABEL"], "value": os["LABEL"]} for os in lista_todas_os],
                                                        multi=True,
                                                        value=["50196"],
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
        dmc.Space(h=40),
                # Tabela com as estatísticas gerais por Colaborador
        dbc.Row(
            [
                dbc.Col(DashIconify(icon="mdi:bus-wrench", width=45), width="auto"),
                dbc.Col(
                    dbc.Row(
                        [
                            html.H4(
                                "VIDA ÚTIL DAS PEÇAS",
                                className="align-self-center",
                            ),
                            dmc.Space(h=5),
                            dbc.Row(
                                [
                                    dbc.Col(gera_labels_inputs("visao-geral-tabela-principais-pecas"), width=True),
                                    dbc.Col(
                                        html.Div(
                                            [
                                                html.Button(
                                                    "Exportar para Excel",
                                                    id="btn-exportar-tabela-pecas-veiculos",
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
                                                dcc.Download(id="download-excel-tabela-pecas-veiculos"),
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
            columnDefs= tbl_veiculos_pecas,
            rowData=[],
            defaultColDef={
            "filter": True,
            "floatingFilter": True,
            "resizable": True,
            "autoSize": True,  # <- aqui já resolve para todas
            },
            columnSize="responsiveSizeToFit",  # Corrigido aqui
            dashGridOptions={
                "localeText": locale_utils.AG_GRID_LOCALE_BR,
            },
            style={"height": 400, "resize": "vertical", "overflow": "hidden"},
        ),
        dmc.Space(h=40),
    ]
)


##############################################################################
# Registro da página #########################################################
##############################################################################
dash.register_page(__name__, name="Veiculos", path="/veiculos_pecas", icon="mdi:bus-alert")
