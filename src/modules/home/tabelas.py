tbl_ranking_de_pecas_mais_trocadas = [
    {
        "field": "posicao",
        "headerName": "POSIÇÃO",
        "pinned": "left",
        "minWidth": 200,
        "type": ["numericColumn"],
    },
    {"field": "nome_peca", "headerName": "NOME DA PEÇA", "pinned": "left", "minWidth": 450},
    {
        "field": "quantidade",
        "headerName": "QUANTIDADE",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "maxWidth": 200,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
    },
    {
        "field": "frequencia",
        "headerName": "FREQUÊNCIA",
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        "type": ["numericColumn"],
    },
    {
        "field": "valor_total",
        "headerName": "VALOR TOTAL",
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        "valueFormatter": {"function": "'R$' + params.value.toLocaleString('pt-BR')"},
        "type": ["numericColumn"],
    },
    {
        "field": "valor_por_unidade",
        "headerName": "VALOR POR UNIDADE",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "'R$' + params.value.toLocaleString('pt-BR')"},
        "maxWidth": 200,
        "type": ["numericColumn"],
    },
]


tbl_veiculos_que_mais_trocam_pecas = [
    {
        "field": "EQUIPAMENTO",
        "headerName": "VEÍCULO",
        "pinned": "left",
    },
    {"field": "MODELO", "headerName": "MODELO", "minWidth": 200, "maxWidth": 200},
    {"field": "quantidade_total", "headerName": "QUANTIDADE DE PEÇAS", "filter": "agNumberColumnFilter", "minWidth": 200, "maxWidth": 200},
    {
        "field": "valor_total",
        "headerName": "VALOR GASTO",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
    },
    {
        "field": "valor_medio_modelo",
        "headerName": "VALOR MÉDIO DO MODELO",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
    },
    {
        "field": "diferenca_valor",
        "headerName": "VALOR MEDIO - VALOR GASTO",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
    },
    {
        "field": "media_mensal",
        "headerName": "MÉDIA DO GASTO POR MÊS",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "params.value.toLocaleString('pt-BR') + '%'"},
        "type": ["numericColumn"],
    },
]

# Tabela Top Veiculo
tbl_pincipais_pecas = [
    {
        "field": "nome_peca",
        "headerName": "PEÇA",
        "minWidth": 350,
        "pinned": "left",
    },
    {
        "field": "quantidade",
        "headerName": "QUANTIDADE",
        "minWidth": 200,
        "maxWidth": 200,
        "pinned": "left",
        "type": ["numericColumn"],

    },
    {
        "field": "valor_total",
        "headerName": "VALOR TOTAL",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "filter": "agNumberColumnFilter",
        "maxWidth": 250,
        "valueFormatter": {"function": "'R$' + params.value.toLocaleString('pt-BR')"},
        "type": ["numericColumn"],
    },
    {
        "field": "valor_por_unidade",
        "headerName": "VALOR POR PEÇA",
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        #"flex": 1,  # <-- esta linha permite que essa coluna "preencha" o espaço restante
        "valueFormatter": {"function": "'R$' + params.value.toLocaleString('pt-BR')"},
        "type": ["numericColumn"],
        "autoSize": True, 
    }
    # {
    #     "field": "QUANTIDADE_MES",
    #     "headerName": "QUANTIDADE POR MÊS",
    #     "wrapHeaderText": True,
    #     "autoHeaderHeight": True,
    #     "filter": "agNumberColumnFilter",
    #     "maxWidth": 350,
    #     "type": ["numericColumn"],
    # },
]
