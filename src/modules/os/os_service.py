
from typing import List
import pandas as pd
import logging

# Imports auxiliares
from modules.sql_utils import *


class ServiceOS:
    def __init__(self, db_engine: any):
        """
        Inicializa o serviço com a conexão ao banco de dados.

        Args:
            db_engine: Conexão ativa com o banco.
        """
        self.db_engine = db_engine

    def get_os(
            self,
            datas: List[str],
            lista_modelos: List[str],
            lista_oficinas: List[str],
            lista_secoes: List[str],
        )->pd.DataFrame:

        # Validação simples de entrada
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")
        
        try:
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            subquery_secoes_str = subquery_secoes(lista_secoes)
            subquery_modelo_str = subquery_modelos(lista_modelos)
            subquery_ofcina_str = subquery_oficinas(lista_oficinas)
                

            query = f"""
               SELECT DISTINCT 
                    "DESCRICAO DO SERVICO" as "LABEL"
                FROM os_dados 
                LEFT JOIN pecas_gerais ON "NUMERO DA OS" = "OS"
                WHERE "DATA" BETWEEN '{data_inicio}' AND '{data_fim}'    
                {subquery_secoes_str}
                {subquery_modelo_str}
                {subquery_ofcina_str}
                ORDER BY "DESCRICAO DO SERVICO";
            """
            return pd.read_sql(query, self.db_engine)
        
        except ValueError as e:
            logging.error(f"Erro ao converter datas: get_custo_mensal_pecas {e}")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Erro ao retornar os dados: get_custo_mensal_pecas {e}")
            return pd.DataFrame()