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
from modules.prontuario.prontuario_service import ProntuarioService
from modules.prontuario.tabelas import *

##############################################################################
# LEITURA DE DADOS ###########################################################
##############################################################################
# Conexão com os bancos
pgDB = PostgresSingleton.get_instance()
pgEngine = pgDB.get_engine()

# Cria o serviço
prontuario_service = ProntuarioService(pgEngine)

# Modelos de veículos
df_modelos_veiculos = get_modelos(pgEngine)
lista_todos_modelos_veiculos = df_modelos_veiculos.to_dict(orient="records")
lista_todos_modelos_veiculos.insert(0, {"MODELO": "TODOS"})

df_veiculos = get_veiculos(pgEngine)
lista_todos_veiculos = df_veiculos.to_dict(orient="records")
lista_todos_veiculos.insert(0, {"EQUIPAMENTO": "TODOS"})

df_grupo = get_grupo_pecas(pgEngine)
lista_todos_grupos = df_grupo.to_dict(orient="records")
lista_todos_grupos.insert(0, {"GRUPO": "TODOS"})

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
def input_valido(datas, lista_modelos, lista_veiculos, lista_grupos, lista_pecas):
    if datas is None or not datas or None in datas:
        return False

    if lista_modelos is None or not lista_modelos or None in lista_modelos:
        return False

    if lista_veiculos is None or not lista_veiculos or None in lista_veiculos:
        return False

    if lista_grupos is None or not lista_grupos or None in lista_grupos:
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
    Output("input-select-modelo-veiculos-prontuario", "value"),
    Input("input-select-modelo-veiculos-prontuario", "value"),
)
def corrige_input_modelos(lista_modelos):
    return corrige_input(lista_modelos, "TODOS")

@callback(
    Output("input-select-grupo-pecas-prontuario", "value"),
    Input("input-select-grupo-pecas-prontuario", "value"),
)
def corrige_input_grupos(lista_modelos):
    return corrige_input(lista_modelos, "TODOS")


@callback(
    Output("input-select-veiculos-prontuario", "value"),
    Input("input-select-veiculos-prontuario", "value"),
)
def corrige_input_veiculos(lista_grupos):
    return corrige_input(lista_grupos)


@callback(
    [
        Output("input-select-pecas-prontuario", "options"),
        Output("input-select-pecas-prontuario", "value"),
    ],
    [
            Input("input-intervalo-datas-prontuario", "value"),
            Input("input-select-modelo-veiculos-prontuario", "value"),
            Input("input-select-veiculos-prontuario", "value"),
            Input("input-select-grupo-pecas-prontuario", "value"),
            Input("input-select-pecas-prontuario", "value")
    ]
)
def corrige_input_pecas(datas, lista_modelos, lista_veiculos, lista_grupos, lista_pecas):
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

    df_lista_pecas_secao = prontuario_service.get_pecas(datas, lista_modelos, lista_veiculos, lista_grupos)

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


##############################################################################
# Callbacks para as tabelas ##################################################
##############################################################################



@callback(
        Output("loading-overlay-prontuario-pecas", "visible"),
        Output("tabela-prontuario-pecas", "rowData"),
    [
            Input("input-intervalo-datas-prontuario", "value"),
            Input("input-select-modelo-veiculos-prontuario", "value"),
            Input("input-select-veiculos-prontuario", "value"),
            Input("input-select-grupo-pecas-prontuario", "value"),
            Input("input-select-pecas-prontuario", "value")
    ],
)
def atualiza_tabela_prontuario_pecas(datas, lista_modelos, lista_veiculos, lista_grupos, lista_pecas):
    # Valida input
    if not input_valido(datas, lista_modelos, lista_veiculos, lista_grupos, lista_pecas):
        return []

    # Obtem dados
    df = prontuario_service.get_prontuario_pecas(datas, lista_modelos, lista_veiculos, lista_grupos, lista_pecas)

    return False, df.to_dict("records")

