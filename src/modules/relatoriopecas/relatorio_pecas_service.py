from typing import List
import pandas as pd
import logging

# Imports auxiliares
from modules.sql_utils import *

class RelatorioPecasService:
    def __init__(self, db_engine: any):
        self.db_engine = db_engine

    def get_pecas_input(self, datas: List[str], lista_modelos: List[str]) -> pd.DataFrame:
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
                    data_peca,
                    ultimo_hodometro,
                    grupo_peca,
                    sub_grupo_peca,
                    quantidade_peca as quantidade_troca_1,
                    LEAD(ultimo_hodometro) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                    ) AS km_proxima_troca,
                    LEAD(quantidade_peca) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                    ) AS quantidade_troca_2,
                    LEAD(ultimo_hodometro) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                    ) - ultimo_hodometro AS duracao_km,
                    LEAD(TO_DATE(data_peca, 'YYYY-MM-DD')) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                    ) AS data_proxima_troca,
                    -- Subtração convertida corretamente
                    LEAD(TO_DATE(data_peca, 'YYYY-MM-DD')) OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY TO_DATE(data_peca, 'YYYY-MM-DD')
                    ) - TO_DATE(data_peca, 'YYYY-MM-DD') AS duracao_dias
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
                    ORDER BY data_peca
                ) AS numero_troca,
                va."Model"
            FROM trocas
            LEFT JOIN veiculos_api va
                ON "Description" = id_veiculo
            ORDER BY
                nome_pecas, id_veiculo, TO_DATE(data_peca, 'YYYY-MM-DD')
            ---
            --
            --
            ) as DF
            WHERE DF.data_peca BETWEEN '{data_inicio}' AND '{data_fim}'
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
        

    def get_pecas(self, datas: List[str], lista_modelos: List[str]) -> pd.DataFrame:

        # Validação simples: verifica se o parâmetro 'datas' contém exatamente duas datas
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")

        try:
            # Converte as datas para o formato desejado (dd/mm/yyyy)
            data_inicio = pd.to_datetime(datas[0]).strftime("%Y-%m-%d")
            data_fim = pd.to_datetime(datas[1]).strftime("%Y-%m-%d")
            
            # Monta a query final com os filtros aplicados
            query = f"""
            WITH ultimo_hodometro_gps AS (
                SELECT
                    va."AssetId",
                    mvd."maior_km_dia",
                    mvd."year_month_day",
                    va."Description" as codigo_veiculo
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
            trocas_detalhadas AS (
                SELECT 
                    trocas.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY id_veiculo, nome_pecas
                        ORDER BY data_os
                    ) AS numero_troca,
                    va."Model",
                    va."AssetId",
                    uhg."maior_km_dia" AS hodometro_atual_gps,
                    uhg."year_month_day" AS data_hodometro_gps
                FROM (
                    SELECT 
                        id_veiculo,
                        nome_pecas,
                        data_os,
                        ultimo_hodometro,
                        valor_peca,
                        codigo_peca,
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
                        LEAD(TO_DATE(data_os, 'YYYY-MM-DD')) OVER (
                            PARTITION BY id_veiculo, nome_pecas
                            ORDER BY TO_DATE(data_os, 'YYYY-MM-DD')
                        ) - TO_DATE(data_os, 'YYYY-MM-DD') AS duracao_dias
                    FROM
                        mat_view_os_pecas_hodometro_v2 as vph
                    where grupo_peca not IN ('CONSUMO PARA FROTAS','MATERIAL DE CONSUMO', 'Pneumáticos')
                        and sub_grupo_peca not in ('Parafusos', 'Tintas')
                ) AS trocas
                LEFT JOIN veiculos_api va
                    ON va."Description" = trocas.id_veiculo
                LEFT JOIN ultimo_hodometro_gps uhg 
                    ON va."AssetId" = uhg."AssetId"
                WHERE
                    duracao_km IS NOT null
                    and (duracao_km::numeric) > 0.1
                    and (duracao_km::numeric) <> 0.0
                    --AND data_os BETWEEN '20250101' AND '20250501'
            ),
            media_pecas AS (
                SELECT 
                    nome_pecas,
                    codigo_peca,
                    ROUND(AVG(duracao_km)) AS media_km_entre_trocas,
                    ROUND(AVG(duracao_dias)) AS media_dias_troca,
                    ROUND(AVG(valor_peca)) AS media_valor_peca_1_troca
                FROM trocas_detalhadas
                GROUP BY nome_pecas, codigo_peca
            ),
            peças AS (
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
                        codigo_peca,
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
                        LEAD(TO_DATE(data_os, 'YYYY-MM-DD')) OVER (
                            PARTITION BY id_veiculo, nome_pecas
                            ORDER BY TO_DATE(data_os, 'YYYY-MM-DD')
                        ) - TO_DATE(data_os, 'YYYY-MM-DD') AS duracao_dias
                    FROM mat_view_os_pecas_hodometro_v2 as vph
                    WHERE grupo_peca NOT IN ('CONSUMO PARA FROTAS','MATERIAL DE CONSUMO', 'Pneumáticos')
                    AND sub_grupo_peca NOT IN ('Parafusos', 'Tintas')
                ) AS trocas
                LEFT JOIN veiculos_api va ON "Description" = id_veiculo
                WHERE duracao_km IS NOT NULL
                --AND data_os BETWEEN '20240501' AND '20250601'
            ),
            estimativa as ( SELECT 
                p.*,
                mp.*,
                ROUND(mp.media_km_entre_trocas + p.km_proxima_troca) AS estimativa_odometro_proxima_troca,
                ROUND(uh.maior_km_dia) as odometro_atual_frota,
                ROUND(mp.media_km_entre_trocas + p.km_proxima_troca - uh.maior_km_dia) as diferenca_entre_hodometro_estimativa_e_atual,
                CASE 
                    WHEN uh.maior_km_dia > (mp.media_km_entre_trocas + p.km_proxima_troca)
                    THEN TRUE
                    ELSE FALSE
                END AS ultrapassou_estimativa,
            CASE 
                    WHEN uh.maior_km_dia > (mp.media_km_entre_trocas + p.km_proxima_troca) THEN 'Vermelho'
                    WHEN uh.maior_km_dia > (p.km_proxima_troca + mp.media_km_entre_trocas * 0.9) THEN 'Laranja'
                    WHEN uh.maior_km_dia > (p.km_proxima_troca + mp.media_km_entre_trocas * 0.65) THEN 'Amarelo'
                    ELSE 'Verde'
                END AS situacao_peca,
                ROW_NUMBER() OVER (
                        PARTITION BY p.id_veiculo, p.nome_pecas
                        ORDER BY p.numero_troca DESC
                    ) AS flag_ultima_troca
            FROM peças p
            LEFT JOIN media_pecas mp
                ON p.codigo_peca = mp.codigo_peca
            AND p.nome_pecas = mp.nome_pecas
            LEFT JOIN ultimo_hodometro_gps uh
                on uh.codigo_veiculo = p.id_veiculo
            ORDER BY
                p.nome_pecas,
                p.id_veiculo,
                TO_DATE(p.data_os, 'YYYY-MM-DD')
            )
            select *
            from estimativa
            where 
            flag_ultima_troca = '1'
                AND data_os BETWEEN '{data_inicio}' AND '{data_fim}'
            ---
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
            