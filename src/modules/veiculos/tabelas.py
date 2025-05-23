
# Tabela Top OS Colaborador
tbl_veiculos_pecas = [
    {
        "field": "nome_pecas",
        "headerName": "PEÇAS",
        "pinned": "left",
    },
    {
        "field": "data_ultima_troca",
        "headerName": "ULTIMA TROCA",
        "minWidth": 200, "maxWidth": 200
    },
    {
        "field": "km_desde_penultima_troca",
        "headerName": "HODOMETRO",
        "filter": "agNumberColumnFilter",
        "minWidth": 200,
        "valueFormatter": {"function": "params.value.toLocaleString('pt-BR') + 'Km'"},
        "maxWidth": 200
    },
]