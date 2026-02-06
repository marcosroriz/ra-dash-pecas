#!/usr/bin/env python
# coding: utf-8

# Dashboard que lista o retrabalho de uma ou mais OS

##############################################################################
# IMPORTS ####################################################################
##############################################################################
# Bibliotecas básicas
from datetime import date
import pandas as pd
import datetime 

# Importar bibliotecas do dash básicas e plotly
from dash import Dash, html, dcc, callback, Input, Output, State
import dash
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
from modules.os.graficos import *
from modules.vidautil.vida_util_service import VidaUtilService
import modules.vidautil.tabelas as vida_util

##############################################################################
# LEITURA DE DADOS ###########################################################
##############################################################################
# Conexão com os bancos
pgDB = PostgresSingleton.get_instance()
pgEngine = pgDB.get_engine()

# Cria o serviço
vida_util_service = VidaUtilService(pgEngine)

# Modelos de veículos
df_modelos_veiculos = get_modelos_pecas_odometro(pgEngine)
lista_todos_modelos_veiculos = df_modelos_veiculos.to_dict(orient="records")
lista_todos_modelos_veiculos.insert(0, {"MODELO": "TODOS"})


##############################################################################
# CALLBACKS ##################################################################
##############################################################################

##############################################################################
# Callbacks para os inputs ###################################################
##############################################################################

@callback(
    Output("input-intervalo-datas-pecas-os", "maxDate"),
    Output("input-intervalo-datas-pecas-os", "value", allow_duplicate=True),  # allow_duplicate para permitir atualizar o valor mesmo que seja o mesmo (útil para resetar o input)
    Input("url", "pathname"),  # fires on page load
    prevent_initial_call=True,
)
def cb_input_datas_home_dinamico(_):
    hoje = date.today()
    return hoje, [date(2024, 8, 1), hoje]

# Função para validar o input
def input_valido(datas, lista_modelos, lista_oficinas, lista_secaos, lista_os):
    if datas is None or not datas or None in datas:
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

# Função para validar o input
def input_valido2(datas, lista_modelos, lista_pecas):
    if datas is None or not datas or None in datas:
        return False

    if lista_modelos is None or not lista_modelos or None in lista_modelos:
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

####FUNCAO DE AUXILIO
def remover_outliers_iqr(df, coluna):
    """
    Remove outliers com base no método do intervalo interquartil (IQR).
    """
    q1 = df[coluna].quantile(0.25)
    q3 = df[coluna].quantile(0.75)
    iqr = q3 - q1
    filtro = (df[coluna] >= (q1 - 1.5 * iqr)) & (df[coluna] <= (q3 + 1.5 * iqr))
    return df[filtro]


@callback(
    Output("input-select-modelo-veiculos-pecas-vida-util", "value"),
    Input("input-select-modelo-veiculos-pecas-vida-util", "value"),
)
def corrige_input_modelos(lista_modelos):
    return corrige_input(lista_modelos, "TODOS")



@callback(
    [
        Output("input-select-peca-vida-util", "options"),
        Output("input-select-peca-vida-util", "value"),
    ],
    [
        Input("input-intervalo-datas-pecas-os", "value"),
        Input("input-select-modelo-veiculos-pecas-vida-util", "value"),
        Input("input-select-peca-vida-util", "value"),  # <- Aqui está o segredo
    ]
)
def corrige_input_pecas(datas, lista_modelos, lista_pecas):
    """
    Atualiza as opções e o valor selecionado do dropdown de peças com base nos filtros aplicados.

    Parâmetros:
        datas (str | list): Intervalo de datas selecionado.
        lista_modelos (list): Lista de modelos de veículos selecionados.
        lista_pecas (list): Lista de peças selecionadas atualmente.

    Retorna:
        tuple:
            - options (list[dict]): Lista de opções para o dropdown no formato {"label": ..., "value": ...}.
            - value (list): Lista de valores corrigida para manter a seleção válida com base nos filtros.
    """

    if not datas or not lista_modelos:
        return [], None

    df_pecas = vida_util_service.get_pecas_input(datas, lista_modelos)

    if df_pecas.empty:
        return [], None

    # Ordena pelo campo quantidade desc (maior quantidade primeiro)
    df_pecas = df_pecas.sort_values(by="quantidade", ascending=False)

    # Monta opções com quantidade no label
    lista_options = [
        {"label": f"{row['nome_pecas']} ({row['quantidade']})", "value": row['nome_pecas']}
        for _, row in df_pecas.iterrows()
    ]

    # Insere "TODAS" no topo
    lista_options.insert(0, {"label": "TODAS", "value": "TODAS"})

    # Define valor padrão como o segundo item da lista (índice 1) ou "TODAS" se não existir
    default_valor = lista_options[1]['value'] if len(lista_options) > 1 else 'TODAS'

    def corrige_input(lista, termo_all="TODAS", default=None):
        # Aplica valor padrão apenas quando não houver lista definida (None)
        if lista is None:
            return [default]
        # Se houver múltiplos incluindo "TODAS", remove "TODAS"
        if len(lista) > 1 and termo_all in lista:
            return [item for item in lista if item != termo_all]
        # Retorna a própria lista (podendo ser apenas ["TODAS"])
        return lista

    # Corrige lista de peças com base na seleção do usuário
    lista_corrigida = corrige_input(lista_pecas, termo_all="TODAS", default=default_valor)

    return lista_options, lista_corrigida




