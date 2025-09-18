from typing import List
import pandas as pd
import logging

# Imports auxiliares
from modules.sql_utils import *

class ServiceOS:
    """
    Classe responsável por fornecer serviços relacionados a Ordens de Serviço (OS),
    incluindo consultas ao banco de dados com base em filtros aplicados.
    """

    def __init__(self, db_engine: any):
        """
        Inicializa a instância do serviço com uma conexão ao banco de dados.

        Args:
            db_engine (any): Objeto de conexão ou engine SQLAlchemy para acessar o banco de dados.
        """
        self.db_engine = db_engine

    def get_os(
        self,
        datas: List[str],
        lista_modelos: List[str],
        lista_oficinas: List[str],
        lista_secoes: List[str],
    ) -> pd.DataFrame:
        """
        Retorna uma lista de descrições de serviços (LABEL) associados a Ordens de Serviço (OS)
        com base nos filtros fornecidos: intervalo de datas, modelos de veículos, oficinas e seções.

        Args:
            datas (List[str]): Lista com duas datas no formato string (data inicial e final).
            lista_modelos (List[str]): Lista de modelos de veículos a serem filtrados.
            lista_oficinas (List[str]): Lista de oficinas a serem filtradas.
            lista_secoes (List[str]): Lista de seções do veículo a serem filtradas.

        Returns:
            pd.DataFrame: DataFrame contendo as descrições dos serviços encontrados,
            ou um DataFrame vazio em caso de erro ou ausência de dados.
        """

        # Validação simples: verifica se o parâmetro 'datas' contém exatamente duas datas
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")

        try:
            # Converte as datas para o formato desejado (dd/mm/yyyy)
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            # Gera subqueries SQL a partir das listas de filtros
            subquery_secoes_str = subquery_secoes(lista_secoes)
            subquery_modelo_str = subquery_modelos(lista_modelos)
            subquery_ofcina_str = subquery_oficinas(lista_oficinas)

            # Monta a query final com os filtros aplicados
            query = f"""
                SELECT DISTINCT 
                    "DESCRICAO DO SERVICO" as "LABEL"
                FROM os_dados
                LEFT JOIN view_pecas_desconsiderando_combustivel ON "NUMERO DA OS" = "OS"
                WHERE "DATA"::DATE  BETWEEN DATE '{data_inicio}' AND DATE '{data_fim}'
                and "TIPO DE MANUTENCAO" = 'Corretiva'
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
        
    def get_pecas_trocadas_por_os(
        self,
        datas: List[str],
        lista_modelos: List[str],
        lista_oficinas: List[str],
        lista_secoes: List[str],
        lista_os: List[str]
    ) -> pd.DataFrame:
        # Validação simples: verifica se o parâmetro 'datas' contém exatamente duas datas
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")

        try:
            # Converte as datas para o formato desejado (dd/mm/yyyy)
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            # Gera subqueries SQL a partir das listas de filtros
            subquery_secoes_str = subquery_secoes(lista_secoes)
            subquery_modelo_str = subquery_modelos(lista_modelos)
            subquery_ofcina_str = subquery_oficinas(lista_oficinas)
            subquery_os_str = subquery_os(lista_os)

            # Monta a query final com os filtros aplicados
            query = f"""
                SELECT 
                    "PRODUTO" AS pecas,
                    SUM("QUANTIDADE") AS total_trocas
                FROM view_pecas_desconsiderando_combustivel
                LEFT JOIN 
                        os_dados ON "NUMERO DA OS" = "OS"
                WHERE 
                    "DATA"::DATE  BETWEEN DATE '{data_inicio}' AND DATE '{data_fim}'
                        and "TIPO DE MANUTENCAO" = 'Corretiva'
                    {subquery_secoes_str}
                    {subquery_modelo_str}
                    {subquery_ofcina_str}
                    {subquery_os_str}
                GROUP BY "PRODUTO"
                ORDER BY total_trocas DESC;
            """
            df = pd.read_sql(query, self.db_engine)
            df["percentual"] = (df["total_trocas"] / df["total_trocas"].sum()) * 100
            # Executa a consulta e retorna os dados como DataFrame
            return df

        except ValueError as e:
            # Erro ao converter datas
            logging.error(f"Erro ao converter datas: get_os - {e}")
            return pd.DataFrame()

        except Exception as e:
            # Erro genérico durante execução da query
            logging.error(f"Erro ao retornar os dados: get_os - {e}")
            return pd.DataFrame()