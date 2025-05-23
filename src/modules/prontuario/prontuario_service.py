from typing import List
import pandas as pd
import logging

# Imports auxiliares
from modules.sql_utils import *

class ProntuarioService:

    def __init__(self, db_engine: any):
        """
        Inicializa o serviço com a conexão ao banco de dados.

        Args:
            db_engine: Conexão ativa com o banco.
        """
        self.db_engine = db_engine

    def get_pecas(
        self,
        datas: List[str],
        lista_modelos: List[str],
        lista_equipamentos: List[str],
        lista_grupo: List[str]
    ) -> pd.DataFrame:
        """
        Retorna a lista de peças (produtos) disponíveis em um intervalo de datas,
        aplicando possíveis filtros por modelo, oficina e seção (ainda não aplicados nesta versão).

        Args:
            datas (List[str]): Lista contendo duas datas [data_inicial, data_final] no formato ISO (YYYY-MM-DD).
            lista_modelos (List[str]): Lista de modelos de veículos para filtrar (não utilizado nesta versão).
            lista_oficinas (List[str]): Lista de oficinas para filtrar (não utilizado nesta versão).
            lista_secoes (List[str]): Lista de seções para filtrar (não utilizado nesta versão).

        Returns:
            List[str]: Lista única de peças (produtos) encontrados no período especificado.
        """
        # Validação simples de entrada
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")

        try:
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            subquery_modelo_str = subquery_modelos_pecas(lista_modelos)
            subquery_equipamentos_str = subquery_equipamentos(lista_equipamentos)
            subquery_grupos_str = subquery_grupos_pecas(lista_grupo)
                

            query = f"""
                SELECT DISTINCT "PRODUTO" AS "LABEL"
                FROM pecas_gerais
                WHERE "DATA" BETWEEN '{data_inicio}' AND '{data_fim}'
                {subquery_modelo_str}
                {subquery_equipamentos_str}
                {subquery_grupos_str}
                ORDER BY "PRODUTO"
            """
            return pd.read_sql(query, self.db_engine)
        
        except ValueError as e:
            logging.error(f"Erro ao converter datas: get_pecas {e}")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Erro ao retornar os dados: get_pecas {e}")
            return pd.DataFrame()
    
    def get_prontuario_pecas(
        self,
        datas: List[str],
        lista_modelos: List[str],
        lista_equipamentos: List[str],
        lista_grupo: List[str],
        lista_pecas: List[str]
    ) -> pd.DataFrame:
        """
        Retorna a lista de peças (produtos) disponíveis em um intervalo de datas,
        aplicando possíveis filtros por modelo, oficina e seção (ainda não aplicados nesta versão).

        Args:
            datas (List[str]): Lista contendo duas datas [data_inicial, data_final] no formato ISO (YYYY-MM-DD).
            lista_modelos (List[str]): Lista de modelos de veículos para filtrar (não utilizado nesta versão).
            lista_oficinas (List[str]): Lista de oficinas para filtrar (não utilizado nesta versão).
            lista_secoes (List[str]): Lista de seções para filtrar (não utilizado nesta versão).

        Returns:
            List[str]: Lista única de peças (produtos) encontrados no período especificado.
        """
        # Validação simples de entrada
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")

        try:
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            subquery_modelo_str = subquery_modelos_pecas(lista_modelos)
            subquery_equipamentos_str = subquery_equipamentos(lista_equipamentos)
            subquery_grupos_str = subquery_grupos_pecas(lista_grupo)
            subquery_pecas_str = subquery_pecas(lista_pecas)
                

            query = f"""
            SELECT 
                "EQUIPAMENTO" AS id_veiculo,
                "PRODUTO" AS nome_peca,
                "MODELO" AS modelo,
                "GRUPO" AS grupo,
                SUM("QUANTIDADE") AS quantidade_total,
                SUM("VALOR") AS valor_total,
                COUNT(*) AS quantidade_trocas,
                MAX(TO_DATE("DATA", 'DD/MM/YYYY')) AS data_ultima_troca
            FROM 
                pecas_gerais
            WHERE "DATA" BETWEEN '{data_inicio}' AND '{data_fim}'
                {subquery_modelo_str}
                {subquery_equipamentos_str}
                {subquery_grupos_str}
                {subquery_pecas_str}
            GROUP BY 
                "EQUIPAMENTO", "PRODUTO", "MODELO", "GRUPO"
            ORDER BY 
                data_ultima_troca DESC;
            """
            return pd.read_sql(query, self.db_engine)
        
        except ValueError as e:
            logging.error(f"Erro ao converter datas: get_pecas {e}")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Erro ao retornar os dados: get_pecas {e}")
            return pd.DataFrame()