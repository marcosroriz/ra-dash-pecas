tbl_ranking_de_pecas_mais_trocadas = [
    {
        "field": "POSICAO",
        "headerName": "POSIÇÃO",
        "pinned": "left",
        "minWidth": 200,
    },
    {"field": "PECA", "headerName": "NOME DA PEÇA", "pinned": "left", "minWidth": 450},
    {
        "field": "QUANTIDADE",
        "headerName": "QUANTIDADE",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "maxWidth": 200,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
    },
    {
        "field": "FREQUENCIA",
        "headerName": "FREQUÊNCIA",
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        "valueFormatter": {"function": "params.value.toLocaleString('pt-BR') + '%'"},
        "type": ["numericColumn"],
    },
    {
        "field": "VALOR_TOTAL",
        "headerName": "VALOR TOTAL",
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        "valueFormatter": {"function": "params.value.toLocaleString('pt-BR') + '%'"},
        "type": ["numericColumn"],
    },
    {
        "field": "VALOR_UNIDADE",
        "headerName": "VALOR POR UNIDADE",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        "type": ["numericColumn"],
    },
]

# Tabela Top OS Colaborador
tbl_veiculos_que_mais_trocam_pecas = [
    {
        "field": "VEICULO",
        "headerName": "VEÍCULO",
        "pinned": "left",
    },
    {"field": "MODELO", "headerName": "MODELO", "minWidth": 200, "maxWidth": 200},
    {"field": "QUANTIDADE", "headerName": "QUANTIDADE DE PEÇAS", "filter": "agNumberColumnFilter", "minWidth": 200, "maxWidth": 200},
    {
        "field": "VALOR_GASTO",
        "headerName": "VALOR GASTO",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
    },
    {
        "field": "VALOR_MEDIO_MODELO",
        "headerName": "VALOR MÉDIO DO MODELO",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
    },
    {
        "field": "DIFERANÇA",
        "headerName": "VALOR MEDIO - VALOR GASTO",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
    },
    {
        "field": "MEDIA_POR_MES",
        "headerName": "MÉDIA DO GASTO POR MÊS",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "params.value.toLocaleString('pt-BR') + '%'"},
        "type": ["numericColumn"],
    },
]

# Tabela Top Veiculo
tbl_pincipais_pecas = [
    {
        "field": "PECA",
        "headerName": "PEÇA",
        "minWidth": 350,
        "pinned": "left",
    },
    {
        "field": "QUANTIDADE",
        "headerName": "QUANTIDADE",
        "minWidth": 200,
        "maxWidth": 200,
        "pinned": "left",
    },
    {
        "field": "VALOR_TOTAL",
        "headerName": "VALOR TOTAL",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
    },
    {
        "field": "VALOR_POR_PECA",
        "headerName": "VALOR POR PEÇA",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "params.value.toLocaleString('pt-BR') + '%'"},
        "type": ["numericColumn"],
    },
    {
        "field": "QUANTIDADE_MES",
        "headerName": "QUANTIDADE POR MÊS",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        "type": ["numericColumn"],
    },
]
