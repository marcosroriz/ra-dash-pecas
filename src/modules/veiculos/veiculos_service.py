from typing import List
import pandas as pd
import logging

# Imports auxiliares
from modules.sql_utils import *

class VeiculosService:

    def __init__(self, db_engine: any):
        self.db_engine = db_engine

    def get_veiculos(
        self,
        datas: List[str],
        lista_modelos: List[str]
    ):
        
         # Validação simples: verifica se o parâmetro 'datas' contém exatamente duas datas
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")

        try:
            # Converte as datas para o formato desejado (dd/mm/yyyy)
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            # Gera subqueries SQL a partir das listas de filtros
            subquery_modelo_str = subquery_modelos_pecas(lista_modelos)

            # Monta a query final com os filtros aplicados
            query = f"""
                SELECT DISTINCT 
                    "EQUIPAMENTO" as "LABEL"
                FROM pecas_gerais
                WHERE "DATA" BETWEEN '{data_inicio}' AND '{data_fim}' 
                {subquery_modelo_str}
                ORDER BY "EQUIPAMENTO";
            """

            # Executa a consulta e retorna os dados como DataFrame
            return pd.read_sql(query, self.db_engine)

        except ValueError as e:
            # Erro ao converter datas
            logging.error(f"Erro ao converter datas: get_veiculos - {e}")
            return pd.DataFrame()

        except Exception as e:
            # Erro genérico durante execução da query
            logging.error(f"Erro ao retornar os dados: get_veiculos - {e}")
            return pd.DataFrame()
        
    
    def get_table_pecas(
        self,
        datas: List[str],
        veiculo: List[str]
    ):
        
         # Validação simples: verifica se o parâmetro 'datas' contém exatamente duas datas
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")

        try:
            # Converte as datas para o formato desejado (dd/mm/yyyy)
            data_inicio = pd.to_datetime(datas[0]).strftime("%Y-%m-%d")
            data_fim = pd.to_datetime(datas[1]).strftime("%Y-%m-%d")

            # Monta a query final com os filtros aplicados
            query = f"""
                select 
                    data_os,
                    nome_pecas,
                    ultimo_hodometro
                from view_os_pecas_hodometro
                WHERE data_os BETWEEN '{data_inicio}' AND '{data_fim}' AND id_veiculo = '{veiculo[0]}'
                ORDER BY nome_pecas;
            """
            print(query)
            df = pd.read_sql(query, self.db_engine)
            # Ordena por data_os
            df = df.sort_values(["nome_pecas", "data_os"])

            # Para cada peça, pega os dois últimos registros
            df_ultimos = df.groupby("nome_pecas").tail(2)

            # Calcula a diferença de hodômetro (último - penúltimo)
            def calcula_km(df_peca):
                if len(df_peca) < 2:
                    return pd.Series({
                        "km_desde_penultima_troca": None,
                        "data_ultima_troca": df_peca.iloc[-1]["data_os"]
                    })
                else:
                    km = df_peca.iloc[-1]["ultimo_hodometro"] - df_peca.iloc[-2]["ultimo_hodometro"]
                    return pd.Series({
                        "km_desde_penultima_troca": round(km,2), 
                        "data_ultima_troca": df_peca.iloc[-1]["data_os"]
                    })

            resultado = (
                df_ultimos.groupby("nome_pecas")
                        .apply(calcula_km)
                        .reset_index()
            )
            resultado['data_ultima_troca'] = pd.to_datetime(resultado['data_ultima_troca'])
            resultado['data_ultima_troca'] = resultado['data_ultima_troca'].apply(lambda x: x.strftime("%d/%m/%Y"))
            resultado = resultado.dropna(subset=["km_desde_penultima_troca"])
            
            return resultado

        except ValueError as e:
            # Erro ao converter datas
            logging.error(f"Erro ao converter datas: get_veiculos - {e}")
            return pd.DataFrame(columns=["nome_pecas", "km_desde_penultima_troca", "data_ultima_troca"])


        except Exception as e:
            # Erro genérico durante execução da query
            logging.error(f"Erro ao retornar os dados: get_veiculos - {e}")
            return pd.DataFrame(columns=["nome_pecas", "km_desde_penultima_troca", "data_ultima_troca"])
