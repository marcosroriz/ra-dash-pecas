tbl_vida_util_pecas = [
    {
        "field": "nome_pecas",
        "headerName": "NOME DA PEÇA",
        "pinned": "left",
        "minWidth": 400,
        "type": ["numericColumn"],
        "cellClass" : "text-center",
        "headerClass": "text-center"
    },
    {
        "field": "id_veiculo",
        "headerName": "VEICULO",
        "pinned": "left",
        "minWidth": 100,
        "type": ["numericColumn"],
        "cellClass" : "text-center",
        "headerClass": "text-center"
    },
    {
    "field": "numero_troca",
        "headerName": "N° TROCA",
        "pinned": "left",
        "minWidth": 25,
        "type": ["numericColumn"],
        "cellClass" : "text-center",
        "headerClass": "text-center"
    },
    {"field": "data_primeira_troca",  
     "headerName": "DATA PRIMEIRA TROCA",
     "minWidth": 150,
     "cellClass" : "text-center",
     "headerClass": "text-center"
     },
    {
     "field": "data_segunda_troca", 
     "headerName": "DATA SEGUNDA TROCA", 
     "minWidth": 150,
     "cellClass" : "text-center",
     "headerClass": "text-center"
    },
    {
        "field": "dias_efetivo_da_peca",
        "headerName": "DURAÇÃO DE DIAS EFETIVOS",
        "filter": "agNumberColumnFilter",
        "maxWidth": 230,
        "type": ["numericColumn"],
        "cellClass" : "text-center",
        "headerClass": "text-center"
    },
    {
        "field": "odometro_primeira_troca",
        "headerName": "HODOMETRO DA PRIMEIRA TROCA",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "maxWidth": 250,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
        "cellClass" : "text-center",
        "headerClass": "text-center"
    },
    {
        "field": "odometro_segunda_troca",
        "headerName": "HODOMETRO DA SEGUNDA TROCA",
        "filter": "agNumberColumnFilter",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "maxWidth": 250,
        "type": ["numericColumn"],
        "cellClass" : "text-center",
        "headerClass": "text-center"
    },
    {
        "field": "hodometro_atual_gps",
        "headerName": "HODOMETRO ATUAL",
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        "type": ["numericColumn"],
        "cellClass" : "text-center",
        "headerClass": "text-center"
    },
    {
        "field": "km_efetivo_da_peca",
        "headerName": "DURAÇÃO KM EFETIVO",
        "filter": "agNumberColumnFilter",
        "maxWidth": 200,
        "type": ["numericColumn"], 
        "cellClass" : "text-center",
        "headerClass": "text-center"
    },
    {
        "field": "quantidade_troca_1",
        "headerName": "QTD TROCA 1",
        "filter": "agNumberColumnFilter",
        "maxWidth": 150,
        "type": ["numericColumn"], 
        "cellClass" : "text-center",
        "headerClass": "text-center"
    },
    {
        "field": "quantidade_troca_2",
        "headerName": "QTD TROCA 2",
        "filter": "agNumberColumnFilter",
        "maxWidth": 150,
        "type": ["numericColumn"], 
        "cellClass" : "text-center",
        "headerClass": "text-center"
    }
] 
