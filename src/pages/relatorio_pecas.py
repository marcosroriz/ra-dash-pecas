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
from modules.relatoriopecas.relatorio_pecas_service import RelatorioPecasService
import modules.relatoriopecas.tabelas as relatorio_pecas

##############################################################################
# LEITURA DE DADOS ###########################################################
##############################################################################
# Conexão com os bancos
pgDB = PostgresSingleton.get_instance()
pgEngine = pgDB.get_engine()

# Cria o serviço
relatorio_pecas_util = RelatorioPecasService(pgEngine)

# Modelos de veículos
df_modelos_veiculos = get_modelos(pgEngine)
lista_todos_modelos_veiculos = df_modelos_veiculos.to_dict(orient="records")
lista_todos_modelos_veiculos.insert(0, {"MODELO": "TODOS"})


##############################################################################
# CALLBACKS ##################################################################
##############################################################################

@callback(
    [Output("tabela-relatorio-pecas-gerais", "rowData"),
     Output("boxplot-vida-util-total-pecas", "figure")],
    [
        Input("input-intervalo-datas-pecas-os", "value"),
        Input("input-select-modelo-veiculos-relatorio-pecas", "value"),
        Input("input-select-peca-relatorio", "value")
    ],
)
def tabela_relatio_peças(datas, lista_modelos, peça):
    if not datas or not lista_modelos or not peça:
        return [], go.Figure()

    df = relatorio_pecas_util.get_pecas(datas, lista_modelos, peça)


    fig = px.box(df, x="nome_peça", y="total_km_peca")

    fig.update_layout(
        xaxis_title="Peça",
        yaxis_title="Duração (km)",
        boxmode="group",
        template="plotly_white"
    )

    return df.to_dict('records'), fig

@callback(
    [Output("grafico-barras-qtd-peças-mes", "figure"),
     Output("grafico-barras-valor-peças-mes", "figure")],
    [
        Input("input-intervalo-datas-pecas-os", "value"),
        Input("input-select-modelo-veiculos-relatorio-pecas", "value"),
        Input("input-select-peca-relatorio", "value"),

    ],
)
def grafico_barras_qtd_valor_peças_mes(datas, lista_modelos, peça):
    #if not datas or not lista_modelos or not peça:
    #    return None
    df = relatorio_pecas_util.get_df_graficos(datas, lista_modelos, peça)
    if df.empty:
        return go.Figure(), go.Figure()
        
    df['mes_ano'] = pd.to_datetime(df['mes_ano'])
    df['mes_ano'] = df['mes_ano'].dt.strftime('%B/%Y') 
    
    # Cria o gráfico diretamente
    fig_qtd = px.bar(
    df,
    x='mes_ano',
    y='qtd_pecas_para_trocar',
    labels={'mes_ano': 'Mês', 'qtd_pecas_para_trocar': 'Qtd. peças para trocar'},
    title='Quantidade de Peças para trocar por Mês'
    )
    fig_qtd.update_traces(
        hovertemplate="<b>Mês:</b> %{x}<br><b>Qtd. peças:</b> %{y}<extra></extra>"
    )
    
    fig_valor = px.bar(
    df,
    x='mes_ano',
    y='valor_esperado',
    labels={'mes_ano': 'Mês', 'valor_esperado': 'Valor de peças para Trocar'},
    title='Valor de Peças para trocar por Mês'
    )
    fig_valor.update_traces(
        marker_color='red',
        hovertemplate="<b>Mês:</b> %{x}<br><b>Valor esperado:</b> R$ %{y:,.2f}<extra></extra>"
    )
    return fig_qtd, fig_valor


##############################################################################
# Callbacks para os inputs ###################################################
##############################################################################

