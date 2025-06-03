tbl_relatorio_pecas = [
    {
        "field": "id_veiculo",
        "headerName": "ID DO VEÍCULO",
        "pinned": "left",
        "minWidth": 100,
        "type": ["numericColumn"],
    },
    {
        "field": "nome_pecas",
        "headerName": "NOME DA PEÇA",
        "pinned": "left",
        "minWidth": 300,
        "type": ["numericColumn"],
    },
    {
        "field": "Model",
        "headerName": "MODELO",
        "pinned": "left",
        "minWidth": 200,
        "type": ["numericColumn"],
    },
    {
        "field": "situacao_peca",  
        "headerName": "STATUS DA PEÇA",
        "minWidth": 200
    },
    {
        "field": "media_km_entre_trocas", 
        "headerName": "MÉDIA DURAÇÃO KM",
        "minWidth": 200
    },
    {
        "field": "media_dias_troca",
        "headerName": "MÉDIA DE DIAS",
        "filter": "agNumberColumnFilter",
        "minWidth": 250,
        "type": ["numericColumn"],
    },
    {
        "field": "data_proxima_troca",
        "headerName": "DATA ÚLTIMA TROCA",
        "filter": "agNumberColumnFilter",
        "maxWidth": 250,
        "type": ["numericColumn"],
    },
    {
        "field": "km_proxima_troca",
        "headerName": "HODÔMETRO DA ÚLTIMA TROCA",
        "filter": "agNumberColumnFilter",
        "minWidth": 250,
        "type": ["numericColumn"],
    },
    {
        "field": "odometro_atual_frota",
        "headerName": "HODÔMETRO ATUAL",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "minWidth": 250,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
    },
    {
        "field": "estimativa_odometro_proxima_troca",
        "headerName": "HODÔMETRO DA PRÓXIMA TROCA",
        "filter": "agNumberColumnFilter",
        "minWidth": 250,
        "type": ["numericColumn"],
    },
    {
        "field": "diferenca_entre_hodometro_estimativa_e_atual",
        "headerName": "DIFERENÇA ESTIMATIVA E ATUAL",
        "filter": "agNumberColumnFilter",
        "minWidth": 250,
        "type": ["numericColumn"],
    },
    {
        "field": "ultrapassou_estimativa",
        "headerName": "ULTRAPASSOU KM ESPERADO",
        "cellRenderer": "agCheckboxCellRenderer",  # ← renderiza como checkbox
        "minWidth": 250,
        "type": ["booleanColumn"],  # ← tipo booleano
        "editable": False,          # ← checkbox apenas visual (sem edição)
    },
] 
