tbl_vida_util_pecas = [
    {
        "field": "nome_pecas",
        "headerName": "NOME DA PEÇA",
        "pinned": "left",
        "minWidth": 400,
        "type": ["numericColumn"],
    },
    {
        "field": "id_veiculo",
        "headerName": "VEICULO",
        "pinned": "left",
        "minWidth": 100,
        "type": ["numericColumn"],
    },
    {
    "field": "numero_troca",
        "headerName": "N° TROCA",
        "pinned": "left",
        "minWidth": 25,
        "type": ["numericColumn"],
    },
    {"field": "data_os",  
     "headerName": "DATA TROCA",
     "minWidth": 450
     },
    {
     "field": "data_proxima_troca", 
     "headerName": "DATA SEGUNDA TROCA", 
     "minWidth": 450
    },
    {
        "field": "duracao_dias",
        "headerName": "DURAÇÃO (DIAS)",
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        "type": ["numericColumn"],
    },
    {
        "field": "ultimo_hodometro",
        "headerName": "KM DA TROCA",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "maxWidth": 200,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
    },
    {
        "field": "km_proxima_troca",
        "headerName": "KM DA SEGUNDA TROCA",
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        "type": ["numericColumn"],
    },
    {
        "field": "duracao_km",
        "headerName": "DURAÇÃO KM",
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        "type": ["numericColumn"],
    }
] 