@callback(
    [
        Output("input-select-peca-relatorio", "options"),
        Output("input-select-peca-relatorio", "value"),
    ],
    [
        Input("input-intervalo-datas-pecas-os", "value"),
        Input("input-select-modelo-veiculos-relatorio-pecas", "value"),
        Input("input-select-peca-relatorio", "value"),  # <- Aqui está o segredo
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

    df_pecas = relatorio_pecas_util.get_pecas_input(datas, lista_modelos)

    if df_pecas.empty:
        return [], None

    # Ordena pelo campo quantidade desc (maior quantidade primeiro)
    #df_pecas = df_pecas.sort_values(by="quantidade", ascending=False)

    # Monta opções com quantidade no label
    lista_options = [
        {"label": f"{row['nome_peça']}", "value": row['nome_peça']}
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
def input_valido2(datas, lista_modelos):
    if datas is None or not datas or None in datas:
        return False

    if lista_modelos is None or not lista_modelos or None in lista_modelos:
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
    Output("input-select-modelo-veiculos-relatorio-pecas", "value"),
    Input("input-select-modelo-veiculos-relatorio-pecas", "value"),
)
def corrige_input_modelos(lista_modelos):
    return corrige_input(lista_modelos, "TODOS")


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
            Input("input-select-modelo-veiculos-relatorio-pecas", "value"),
        ],
    )
    def atualiza_labels_inputs(datas, lista_modelos):
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

        return [dmc.Group(labels_antes + datas_label + lista_oficinas_labels + lista_os_labels)]

    # Cria o componente
    return dmc.Group(id=f"{campo}-labels", children=[])

##############################################################################
### Callbacks para os dowload ################################################
##############################################################################

