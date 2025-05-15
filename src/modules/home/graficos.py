import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def grafico_custo_quantidade_mensal(
    df_custo: pd.DataFrame,
    df_quantidade: pd.DataFrame
) -> go.Figure:
    """
    Gera dois gráficos de linha lado a lado:
        1. Custo mensal por tipo de peça
        2. Quantidade mensal de peças trocadas por tipo

    Parâmetros
    ----------
    df_custo : pd.DataFrame
        Deve ter as colunas:
            - 'mes' (datetime ou str 'YYYY-MM')
            - 'custo_total' (float)
            - 'tipo_peca' (str)  -> valores 'Recondicionada' ou 'Nao Recondicionada'

    df_quantidade : pd.DataFrame
        Deve ter as colunas:
            - 'mes' (datetime ou str 'YYYY-MM')
            - 'quantidade_total' (int)
            - 'tipo_peca' (str)

    Retorno
    -------
    fig : plotly.graph_objects.Figure
        Figure com os dois subplots.
    """

    # Padroniza rótulos dos tipos de peça
    mapa_tipos = {"Recondicionada": "Peça Recondicionada",
                  "Nao Recondicionada": "Peça Nova"}
    df_custo["tipo_peca"] = df_custo["tipo_peca"].replace(mapa_tipos)
    df_quantidade["tipo_peca"] = df_quantidade["tipo_peca"].replace(mapa_tipos)

    # Garante colunas de mês legíveis
    df_custo["mes"] = pd.to_datetime(df_custo["mes"])
    df_quantidade["mes"] = pd.to_datetime(df_quantidade["mes"])
    df_custo["mes_fmt"] = df_custo["mes"].dt.strftime("%b %Y")
    df_quantidade["mes_fmt"] = df_quantidade["mes"].dt.strftime("%b %Y")

    # Cria os dois subplots
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Custo com Peças por Mês",
                        "Quantidade de Peças Trocadas por Mês"),
        shared_yaxes=False
    )

    # ---------- Gráfico 1: CUSTO ----------
    for tipo in df_custo["tipo_peca"].unique():
        dados = df_custo[df_custo["tipo_peca"] == tipo]
        fig.add_trace(
            go.Scatter(
                x=dados["mes_fmt"],
                y=dados["custo_total"],
                mode="lines+markers",
                name=tipo
            ),
            row=1, col=1
        )

    # ---------- Gráfico 2: QUANTIDADE ----------
    for tipo in df_quantidade["tipo_peca"].unique():
        dados = df_quantidade[df_quantidade["tipo_peca"] == tipo]
        fig.add_trace(
            go.Scatter(
                x=dados["mes_fmt"],
                y=dados["quantidade_total"],
                mode="lines+markers",
                name=tipo,
                showlegend=False  # evita legenda duplicada
            ),
            row=1, col=2
        )

    # Layout final
    fig.update_layout(
        height=500,
        width=1200,
        legend_title="Tipo de Peça"
    )

    return fig