##############################################################################
# Callbacks para os gráficos #################################################
##############################################################################


@callback(
    Output("boxplot-vida-util-pecas", "figure"),
    Output("tabela-vida-util-pecas", "rowData"),
    [
        Input("input-intervalo-datas-pecas-os", "value"),
        Input("input-select-modelo-veiculos-pecas-vida-util", "value"),
        Input("input-select-peca-vida-util", "value"),
    ],
)
def grafico_e_df_boxplot_pecas(datas, lista_modelos, lista_pecas):
    if not datas or not lista_modelos or not lista_pecas:
        return go.Figure(), []

    df = vida_util_service.get_pecas(datas, lista_modelos, lista_pecas)

    if df is None or df.empty or "km_efetivo_da_peca" not in df.columns:
        return go.Figure(), []

    # Remove outliers
    #df = remover_outliers_iqr(df, "km_efetivo_da_peca")
    df["km_efetivo_da_peca"] = df["km_efetivo_da_peca"].round(1)

    if "TODAS" in lista_pecas:
        fig = px.box(df, y="km_efetivo_da_peca", title="Boxplot Geral da Duração (km)")
    else:
        fig = px.box(df, x="nome_pecas", y="km_efetivo_da_peca")

    fig.update_layout(
        xaxis_title="Peça" if "TODAS" not in lista_pecas else "",
        yaxis_title="Duração (km)",
        boxmode="group",
        template="plotly_white"
    )

    return fig, df.to_dict('records')


@callback(
    Output("boxplot-vida-util-pecas-5000km", "figure"),
    #Output("tabela-vida-util-pecas", "rowData"),
    [
        Input("input-intervalo-datas-pecas-os", "value"),
        Input("input-select-modelo-veiculos-pecas-vida-util", "value"),
        Input("input-select-peca-vida-util", "value"),
    ],
)
def grafico_e_df_boxplot_pecas_5000km(datas, lista_modelos, lista_pecas):
    if not datas or not lista_modelos or not lista_pecas:
        return go.Figure()#, []

    df = vida_util_service.get_pecas(datas, lista_modelos, lista_pecas)

    if df is None or df.empty or "km_efetivo_da_peca" not in df.columns:
        return go.Figure()#, []

    # Remove outliers
    #df = remover_outliers_iqr(df, "km_efetivo_da_peca")
    df["km_efetivo_da_peca"] = df["km_efetivo_da_peca"].round(1)
    df = df[df["km_efetivo_da_peca"] > 5000]

    if "TODAS" in lista_pecas:
        fig = px.box(df, y="km_efetivo_da_peca", title="Boxplot Geral da Duração (km)")
    else:
        fig = px.box(df, x="nome_pecas", y="km_efetivo_da_peca")

    fig.update_layout(
        xaxis_title="Peça" if "TODAS" not in lista_pecas else "",
        yaxis_title="Duração (km)",
        boxmode="group",
        template="plotly_white"
    )

    return fig#, df.to_dict('records')

# boxplot-vida-util-pecas-5000km
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
            Input("input-intervalo-datas-pecas-os", "value"),
            Input("input-select-modelo-veiculos-pecas-vida-util", "value"),
            Input("input-select-peca-vida-util", "value"),
        ],
    )
    def atualiza_labels_inputs(datas, lista_modelos, lista_pecas):
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
        lista_oficina = 'TODAS'
        lista_secao = 'TODAS'
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
### Callbacks para os dowload #################################################
##############################################################################

