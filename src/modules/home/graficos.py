import pandas as pd
import plotly.express as px

def grafico_custo_mensal(dataframe: pd.DataFrame) -> any:
    """
    Gera um gráfico de linha para comparar o custo mensal de peças recondicionadas e não recondicionadas.

    A função cria um gráfico interativo onde o eixo X mostra os meses e o eixo Y mostra o custo total
    para cada tipo de peça, com a linha colorida de acordo com o tipo de peça.

    Parâmetros:
    ----------
    dataframe : pd.DataFrame
        O DataFrame com os dados do custo das peças. As colunas devem ser:
        - 'mes' (str): O mês no formato 'YYYY-MM'.
        - 'custo_total' (float): O valor do custo total mensal.
        - 'tipo_peca' (str): O tipo de peça ('Recondicionada' ou 'Nao Recondicionada').

    Retorna:
    -------
    fig : plotly.graph_objects.Figure
        O gráfico de linha comparando os custos mensais das peças.
    """
    dataframe['tipo_peca'] = dataframe['tipo_peca'].replace({
        'Recondicionada': 'Peça Recondicionada',
        'Nao Recondicionada': 'Peça Nova'
    })
    fig = px.line(dataframe, 
                  x='mes', 
                  y='custo_total', 
                  color='tipo_peca', 
                  labels={'custo_total': 'Custo Total', 'mes': 'Mês'},
        )
    fig.update_layout(legend_title_text='Tipo de Peça')
    return fig

def grafico_troca_pecas_mensal(dataframe: pd.DataFrame) -> any:
    """
    Gera um gráfico de linha para comparar a quantidade de peças trocadas mensalmente, com a distinção entre peças recondicionadas e peças novas.

    A função cria um gráfico interativo onde o eixo X mostra os meses e o eixo Y mostra a quantidade total de peças trocadas,
    com a linha colorida de acordo com o tipo de peça (Recondicionada ou Nova).

    Parâmetros:
    ----------
    dataframe : pd.DataFrame
        O DataFrame com os dados das trocas de peças. As colunas devem ser:
        - 'mes' (str): O mês no formato 'YYYY-MM'.
        - 'quantidade_total' (int): A quantidade total de peças trocadas.
        - 'tipo_peca' (str): O tipo de peça ('Recondicionada' ou 'Nao Recondicionada').

    Retorna:
    -------
    fig : plotly.graph_objects.Figure
        O gráfico de linha comparando as quantidades mensais das peças trocadas.
    
    """
    dataframe['tipo_peca'] = dataframe['tipo_peca'].replace({
        'Recondicionada': 'Peça Recondicionada',
        'Nao Recondicionada': 'Peça Nova'
    })
    fig = px.line(dataframe, 
                  x='mes', 
                  y='quantidade_total', 
                  color='tipo_peca', 
                  labels={'quantidade_total': 'Quantidade Total', 'mes': 'Mês'},
        )
    fig.update_layout(legend_title_text='Tipo de Peça')
    return fig
