import plotly.graph_objects as go
import pandas as pd

def grafico_pecas_mais_trocadas(dataframe: pd.DataFrame, titulo: str = "Peças Mais Trocadas"):
    df = dataframe.copy()
    df = df.sort_values(by="percentual", ascending=True)

    # Filtrar apenas peças com percentual > 0 para foco visual
    df = df[df["percentual"] > 0].tail(10)

    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Nenhuma peça com percentual relevante", height=300)
        return fig

    # Truncar nomes longos e manter original no hover
    df["pecas_truncadas"] = df["pecas"].apply(lambda x: x if len(x) <= 40 else x[:40] + "...")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df["pecas_truncadas"],
        x=df["percentual"],
        orientation='h',
        text=[f"{p:.1f}% ({q})" for p, q in zip(df["percentual"], df["total_trocas"])],
        textposition="auto",
        marker=dict(
            color=df["percentual"],
            colorscale="Reds",
            line=dict(color='rgba(0,0,0,0)', width=1)
        ),
        customdata=df["pecas"],  # nome completo no hover
        hovertemplate="<b>%{customdata}</b><br>Percentual: %{x:.1f}%<br>Qtd: %{text}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text=titulo, x=0.5, font=dict(size=20)),
        xaxis=dict(title="Percentual (%)", range=[0, 100]),
        yaxis=dict(title="", automargin=True),
        margin=dict(l=120, r=20, t=60, b=40),
        height=500,
        template="plotly_white",
        bargap=0.4,
    )

    return fig
