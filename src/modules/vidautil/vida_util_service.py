from typing import List
import pandas as pd
import logging

# Imports auxiliares
from modules.sql_utils import *

class VidaUtilService:
    """
    Serviço para manipulação de dados relacionados à Vida Útil de Ordens de Serviço (OS).
    """
    def __init__(self, db_engine: any):
        """
        Inicializa a instância do serviço com uma conexão ao banco de dados.

        Args:
            db_engine (any): Objeto de conexão ou engine SQLAlchemy para acessar o banco de dados.
        """
        self.db_engine = db_engine

    def get_pecas(
        self,
        datas: List[str],
        lista_modelos: List[str]
    ) -> pd.DataFrame:
        """
        Obtém as peças trocadas em ordens de serviço dentro de um intervalo de datas e filtradas por modelos.
        Args:
            datas (List[str]): Lista contendo duas strings representando as datas de início e fim no formato 'dd/mm/yyyy'.
            lista_modelos (List[str]): Lista de modelos para filtrar as ordens de serviço.
            """

        # Validação simples: verifica se o parâmetro 'datas' contém exatamente duas datas
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")

        try:
            # Converte as datas para o formato desejado (dd/mm/yyyy)
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")
            
            lista_secoes = "TODAS"
            lista_oficinas = "TODAS"
            # Gera subqueries SQL a partir das listas de filtros
            subquery_secoes_str = subquery_secoes(lista_secoes)
            subquery_modelo_str = subquery_modelos(lista_modelos)
            subquery_ofcina_str = subquery_oficinas(lista_oficinas)

            # Monta a query final com os filtros aplicados
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

            # Executa a consulta e retorna os dados como DataFrame
            return pd.read_sql(query, self.db_engine)

        except ValueError as e:
            # Erro ao converter datas
            logging.error(f"Erro ao converter datas: get_os - {e}")
            return pd.DataFrame()

        except Exception as e:
            # Erro genérico durante execução da query
            logging.error(f"Erro ao retornar os dados: get_os - {e}")
            return pd.DataFrame()
