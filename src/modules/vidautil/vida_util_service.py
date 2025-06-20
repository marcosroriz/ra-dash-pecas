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
            WITH trocas as (
                    SELECT 
                        id_veiculo,
                        nome_pecas,
                        data_peca as data_primeira_troca,
                        data_ultimo_hodometro as data_odometro_primeira_troca,
                        ultimo_hodometro as odometro_primeira_troca,
                        codigo_peca,
                        grupo_peca,
                        sub_grupo_peca,
                        quantidade_peca as quantidade_troca_1,
                        valor_peca,
                        LEAD(quantidade_peca) OVER (
                            PARTITION BY id_veiculo, nome_pecas
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) AS quantidade_troca_2,
                        LEAD(ultimo_hodometro) OVER (
                            PARTITION BY id_veiculo, codigo_peca
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) AS odometro_segunda_troca,
                        LEAD(TO_DATE(data_peca, 'YYYY-MM-DD')) OVER (
                            PARTITION BY id_veiculo, codigo_peca
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) AS data_segunda_troca,
                    LEAD(TO_DATE(data_ultimo_hodometro, 'YYYY-MM-DD')) OVER (
                            PARTITION BY id_veiculo, codigo_peca
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) AS data_odometro_segunda_troca,
                        LEAD(ultimo_hodometro) OVER (
                            PARTITION BY id_veiculo, codigo_peca
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) - ultimo_hodometro AS duracao_km_entre_trocas,
                        LEAD(TO_DATE(data_peca, 'YYYY-MM-DD')) OVER (
                            PARTITION BY id_veiculo, codigo_peca
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) - TO_DATE(data_peca, 'YYYY-MM-DD') AS duracao_dias_entre_trocas
                FROM
                    mat_view_os_pecas_hodometro_v3 as vph
            where 
                 grupo_peca NOT IN ('CONSUMO PARA FROTAS','MATERIAL DE CONSUMO', 'Pneumáticos')
                AND sub_grupo_peca NOT IN ('Parafusos', 'Tintas')
            )
            SELECT 
                trocas.*,
                ROW_NUMBER() OVER (
                    PARTITION BY id_veiculo, nome_pecas
                    ORDER BY data_primeira_troca
                ) AS numero_troca,
                va."Model"
            FROM trocas
            LEFT JOIN veiculos_api va
                ON "Description" = id_veiculo
            ORDER BY
                nome_pecas, id_veiculo, TO_DATE(data_primeira_troca, 'YYYY-MM-DD')
            ---
            --
            --
            ) as DF
            WHERE    DF.duracao_km_entre_trocas IS NOT NULL
                    AND DF.valor_peca > 0
                    AND DF.data_primeira_troca BETWEEN '{data_inicio}' AND '{data_fim}'
                    {subquery_modelo_str}

            group by    
                nome_pecas
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
            WITH ultimo_hodometro_gps AS (
                SELECT
                    va."AssetId",
                    mvd."maior_km_dia",
                    mvd."year_month_day"
                FROM veiculos_api va
                LEFT JOIN LATERAL (
                    SELECT 
                        mvod."year_month_day",
                        mvod."maior_km_dia"
                    FROM mat_view_odometro_diario mvod
                    WHERE mvod."AssetId" = va."AssetId"
                    ORDER BY mvod."year_month_day" DESC
                    LIMIT 1
                ) mvd ON TRUE
            ),
            trocas AS (
                    SELECT 
                        id_veiculo,
                        nome_pecas,
                        data_peca as data_primeira_troca,
                        data_ultimo_hodometro as data_odometro_primeira_troca,
                        ultimo_hodometro as odometro_primeira_troca,
                        codigo_peca,
                        grupo_peca,
                        sub_grupo_peca,
                        quantidade_peca as quantidade_troca_1,
                        valor_peca,
                        LEAD(quantidade_peca) OVER (
                            PARTITION BY id_veiculo, nome_pecas
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) AS quantidade_troca_2,
                        LEAD(ultimo_hodometro) OVER (
                            PARTITION BY id_veiculo, codigo_peca
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) AS odometro_segunda_troca,
                        LEAD(TO_DATE(data_peca, 'YYYY-MM-DD')) OVER (
                            PARTITION BY id_veiculo, codigo_peca
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) AS data_segunda_troca,
                    LEAD(TO_DATE(data_ultimo_hodometro, 'YYYY-MM-DD')) OVER (
                            PARTITION BY id_veiculo, codigo_peca
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) AS data_odometro_segunda_troca,
                        LEAD(ultimo_hodometro) OVER (
                            PARTITION BY id_veiculo, codigo_peca
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) - ultimo_hodometro AS duracao_km_entre_trocas,
                        LEAD(TO_DATE(data_peca, 'YYYY-MM-DD')) OVER (
                            PARTITION BY id_veiculo, codigo_peca
                            ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                        ) - TO_DATE(data_peca, 'YYYY-MM-DD') AS duracao_dias_entre_trocas
                    FROM
                        mat_view_os_pecas_hodometro_v3 as vph
            ),
            trocas_detalhadas AS (
                SELECT 
                    trocas.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY id_veiculo, codigo_peca
                        ORDER BY data_primeira_troca
                    ) AS numero_troca,
                    CASE 
                        WHEN duracao_km_entre_trocas is NOT NULL 
                        THEN 'TEVE PAR'
                        ELSE 'NÃO TEVE PAR'
                    END AS flag_troca,
                    va."Model",
                    va."AssetId",
                    uhg."maior_km_dia" AS hodometro_atual_gps,
                    uhg."year_month_day" AS data_hodometro_gps,
                    ROUND(
                        CASE
                            WHEN trocas.duracao_km_entre_trocas IS NOT NULL THEN trocas.duracao_km_entre_trocas
                            WHEN uhg."maior_km_dia" >= trocas.odometro_primeira_troca THEN uhg."maior_km_dia" - trocas.odometro_primeira_troca
                            WHEN duracao_km_entre_trocas < 0 THEN (1000000 - trocas.odometro_primeira_troca) + trocas.odometro_segunda_troca
                            ELSE (1000000 - trocas.odometro_primeira_troca) + uhg."maior_km_dia"
                        END::numeric, 
                    2
                    ) AS km_efetivo_da_peca,
                    CASE
                        WHEN trocas.duracao_dias_entre_trocas IS NOT NULL THEN trocas.duracao_dias_entre_trocas
                        ELSE (CURRENT_DATE - trocas.data_primeira_troca::date)
                    END AS dias_efetivo_da_peca
                FROM trocas
                LEFT JOIN veiculos_api va
                    ON va."Description" = trocas.id_veiculo
                LEFT JOIN ultimo_hodometro_gps uhg 
                    ON va."AssetId" = uhg."AssetId"
                WHERE
                    duracao_km_entre_trocas IS NOT NULL
                    AND valor_peca > 0
                    --AND data_os BETWEEN '20250101' AND '20250501'
            )
            SELECT 
                *
                FROM trocas_detalhadas
            WHERE 
                km_efetivo_da_peca < 123000
                AND grupo_peca NOT IN ('CONSUMO PARA FROTAS','MATERIAL DE CONSUMO', 'Pneumáticos')
                AND sub_grupo_peca NOT IN ('Parafusos', 'Tintas')
                AND data_primeira_troca BETWEEN '{data_inicio}' AND '{data_fim}'
                    {subquery_modelo_str}
                    {subquery_peças_str}
            ORDER BY
                nome_pecas, id_veiculo, TO_DATE(data_primeira_troca, 'YYYY-MM-DD')
            """

            
            # Executa a consulta e retorna os dados como DataFrame
            df = pd.read_sql(query, self.db_engine)
            return df

        except ValueError as e:
            # Erro ao converter datas
            logging.error(f"Erro ao converter datas: get_os - {e}")
            return pd.DataFrame()

        except Exception as e:
            # Erro genérico durante execução da query
            logging.error(f"Erro ao retornar os dados: get_os - {e}")
            return pd.DataFrame()