@callback(
    Output("download-excel-tabela-vida-util-pecas", "data"),
    Input("btn-exportar-tabela-vida-util-pecas", "n_clicks"),
    State("input-intervalo-datas-pecas-os", "value"),
    State("input-select-modelo-veiculos-pecas-vida-util", "value"),
    State("input-select-peca-vida-util", "value"),
    prevent_initial_call=True
)
def download_excel_tabela_vida_util_pecas(n_clicks, datas, lista_modelos, lista_pecas):
    if not n_clicks or n_clicks <= 0:
        return dash.no_update

    date_now = date.today().strftime('%d-%m-%Y')

    df = vida_util_service.get_pecas(datas, lista_modelos, lista_pecas)
    #df = remover_outliers_iqr(df, "km_efetivo_da_peca")
    df["km_efetivo_da_peca"] = df["km_efetivo_da_peca"].round(1)

    df.rename(columns={
        "nome_pecas": "NOME DA PEÇA",
        "id_veiculo": "VEICULO",
        "numero_troca": "N° TROCA",
        "data_primeira_troca": "DATA PRIMEIRA TROCA",
        "data_segunda_troca": "DATA SEGUNDA TROCA",
        "dias_efetivo_da_peca": "DURAÇÃO DE DIAS EFETIVOS",
        "odometro_primeira_troca": "HODOMETRO DA PRIMEIRA TROCA",
        "odometro_segunda_troca": "HODOMETRO DA SEGUNDA TROCA",
        "hodometro_atual_gps": "HODOMETRO ATUAL",
        "km_efetivo_da_peca": "DURAÇÃO KM EFETIVO",
        "quantidade_troca_1": "QTD TROCA 1",
        "quantidade_troca_2": "QTD TROCA 2"
    }, inplace=True)
    
    excel_data = gerar_excel(df=df)
    return dcc.send_bytes(excel_data, f"tabela_vida_util_pecas_{date_now}.xlsx")



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
                                                    "Visão da\u00a0",
                                                    html.Strong("vida útil das peças"),
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
                                                        id="input-intervalo-datas-pecas-os",
                                                        allowSingleDateInRange=True,
                                                        type="range",
                                                        minDate=date(2024, 1, 1),
                                                        maxDate=date.today(),
                                                        value=[date(2025, 1, 1), date.today()],
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
                                                        id="input-select-modelo-veiculos-pecas-vida-util",
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
                                                    dbc.Label("Peça específica"),
                                                    dcc.Dropdown(
                                                        id="input-select-peca-vida-util",
                                                        options=[],  # começa vazio, o callback vai preencher
                                                        multi=True,
                                                        value=[],    # começa vazio, o callback define o valor inicial
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
                                dmc.Space(h=30),
                                dbc.Row(
                                    [
                                        dbc.Col(DashIconify(icon="mdi:chart-line", width=45), width="auto"),
                                        dbc.Col(
                                            dbc.Row(
                                                [
                                                    html.H4(
                                                        "Boxplot vida útil das peças",
                                                        className="align-self-center",
                                                    ),
                                                    dmc.Space(h=5),
                                                    gera_labels_inputs("vida-util-das-pecas"),
                                                ]
                                            ),
                                            width=True,
                                        ),
                                    ],
                                    align="center",
                                ),
                                dcc.Graph(id="boxplot-vida-util-pecas"),
                                dmc.Space(h=40),
                                dbc.Row(
                                    [
                                        dbc.Col(DashIconify(icon="mdi:chart-line", width=45), width="auto"),
                                        dbc.Col(
                                            dbc.Row(
                                                [
                                                    html.H4(
                                                        "Boxplot vida útil das peças acima de 5000 km",
                                                        className="align-self-center",
                                                    ),
                                                    dmc.Space(h=5),
                                                    gera_labels_inputs("vida-util-das-pecas-5000km"),
                                                ]
                                            ),
                                            width=True,
                                        ),
                                    ],
                                    align="center",
                                ),
                                dcc.Graph(id="boxplot-vida-util-pecas-5000km"),
                                dmc.Space(h=40),
                                # Tabela com as estatísticas gerais de Retrabalho
                                dbc.Row(
                                    [
                                        dbc.Col(DashIconify(icon="mdi:gear", width=45), width="auto"),
                                        dbc.Col(
                                            dbc.Row(
                                                [
                                                    html.H4(
                                                        "Tabela de vida útil das peças",
                                                        className="align-self-center",
                                                    ),
                                                    dmc.Space(h=5),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(gera_labels_inputs("tabela-vida-util-pecas"), width=True),
                                                            dbc.Col(
                                                                html.Div(
                                                                    [
                                                                        html.Button(
                                                                            "Exportar para Excel",
                                                                            id="btn-exportar-tabela-vida-util-pecas",
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
                                                                        dcc.Download(id="download-excel-tabela-vida-util-pecas"),
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
                                        id="tabela-vida-util-pecas",
                                        columnDefs=vida_util.tbl_vida_util_pecas,
                                        rowData=[],
                                        defaultColDef={"filter": True, "floatingFilter": True},
                                        columnSize="autoSize",
                                        dashGridOptions={
                                            "localeText": locale_utils.AG_GRID_LOCALE_BR,
                                            },
                                        # Permite resize --> https://community.plotly.com/t/anyone-have-better-ag-grid-resizing-scheme/78398/5
                                        style={"height": 400, "resize": "vertical", "overflow": "hidden"},
                                        dangerously_allow_code=True, 
                                    ),
                                dmc.Space(h=40),
                            ]
                        ),
                    ],
                    md=12,
                ),
            ]
        ),
    ]
)
##############################################################################
# Registro da página #########################################################
##############################################################################
dash.register_page(__name__, name="Vida útil", path="/Vida-util", icon="mdi:bus-alert")
