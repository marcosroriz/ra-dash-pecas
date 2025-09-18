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
        "minWidth": 200,
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "situacao_peca_porcentagem",
        "headerName": "VIDA ÚTIL CONSUMIDA(%)",
        "minWidth": 150,
        "headerClass": "ag-center-header",
        "valueFormatter": {
            "function": "params.value.toFixed(1) + '%'"
        },
        "cellStyle": {
            "styleConditions": [
                {
                    "condition": "params.value > 100",
                    "style": {
                        "backgroundColor": "#e74c3c",  # D - vermelho
                        "color": "white",
                        "fontWeight": "bold",
                        "textAlign": "center"
                    }
                },
                {
                    "condition": "params.value > 90 && params.value <= 100",
                    "style": {
                        "backgroundColor": "#e67e22",  # C - laranja
                        "color": "white",
                        "fontWeight": "bold",
                        "textAlign": "center"
                    }
                },
                {
                    "condition": "params.value > 65 && params.value <= 90",
                    "style": {
                        "backgroundColor": "#f1c40f",  # B - amarelo
                        "color": "black",
                        "fontWeight": "bold",
                        "textAlign": "center"
                    }
                },
                {
                    "condition": "params.value <= 65",
                    "style": {
                        "backgroundColor": "#2ecc71",  # A - verde
                        "color": "white",
                        "fontWeight": "bold",
                        "textAlign": "center"
                    }
                }
            ]
        }
    },
    {
        "field": "class_peca",
        "headerName": "CLASSIFICAÇÃO",
        "minWidth": 200,
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
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
        "headerName": "DATA DA ULTIMA TROCA",
        "filter": "agNumberColumnFilter",
        "maxWidth": 250,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "odometro_troca",
        "headerName": "HODÔMETRO DA ULTIMA TROCA",
        "filter": "agNumberColumnFilter",
        "minWidth": 250,
        "type": ["numericColumn"],
        "headerClass": "ag-center-header",
        "cellStyle": {"textAlign": "center"}
    },
    {
        "field": "hodometro_atual_gps",
        "headerName": "HODÔMETRO ATUAL DA FROTA",
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
        "headerName": "HODÔMETRO ESTIMADO DA PRÓXIMA TROCA",
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