# Callback para atualizar o link de download quando o botão for clicado
@callback(
    Output("download-excel-tabela-prontuario-pecas", "data"),
    [
        Input("btn-exportar-tabela-prontuario-pecas", "n_clicks"),
        Input("input-intervalo-datas-prontuario", "value"),
        Input("input-select-modelo-veiculos-prontuario", "value"),
        Input("input-select-veiculos-prontuario", "value"),
        Input("input-select-grupo-pecas-prontuario", "value"),
        Input("input-select-pecas-prontuario", "value")
    ],
    prevent_initial_call=True
)
def download_excel_principais_pecas(n_clicks, datas, lista_modelos, lista_veiculos, lista_grupos, lista_pecas):
    if not n_clicks or n_clicks <= 0: # Garantre que ao iniciar ou carregar a page, o arquivo não seja baixado
        return dash.no_update

    date_now = date.today().strftime('%d-%m-%Y')
    
    # Obtem os dados
    df = prontuario_service.get_prontuario_pecas(datas, lista_modelos, lista_veiculos, lista_grupos, lista_pecas)

    excel_data = gerar_excel(df=df)
    return dcc.send_bytes(excel_data, f"tabela_prontuario_pecas_{date_now}.xlsx")

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
            Input("input-intervalo-datas-prontuario", "value"),
            Input("input-select-modelo-veiculos-prontuario", "value"),
            Input("input-select-veiculos-prontuario", "value"),
            Input("input-select-grupo-pecas-prontuario", "value"),
            Input("input-select-pecas-prontuario", "value"),
        ],
    )
    def atualiza_labels_inputs(datas, lista_modelos, lista_veiculos, lista_grupos, lista_pecas):
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

        lista_modelos_labels = []
        lista_veiculos_labels = []
        lista_pecas_labels = []
        lista_grupos_labels = []

        if lista_modelos is None or not lista_modelos or "TODOS" in lista_modelos:
            lista_modelos_labels.append(dmc.Badge("Todos os modelos", variant="outline"))
        else:
            for modelos in lista_modelos:
                lista_modelos_labels.append(dmc.Badge(modelos, variant="dot"))

        if lista_veiculos is None or not lista_veiculos or "TODOS" in lista_veiculos:
            lista_veiculos_labels.append(dmc.Badge("Todos os veiculos", variant="outline"))
        else:
            for veiculos in lista_veiculos:
                lista_veiculos_labels.append(dmc.Badge(veiculos, variant="dot"))

        if lista_grupos is None or not lista_grupos or "TODOS" in lista_grupos:
            lista_grupos_labels.append(dmc.Badge("Todos os grupos", variant="outline"))
        else:
            for grupos in lista_grupos:
                lista_grupos_labels.append(dmc.Badge(grupos, variant="dot"))

        if lista_pecas is None or not lista_pecas or "TODAS" in lista_pecas:
            lista_pecas_labels.append(dmc.Badge("Todas as peças", variant="outline"))
        else:
            for pecas in lista_pecas:
                lista_pecas_labels.append(dmc.Badge(f"Peças: {pecas}", variant="dot"))

        return [dmc.Group(labels_antes + datas_label + lista_modelos_labels + lista_grupos_labels + lista_pecas_labels)]

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
            id="loading-overlay-prontuario-pecas",
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
                                                    "Prontuario de\u00a0",
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
                                                        id="input-intervalo-datas-prontuario",
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
                                                        id="input-select-modelo-veiculos-prontuario",
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
                                                        id="input-select-veiculos-prontuario",
                                                        options=[{"label": os["EQUIPAMENTO"], "value": os["EQUIPAMENTO"]} for os in lista_todos_veiculos],
                                                        multi=True,
                                                        value=["TODOS"],
                                                        placeholder="Selecione um ou mais veiculos...",
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
                                                    dbc.Label("Grupo de Peças"),
                                                    dcc.Dropdown(
                                                        id="input-select-grupo-pecas-prontuario",
                                                        options=[{"label": os["GRUPO"], "value": os["GRUPO"]} for os in lista_todos_grupos],
                                                        multi=True,
                                                        value=["TODOS"],
                                                        placeholder="Selecione um ou mais grupo de pecas...",
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
                                                        id="input-select-pecas-prontuario",
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
                                "FICHA TÉCNICA/PRONTUÁRIO DE PEÇAS TROCADAS POR CADA VEÍCULO",
                                className="align-self-center",
                            ),
                            dmc.Space(h=5),
                            dbc.Row(
                                [
                                    dbc.Col(gera_labels_inputs("prontuario-pecas-tabela"), width=True),
                                    dbc.Col(
                                        html.Div(
                                            [
                                                html.Button(
                                                    "Exportar para Excel",
                                                    id="btn-exportar-tabela-prontuario-pecas",
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
                                                dcc.Download(id="download-excel-tabela-prontuario-pecas"),
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
            id="tabela-prontuario-pecas",
            columnDefs=tbl_prontuario_veiculo,
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
    ]
)


##############################################################################
# Registro da página #########################################################
##############################################################################
dash.register_page(__name__, name="Prontuário de peças", path="/prontuario_pecas", icon="mdi:bus-alert")
