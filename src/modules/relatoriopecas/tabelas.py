tbl_relatorio_pecas = [
    {
        "field": "id_veiculo",
        "headerName": "ID DO VEÍCULO",
        "pinned": "left",
        "minWidth": 100,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "nome_peça",
        "headerName": "NOME DA PEÇA",
        "pinned": "left",
        "minWidth": 300,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "modelo_veiculo",
        "headerName": "MODELO",
        "pinned": "left",
        "minWidth": 200,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "situacao_peca_porcentagem",
        "headerName": "STATUS DA PEÇA",
        "minWidth": 150,
        "headerClass": "ag-center-header",
        "cellStyle": {
            "styleConditions": [
                {
                    "condition": "params.value && params.value.split(' -')[0].trim() === 'Vermelho'",
                    "style": {
                        "backgroundColor": "#e74c3c",
                        "color": "white",
                        "fontWeight": "bold",
                        "textAlign": "center"
                    }
                },
                {
                    "condition": "params.value && params.value.split(' -')[0].trim() === 'Verde'",
                    "style": {
                        "backgroundColor": "#2ecc71",
                        "color": "white",
                        "fontWeight": "bold",
                        "textAlign": "center"
                    }
                },
                {
                    "condition": "params.value && params.value.split(' -')[0].trim() === 'Amarelo'",
                    "style": {
                        "backgroundColor": "#f1c40f",
                        "color": "black",
                        "fontWeight": "bold",
                        "textAlign": "center"
                    }
                },
                {
                    "condition": "params.value && params.value.split(' -')[0].trim() === 'Laranja'",
                    "style": {
                        "backgroundColor": "#e67e22",
                        "color": "white",
                        "fontWeight": "bold",
                        "textAlign": "center"
                    }
                }
            ]
        }
    },
    {
        "field": "media_km_entre_trocas",
        "headerName": "MÉDIA DURAÇÃO KM",
        "minWidth": 200,
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "qtd_amostras_media",
        "headerName": "QTD AMOSTRAS MÉDIA",
        "minWidth": 200,
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "data_primeira_troca",
        "headerName": "DATA TROCA",
        "filter": "agNumberColumnFilter",
        "maxWidth": 250,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "odometro_troca",
        "headerName": "HODÔMETRO DA TROCA",
        "filter": "agNumberColumnFilter",
        "minWidth": 250,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "hodometro_atual_gps",
        "headerName": "HODÔMETRO ATUAL",
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "minWidth": 250,
        "filter": "agNumberColumnFilter",
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "estimativa_odometro_proxima_troca",
        "headerName": "HODÔMETRO DA PRÓXIMA TROCA",
        "filter": "agNumberColumnFilter",
        "minWidth": 250,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "diferenca_entre_hodometro_estimativa_e_atual",
        "headerName": "DIFERENÇA ESTIMATIVA E ATUAL",
        "filter": "agNumberColumnFilter",
        "minWidth": 250,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "total_km_peca",
        "headerName": "KM TOTAL (RODADO) DA PEÇA",
        "filter": "agNumberColumnFilter",
        "minWidth": 250,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "ultrapassou_estimativa",
        "headerName": "ULTRAPASSOU KM ESPERADO",
        "minWidth": 250,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "media_km_diario_veiculo",
        "headerName": "MÉDIA DE KM DIÁRIO DO VEÍCULO",
        "minWidth": 250,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "calculo_dias",
        "headerName": "DIAS ATÉ A TROCA",
        "minWidth": 250,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "data_estimada",
        "headerName": "DATA ESTIMADA PARA TROCA",
        "minWidth": 250,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    }
]