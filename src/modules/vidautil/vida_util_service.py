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

    def get_pecas_input(self, datas: List[str], lista_modelos: List[str]) -> pd.DataFrame:
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
            data_inicio = pd.to_datetime(datas[0]).strftime("%Y-%m-%d")
            data_fim = pd.to_datetime(datas[1]).strftime("%Y-%m-%d")


            
            # Gera subqueries SQL a partir das listas de filtros
            subquery_modelo_str = subquery_modelos_peças(lista_modelos, prefix="DF.")

            # Monta a query final com os filtros aplicados
            query = f"""
            select nome_pecas, 
                Count(nome_pecas) as quantidade
            from (
            --
            --
            --
            --QUERY ORIGINAL
            SELECT 
                trocas.*,
                ROW_NUMBER() OVER (
                    PARTITION BY id_veiculo, nome_pecas
                    ORDER BY data_os
                ) AS numero_troca,
                va."Model"
            FROM (
                SELECT 
                    id_veiculo,
                    nome_pecas,
                    data_os,
                    ultimo_hodometro,
                    grupo_peca,
                    sub_grupo_peca,
                    LEAD(ultimo_hodometro) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_os, 'YYYY-MM-DD')
                    ) AS km_proxima_troca,
                    LEAD(ultimo_hodometro) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_os, 'YYYY-MM-DD')
                    ) - ultimo_hodometro AS duracao_km,
                    LEAD(TO_DATE(data_os, 'YYYY-MM-DD')) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_os, 'YYYY-MM-DD')
                    ) AS data_proxima_troca,
                    -- Subtração convertida corretamente
                    LEAD(TO_DATE(data_os, 'YYYY-MM-DD')) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_os, 'YYYY-MM-DD')
                    ) - TO_DATE(data_os, 'YYYY-MM-DD') AS duracao_dias
                FROM
                    mat_view_os_pecas_hodometro_v2 as vph
            ) AS trocas
            LEFT JOIN veiculos_api va
                ON "Description" = id_veiculo
            WHERE 
                duracao_km IS NOT NULL
                AND grupo_peca NOT IN ('CONSUMO PARA FROTAS','MATERIAL DE CONSUMO', 'Pneumáticos')
                AND sub_grupo_peca NOT IN ('Parafusos', 'Tintas')
            ORDER BY
                nome_pecas, id_veiculo, TO_DATE(data_os, 'YYYY-MM-DD')
            ---
            --
            --
            ) as DF
            WHERE DF.data_os BETWEEN '{data_inicio}' AND '{data_fim}'
                    {subquery_modelo_str}
            group by    
                nome_pecas
            """
            print(query)
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
        

    def get_pecas(self, datas: List[str], lista_modelos: List[str], lista_peças: List[str]) -> pd.DataFrame:
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
            data_inicio = pd.to_datetime(datas[0]).strftime("%Y-%m-%d")
            data_fim = pd.to_datetime(datas[1]).strftime("%Y-%m-%d")

            
            # Gera subqueries SQL a partir das listas de filtros
            subquery_modelo_str = subquery_modelos_peças(lista_modelos)
            subquery_peças_str = subquery_pecas2(lista_peças)
            # Monta a query final com os filtros aplicados
            query = f"""
            --QUERY ORIGINAL
            SELECT 
                trocas.*,
                ROW_NUMBER() OVER (
                    PARTITION BY id_veiculo, nome_pecas
                    ORDER BY data_os
                ) AS numero_troca,
                va."Model"
            FROM (
                SELECT 
                    id_veiculo,
                    nome_pecas,
                    data_os,
                    ultimo_hodometro,
                    grupo_peca,
                    sub_grupo_peca,
                    quantidade_peca as quantidade_troca_1,
                    LEAD(ultimo_hodometro) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_os, 'YYYY-MM-DD')
                    ) AS km_proxima_troca,
                    LEAD(quantidade_peca) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_os, 'YYYY-MM-DD')
                    ) AS quantidade_troca_2,
                    LEAD(ultimo_hodometro) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_os, 'YYYY-MM-DD')
                    ) - ultimo_hodometro AS duracao_km,
                    LEAD(TO_DATE(data_os, 'YYYY-MM-DD')) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_os, 'YYYY-MM-DD')
                    ) AS data_proxima_troca,
                    -- Subtração convertida corretamente
                    LEAD(TO_DATE(data_os, 'YYYY-MM-DD')) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_os, 'YYYY-MM-DD')
                    ) - TO_DATE(data_os, 'YYYY-MM-DD') AS duracao_dias
                FROM
                    mat_view_os_pecas_hodometro_v2 as vph
            where 
                 grupo_peca NOT IN ('CONSUMO PARA FROTAS','MATERIAL DE CONSUMO', 'Pneumáticos')
                AND sub_grupo_peca NOT IN ('Parafusos', 'Tintas')
            ) AS trocas
            LEFT JOIN veiculos_api va
                ON "Description" = id_veiculo
            WHERE   duracao_km IS NOT NULL
                AND data_os BETWEEN '{data_inicio}' AND '{data_fim}'
                    {subquery_modelo_str}
                    {subquery_peças_str}
            ORDER BY
                nome_pecas, id_veiculo, TO_DATE(data_os, 'YYYY-MM-DD')
            ---
            """

            print(query)
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