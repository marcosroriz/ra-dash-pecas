import plotly.graph_objects as go
import pandas as pd

def grafico_pecas_mais_trocadas(dataframe: pd.DataFrame, titulo: str = "Peças Mais Trocadas"):
    """
    Gera um gráfico de barras horizontal interativo com as peças mais trocadas.

    Args:
        dataframe (pd.DataFrame): DataFrame com colunas 'pecas', 'total_trocas', 'percentual'.
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
        text=[f"{p:.0f}% ({q})" for p, q in zip(df["percentual"], df["total_trocas"])],
        textposition="inside",
        insidetextanchor="start",
        marker=dict(
            color=df["percentual"],
            colorscale="Bluered",
            line=dict(width=0)
        ),
        hovertemplate="%{y}<br>%{x:.1f}%<br>Qtd: %{customdata}" + "<extra></extra>",
        customdata=df["total_trocas"]
    ))

    fig.update_layout(
        title=titulo,
        title_x=0.5,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            range=[0, 100],
            title="Percentual (%)",
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
        ),
        template="simple_white",
        height=400,
    )

    return fig