@callback(
    Output("download-excel-tabela-relatorio-pecas", "data"),
    Input("btn-exportar-tabela-relatorio-pecas", "n_clicks"),
    State("input-intervalo-datas-pecas-os", "value"),
    State("input-select-modelo-veiculos-relatorio-pecas", "value"),
    Input("input-select-peca-relatorio", "value"),
    prevent_initial_call=True
)
def download_excel_tabela_vida_util_pecas(n_clicks, datas, lista_modelos, peça):
    if not n_clicks or n_clicks <= 0:
        return dash.no_update
    df = relatorio_pecas_util.get_pecas(datas, lista_modelos, peça)

    if df.empty:
        return go.Figure(), go.Figure()
    
    date_now = date.today().strftime('%d-%m-%Y')

    df.rename(columns={ 
        "id_veiculo": "ID DO VEÍCULO",
        "nome_pecas": "NOME DA PEÇA",
        "modelo_veiculo": "MODELO",
        "situacao_peca": "STATUS DA PEÇA",
        "media_km_entre_trocas": "MÉDIA DURAÇÃO KM",
        "data_primeira_troca": "DATA TROCA",
        "odometro_troca": "HODÔMETRO DA TROCA",
        "hodometro_atual_gps": "HODÔMETRO ATUAL",
        "estimativa_odometro_proxima_troca": "HODÔMETRO DA PRÓXIMA TROCA",
        "diferenca_entre_hodometro_estimativa_e_atual": "DIFERENÇA ESTIMATIVA E ATUAL",
        "total_km_peca": "KM TOTAL(RODADO) DA PEÇA",
        "ultrapassou_estimativa": "ULTRAPASSOU KM ESPERADO",
        "media_km_diario_veiculo": "MEDIA DE KM DIÁRIO DO VEÍCULO",
        "calculo_dias": "DIAS ATÉ A TROCA",
        "data_estimada": "DATA ESTIMADA PARA TROCA"
    }, inplace=True)

    excel_data = gerar_excel(df=df)

    return dcc.send_bytes(excel_data, f"tabela_relatorio_pecas_{date_now}.xlsx")



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
                                                    html.Strong("Relatório das peças"),
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
                                                        id="input-select-modelo-veiculos-relatorio-pecas",
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
                                                    dbc.Label("Peça específica"),
                                                    dcc.Dropdown(
                                                        id="input-select-peca-relatorio",
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
                                dmc.Space(h=40),
                                dbc.Row(
                                    [
                                        dbc.Col(DashIconify(icon="mdi:chart-line", width=45), width="auto"),
                                        dbc.Col(
                                            dbc.Row(
                                                [
                                                    html.H4(
                                                        "Trocas esperadas por mês",
                                                        className="align-self-center",
                                                    ),
                                                    dmc.Space(h=5),
                                                    gera_labels_inputs("pecas-esperadas-mes"),
                                                ]
                                            ),
                                            width=True,
                                        ),
                                    ],
                                    align="center",
                                ),
                                dcc.Graph(id="grafico-barras-qtd-peças-mes"),
                                dmc.Space(h=40),
                                dbc.Row(
                                    [
                                        dbc.Col(DashIconify(icon="mdi:chart-line", width=45), width="auto"),
                                        dbc.Col(
                                            dbc.Row(
                                                [
                                                    html.H4(
                                                        "Preço esperadas por mês",
                                                        className="align-self-center",
                                                    ),
                                                    dmc.Space(h=5),
                                                    gera_labels_inputs("preco-pecas-por-mes"),
                                                ]
                                            ),
                                            width=True,
                                        ),
                                    ],
                                    align="center",
                                ),
                                dcc.Graph(id="grafico-barras-valor-peças-mes"),
                                dmc.Space(h=40),
                                dbc.Row(
                                    [
                                        dbc.Col(DashIconify(icon="mdi:chart-line", width=45), width="auto"),
                                        dbc.Col(
                                            dbc.Row(
                                                [
                                                    html.H4(
                                                        "Boxplot vida útil total das peças",
                                                        className="align-self-center",
                                                    ),
                                                    dmc.Space(h=5),
                                                    gera_labels_inputs("vida-util--total-das-pecas"),
                                                ]
                                            ),
                                            width=True,
                                        ),
                                    ],
                                    align="center",
                                ),
                                dcc.Graph(id="boxplot-vida-util-total-pecas"),
                                dmc.Space(h=40),
                                # Tabela com as estatísticas gerais de Retrabalho
                                dbc.Row(
                                    [
                                        dbc.Col(DashIconify(icon="mdi:gear", width=45), width="auto"),
                                        dbc.Col(
                                            dbc.Row(
                                                [
                                                    html.H4(
                                                        "Tabela relatório de peças",
                                                        className="align-self-center",
                                                    ),
                                                    dmc.Space(h=5),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(gera_labels_inputs("tabela-relatorio-pecas"), width=True),
                                                            dbc.Col(
                                                                html.Div(
                                                                    [
                                                                        html.Button(
                                                                            "Exportar para Excel",
                                                                            id="btn-exportar-tabela-relatorio-pecas",
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
                                                                        dcc.Download(id="download-excel-tabela-relatorio-pecas"),
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
                                        columnDefs=relatorio_pecas.tbl_relatorio_pecas,
                                        id="tabela-relatorio-pecas-gerais",
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
                                dmc.Space(h=20),
                                html.H6("Legenda: Status da Peça (Vida útil total)", style={"marginBottom": "5px"}),
                                html.Div(
                                    [
                                        html.Div([
                                            html.Span("●", style={"color": "#2ecc71", "fontSize": "24px", "marginRight": "12px"}),
                                            html.Span("Verde — Dentro da estimativa - Menor que 65%", style={"fontSize": "18px"})
                                        ], style={"marginRight": "40px"}),

                                        html.Div([
                                            html.Span("●", style={"color": "#f1c40f", "fontSize": "24px", "marginRight": "12px"}),
                                            html.Span("Amarelo — Maior que 65%", style={"fontSize": "18px"})
                                        ], style={"marginRight": "40px"}),

                                        html.Div([
                                            html.Span("●", style={"color": "#e67e22", "fontSize": "24px", "marginRight": "12px"}),
                                            html.Span("Laranja — Maior que 90%", style={"fontSize": "18px"})
                                        ], style={"marginRight": "40px"}),

                                        html.Div([
                                            html.Span("●", style={"color": "#e74c3c", "fontSize": "24px", "marginRight": "12px"}),
                                            html.Span("Vermelho — Ultrapassou o limite", style={"fontSize": "18px"})
                                        ])
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexWrap": "wrap",
                                        "justifyContent": "center",
                                        "alignItems": "center",
                                        "marginTop": "5px",
                                        "gap": "20px"
                                    }
                                ),
                                dmc.Space(h=50),
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
dash.register_page(__name__, name="Relatório de peças", path="/relatorio-pecas", icon="mdi:bus-alert")
