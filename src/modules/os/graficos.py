import plotly.graph_objects as go
import pandas as pd

def grafico_pecas_mais_trocadas(dataframe: pd.DataFrame, titulo: str = "Peças Mais Trocadas"):
    """
    Gera um gráfico de barras horizontal interativo com as peças mais trocadas.

    Args:
        dataframe (pd.DataFrame): DataFrame com colunas 'Peça' e 'Quantidade'.
        titulo (str): Título do gráfico.

    Returns:
        plotly.graph_objects.Figure: Figura Plotly pronta para exibição.
    """
    df = dataframe.head(10).sort_values(by="percentual")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df["pecas"],
        x=df["percentual"],
        orientation='h',
        text=[f"{v:.0f}%" for v in df["percentual"]],
        textposition="inside",
        insidetextanchor="middle",
        marker=dict(
            color=df["percentual"],
            colorscale="Bluered",  # Pode ser personalizado
            line=dict(width=0)
        ),
        hovertemplate="%{y}<br>%{x:.1f}%" + "<extra></extra>",
    ))

    fig.update_layout(
        #title=titulo,
        #title_x=0.5,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            range=[0, 100],
            title="Percentual (%)",  # só troque o título

        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
        ),
        template="simple_white",
        height=400,
    )

    return fig