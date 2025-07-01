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
            regexp_replace(va."Description", '\s*-\s*.*$', '') as codigo_veiculo
        FROM veiculos_api va
        LEFT JOIN LATERAL (
            SELECT 
                mvod."year_month_day",
                mvod."maior_km_dia"
            FROM mat_view_odometro_diario mvod
            WHERE mvod."AssetId" = va."AssetId"
            ORDER BY mvod."year_month_day" DESC
            LIMIT 1 ) mvd ON TRUE
        ),
        km_diario as (
            SELECT
                t."AssetId",
                t."year_month_day" AS data_atual,
                t."maior_km_dia",
                LAG(t."maior_km_dia") OVER (PARTITION BY t."AssetId" ORDER BY t."year_month_day") AS odometro_dia_anterior,
                t."maior_km_dia" - LAG(t."maior_km_dia") OVER (PARTITION BY t."AssetId" ORDER BY t."year_month_day") AS km_rodados
            FROM
                mat_view_odometro_diario t
            WHERE
                t."year_month_day"::Date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY
                t."AssetId", t."year_month_day"
        ),
        km_diario_iqr_limites AS (
            SELECT
                PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY km_rodados) AS q1,
                PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY km_rodados) AS q3
            FROM
                km_diario
            WHERE
                km_rodados IS NOT NULL AND km_rodados > 0
        ),
        km_diario_filtrado AS (
            SELECT
                k.*
            FROM
                km_diario k, km_diario_iqr_limites i
            WHERE
                k.km_rodados IS NOT NULL
                AND k.km_rodados > 0
                AND k.km_rodados >= (i.q1 - 1.5 * (i.q3 - i.q1))
                AND k.km_rodados <= (i.q3 + 1.5 * (i.q3 - i.q1))
        ),
        media_km_diario as (
        select
            "AssetId",
            ROUND(avg(km_rodados)) as media_km_diario
        from 
            km_diario_filtrado
        where 
                km_rodados is not null 
            and km_rodados > 0
        group by "AssetId"
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
                    status_veiculo,
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
                    valor_peca > 0 -- NÃO PEGAR as PEÇAS COM VALOR NEGATIVO
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
                    WHEN trocas.duracao_km_entre_trocas < 0 THEN (1000000 - trocas.odometro_primeira_troca) + trocas.odometro_segunda_troca
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
        --WHERE
            --duracao_km_entre_trocas IS NOT NULL
                --AND data_os BETWEEN '20250101' AND '20250501'
        ),
        media_pecas AS (
                    SELECT 
                        nome_pecas,
                        codigo_peca,
                        ROUND(AVG(duracao_km_entre_trocas)) AS media_km_entre_trocas,
                        ROUND(AVG(duracao_dias_entre_trocas)) AS media_dias_troca,
                        ROUND(AVG(valor_peca)) AS media_valor_peca_troca,
                        Count(*) as qtd_amostras_media
                    FROM trocas_detalhadas
                    where   valor_peca > 0 
                        and duracao_km_entre_trocas > 0 
                        and duracao_km_entre_trocas IS NOT null -- PEGAR SOMENTE as PEÇAS QUE NÃO FORAM DEVOLVIDAS AO ESTOQUE E POSITIVAS
                    GROUP BY nome_pecas, codigo_peca
                ),
        peças AS (
                SELECT * 
                from trocas_detalhadas
                WHERE 
                        grupo_peca NOT IN ('CONSUMO PARA FROTAS','MATERIAL DE CONSUMO', 'Pneumáticos')
                        AND sub_grupo_peca NOT IN ('Parafusos', 'Tintas')
                    ),
        estimativa as ( 
                    SELECT 
                        p."AssetId",
                        p.id_veiculo,
                        p."Model" as modelo_veiculo,
                        p.nome_pecas as nome_peça,
                        mp.media_km_entre_trocas,
                        mp.media_valor_peca_troca,
                        mp.qtd_amostras_media,
                        p.data_primeira_troca,
                        ROUND(p.odometro_primeira_troca) as odometro_troca,
                        ROUND(p.hodometro_atual_gps) as hodometro_atual_gps,
                        ROUND(mp.media_km_entre_trocas + p.odometro_primeira_troca) AS estimativa_odometro_proxima_troca,
                        ROUND(mp.media_km_entre_trocas + p.odometro_primeira_troca - p.hodometro_atual_gps) as diferenca_entre_hodometro_estimativa_e_atual,
                        ROUND(p.hodometro_atual_gps - p.odometro_primeira_troca) as total_km_peca,
                        CASE 
                            WHEN p.hodometro_atual_gps > (mp.media_km_entre_trocas + p.odometro_primeira_troca)
                            THEN TRUE
                            ELSE FALSE
                        END AS ultrapassou_estimativa,
                    CASE 
                            WHEN p.hodometro_atual_gps > (mp.media_km_entre_trocas + p.odometro_primeira_troca) THEN 'Vermelho'
                            WHEN p.hodometro_atual_gps > (p.odometro_primeira_troca + mp.media_km_entre_trocas * 0.9) THEN 'Laranja'
                            WHEN p.hodometro_atual_gps > (p.odometro_primeira_troca + mp.media_km_entre_trocas * 0.65) THEN 'Amarelo'
                            ELSE 'Verde'
                        END AS situacao_peca,
                        ROW_NUMBER() OVER (
                                PARTITION BY p.id_veiculo, p.nome_pecas
                                ORDER BY p.numero_troca DESC
                            ) AS flag_ultima_troca,
                        COALESCE(mkd.media_km_diario, 150) AS media_km_diario_veiculo -- SE NÃO ACHAR O VALOR, COLOQUE 150 KM POR DIA
                    FROM peças p
                    LEFT JOIN media_pecas mp
                        ON p.codigo_peca = mp.codigo_peca
                        AND p.nome_pecas = mp.nome_pecas
                    left join media_km_diario mkd
                        ON p."AssetId" = mkd."AssetId"
                where valor_peca > 0 -- NÃO PEGAR PEÇAS QUE FORAM DEVOLVIDAS AO ESTOQUE
                        --and duracao_km_entre_trocas > 0
                        and status_veiculo = 'ATIVO' -- PEGAR SOMENTE VEÍCULOS ATIVOS
                    ),
        calculo_previsao_dia as (
                    select *,
                    CASE 
                        WHEN 0 < diferenca_entre_hodometro_estimativa_e_atual THEN round(diferenca_entre_hodometro_estimativa_e_atual / media_km_diario_veiculo)
                        ELSE round(diferenca_entre_hodometro_estimativa_e_atual / media_km_diario_veiculo)
                    END AS calculo_dias,
                    CASE 
                    WHEN 0 < diferenca_entre_hodometro_estimativa_e_atual 
                        THEN CURRENT_DATE + round(diferenca_entre_hodometro_estimativa_e_atual / media_km_diario_veiculo)::int
                    ELSE CURRENT_DATE
                    END AS data_estimada
                    from estimativa
                    --where flag_ultima_troca = '1' -- ATENÇÃO NA ULTIMA TROCA (1 = ULTIMA TROCA, 2= PNEULTIMA TROCA, ...)
        )
        select * from calculo_previsao_dia
        where 
            --flag_ultima_troca = '1'
            flag_ultima_troca = '1'
            and media_km_entre_trocas is not null  --Não linhas que não tenham média de KM
            and "AssetId" is not null; -- Não quero veiculos que não tenha odometro
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
            