#!/usr/bin/env python
# coding: utf-8

"""
Módulo que centraliza os serviços para a página inicial (home).

Este serviço busca e filtra informações essenciais como produtos/peças
para exibir de forma resumida e objetiva na interface inicial da aplicação.
"""

from typing import List
import pandas as pd
import logging

# Imports auxiliares
from modules.sql_utils import *


class HomeService:
    """
    Serviço responsável por obter informações e dados para a página inicial home (Visão Geral).

    Attributes:
        db_engine: Instância do SQLAlchemy Engine para conexão com o banco de dados.
    """

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
        lista_oficinas: List[str],
        lista_secoes: List[str]
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

            subquery_secoes_str = subquery_secoes(lista_secoes)
            subquery_modelo_str = subquery_modelos(lista_modelos)
            subquery_ofcina_str = subquery_oficinas(lista_oficinas)
                

            query = f"""
                SELECT DISTINCT "PRODUTO" AS "LABEL"
                FROM pecas_gerais
                LEFT JOIN os_dados ON "NUMERO DA OS" = "OS"
                WHERE "DATA"::DATE  BETWEEN DATE '{data_inicio}' AND DATE '{data_fim}'    
                and "TIPO DE MANUTENCAO" = 'Corretiva'
                {subquery_secoes_str}
                {subquery_modelo_str}
                {subquery_ofcina_str}
                ORDER BY "PRODUTO"
            """
            return pd.read_sql(query, self.db_engine)
        
        except ValueError as e:
            logging.error(f"Erro ao converter datas: get_pecas {e}")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Erro ao retornar os dados: get_pecas {e}")
            return pd.DataFrame()
        
        
    def get_custo_mensal_pecas(
        self,
        datas: List[str],
        lista_modelos: List[str],
        lista_oficinas: List[str],
        lista_secoes: List[str],
        lista_pecas: List[str]
    )-> pd.DataFrame:
        """
        Recupera o custo mensal das peças, separando entre peças recondicionadas e não recondicionadas.

        A função executa uma consulta SQL que retorna o custo total mensal para cada tipo de peça, com base nos filtros de datas, modelos, oficinas, seções e peças fornecidos. A consulta inclui uma CTE (Common Table Expression) que filtra e agrupa os dados por mês e tipo de peça.

        Parâmetros:
        ----------
        datas : List[str]
            Lista contendo duas datas no formato 'YYYY-MM-DD', representando o intervalo de tempo para o qual os custos devem ser calculados. Exemplo: ['2025-01-01', '2025-01-31'].

        lista_modelos : List[str]
            Lista de modelos de veículos a serem filtrados na consulta.

        lista_oficinas : List[str]
            Lista de oficinas a serem filtradas na consulta.

        lista_secoes : List[str]
            Lista de seções a serem filtradas na consulta.

        lista_pecas : List[str]
            Lista de tipos de peças a serem filtrados na consulta.

        Retorna:
        -------
        pd.DataFrame
            Um DataFrame contendo as colunas 'mes', 'tipo_peca' e 'custo_total', com o custo mensal de peças recondicionadas e não recondicionadas.
            - 'mes' (str): O mês no formato 'YYYY-MM'.
            - 'tipo_peca' (str): O tipo da peça ('Recondicionada' ou 'Nao Recondicionada').
            - 'custo_total' (float): O custo total para o mês e tipo de peça.
        """
        # Validação simples de entrada
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")
        
        try:
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            subquery_secoes_str = subquery_secoes(lista_secoes)
            subquery_modelo_str = subquery_modelos(lista_modelos)
            subquery_ofcina_str = subquery_oficinas(lista_oficinas)
            subquery_pecas_str = subquery_pecas(lista_pecas)
                

            query = f"""
                WITH cte AS (
                    SELECT DISTINCT ON (pecas_gerais."KEY_HASH")
                        TO_CHAR("DATA"::DATE, 'YYYY-MM') AS mes,
                        CASE 
                            WHEN LOWER("PRODUTO") ILIKE '%%recond%%' THEN 'Recondicionada'
                            ELSE 'Nao Recondicionada'
                        END AS tipo_peca,
                        "VALOR"
                    FROM 
                        pecas_gerais
                    LEFT JOIN 
                        os_dados ON "NUMERO DA OS" = "OS"
                    WHERE "DATA"::DATE  BETWEEN DATE '{data_inicio}' AND DATE '{data_fim}'
                    and "TIPO DE MANUTENCAO" = 'Corretiva'
                    {subquery_secoes_str}
                    {subquery_modelo_str}
                    {subquery_ofcina_str}
                    {subquery_pecas_str}
                )
                SELECT
                    mes,
                    tipo_peca,
                    ROUND(SUM("VALOR"), 2) AS custo_total
                FROM
                    cte
                GROUP BY
                    mes,
                    tipo_peca
                ORDER BY
                    mes, tipo_peca;
            """
            print(query) 
            return pd.read_sql(query, self.db_engine)
        
        except ValueError as e:
            logging.error(f"Erro ao converter datas: get_custo_mensal_pecas {e}")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Erro ao retornar os dados: get_custo_mensal_pecas {e}")
            return pd.DataFrame()
        
    def get_custo_mensal_pecas_retrabalho(
        self,
        datas: List[str],
        lista_modelos: List[str],
        lista_oficinas: List[str],
        lista_secoes: List[str],
        lista_pecas: List[str]
    )-> pd.DataFrame:
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")
        
        try:
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            subquery_secoes_str = subquery_secoes(lista_secoes)
            subquery_modelo_str = subquery_modelos(lista_modelos)
            subquery_ofcina_str = subquery_oficinas(lista_oficinas)
            subquery_pecas_str = subquery_pecas(lista_pecas)

            query = f"""  
                WITH pecas AS (
                    SELECT DISTINCT ON (view_pecas_desconsiderando_combustivel."KEY_HASH")
                        "PRODUTO" AS nome_peca,
                        "QUANTIDADE",
                        "VALOR",
                        "OS",
                        "PRODUTO",
                        "DATA"
                    FROM view_pecas_desconsiderando_combustivel
                    LEFT JOIN os_dados 
                        ON "NUMERO DA OS" = "OS"
                    WHERE "DATA"::DATE  BETWEEN DATE '{data_inicio}' AND DATE '{data_fim}'
                    and "TIPO DE MANUTENCAO" = 'Corretiva'
                    {subquery_secoes_str}
                    {subquery_modelo_str}
                    {subquery_ofcina_str}
                    {subquery_pecas_str}
                ),
                -- CTE INICIAL DO RETRABALHO DA OS
                retrabalho_os AS (
                    SELECT *
                    FROM mat_view_retrabalho_30_dias_distinct
                    where "TIPO DE MANUTENCAO" = 'Corretiva'
                ),
                -- CTE INTERMEDIARIA QUE IDENTIFICA E RETIRA AS OS
                pecas_retrabalho_sem_duplicadas AS (
                    SELECT *, 
                        TO_CHAR("DATA"::DATE, 'YYYY-MM') AS mes
                    FROM (
                        SELECT 
                            pg.*,
                            r.*,
                            COUNT(*) OVER (
                                PARTITION BY pg."PRODUTO", r."NUMERO DA OS"
                            ) AS qtde_linhas
                        FROM pecas pg
                        LEFT JOIN retrabalho_os r
                            ON pg."OS" = r."NUMERO DA OS"
                    ) sub
                    WHERE qtde_linhas = 1  -- mantém apenas grupos que têm 1 linha
                ),
                -- CTE QUE REALIZA OS CÁLCULOS VALORES GASTOS COM RETRABALHO DADO A TABELA JÁ FILTRADA pecas_retrabalho_sem_duplicadas
                retrabalho_pecas AS (
                    SELECT 
                        rp.mes as mes,
                        COALESCE(SUM(CASE WHEN rp."retrabalho" THEN rp."VALOR" ELSE 0 END), 0) AS total_gasto_retrabalho,
                        COALESCE(SUM(CASE WHEN rp."retrabalho" THEN rp."QUANTIDADE" ELSE 0 END), 0) AS total_quantidade_retrabalho
                    FROM pecas_retrabalho_sem_duplicadas rp
                    GROUP BY rp.mes
                )
                -- CÁLCULO FINAL
                SELECT  * from retrabalho_pecas

            """
            return pd.read_sql(query, self.db_engine)

        except Exception as e:
            logging.error(f"Erro ao retornar os dados: get_custo_mensal_pecas_retrabalho {e}")
            return pd.DataFrame()

    
    def get_troca_pecas_mensal(
        self,
        datas: List[str],
        lista_modelos: List[str],
        lista_oficinas: List[str],
        lista_secoes: List[str],
        lista_pecas: List[str]
    )-> pd.DataFrame:
        """
        Método para recuperar o total de peças trocadas por tipo e mês, com base nos parâmetros fornecidos, 
        aplicando filtros por datas, modelos, oficinas, seções e tipos de peças.

        Parâmetros:
        -----------
        datas : List[str]
            Uma lista contendo duas datas: a data inicial e a data final, no formato 'dd/mm/yyyy'.
            Exemplo: ['01/01/2022', '31/01/2022'].
            
        lista_modelos : List[str]
            Lista com os modelos dos veículos a serem filtrados.
            
        lista_oficinas : List[str]
            Lista com as oficinas a serem filtradas.
            
        lista_secoes : List[str]
            Lista com as seções a serem filtradas.
            
        lista_pecas : List[str]
            Lista com os tipos de peças a serem filtrados.

        Retorno:
        --------
        pd.DataFrame
            DataFrame contendo o total de peças trocadas, agrupadas por tipo de peça e mês, 
            com as colunas: 'mes', 'tipo_peca' e 'quantidade_total'. Caso ocorra algum erro, 
            o método retorna um DataFrame vazio.
        """
        # Validação simples de entrada
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")
        
        try:
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            subquery_secoes_str = subquery_secoes(lista_secoes)
            subquery_modelo_str = subquery_modelos(lista_modelos)
            subquery_ofcina_str = subquery_oficinas(lista_oficinas)
            subquery_pecas_str = subquery_pecas(lista_pecas)
                

            query = f"""
                WITH cte AS (
                    SELECT DISTINCT ON (pecas_gerais."KEY_HASH")
                        TO_CHAR("DATA"::DATE, 'YYYY-MM') AS mes,
                        CASE 
                            WHEN LOWER("PRODUTO") ILIKE '%%recond%%' THEN 'Recondicionada'
                            ELSE 'Nao Recondicionada'
                        END AS tipo_peca,
                        "QUANTIDADE"
                    FROM 
                        pecas_gerais
                    LEFT JOIN 
                        os_dados ON "NUMERO DA OS" = "OS"
                    WHERE "DATA"::DATE  BETWEEN DATE '{data_inicio}' AND DATE '{data_fim}'     
                    and "TIPO DE MANUTENCAO" = 'Corretiva'
                    {subquery_secoes_str}
                    {subquery_modelo_str}
                    {subquery_ofcina_str}
                    {subquery_pecas_str}
                )
                SELECT
                    mes,
                    tipo_peca,
                    ROUND(SUM("QUANTIDADE"), 2) AS quantidade_total
                FROM
                    cte
                GROUP BY
                    mes,
                    tipo_peca
                ORDER BY
                    mes, tipo_peca;
            """
            return pd.read_sql(query, self.db_engine)
        
        except ValueError as e:
            logging.error(f"Erro ao converter datas: get_custo_mensal_pecas {e}")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Erro ao retornar os dados: get_custo_mensal_pecas {e}")
            return pd.DataFrame()
        
    def get_rank_pecas(
        self,
        datas: List[str],
        lista_modelos: List[str],
        lista_oficinas: List[str],
        lista_secoes: List[str],
        lista_pecas: List[str]
    )-> pd.DataFrame:
        """
            Retorna um ranking de peças mais utilizadas no período especificado, 
            com base em filtros aplicados por modelo de veículo, oficina, seção e peças.

            Parâmetros:
            -----------
            datas : List[str]
                Lista com duas datas no formato string (ex: ["01/01/2024", "31/03/2024"])
                representando o intervalo [data_inicial, data_final].

            lista_modelos : List[str]
                Lista de modelos de veículos a serem filtrados.

            lista_oficinas : List[str]
                Lista de oficinas a serem consideradas no filtro.

            lista_secoes : List[str]
                Lista de seções (ex: áreas, centros de custo, departamentos, etc.) para filtrar os dados.

            lista_pecas : List[str]
                Lista de nomes de peças para incluir no filtro.

            Retorno:
            --------
            pd.DataFrame
                Um DataFrame contendo o ranking das peças, incluindo:
                - `posicao`: posição no ranking com base no valor total gasto.
                - `nome_peca`: nome da peça.
                - `quantidade`: soma total das quantidades utilizadas.
                - `frequencia`: número de ocorrências (linhas) da peça.
                - `valor_total`: valor total gasto com a peça (quantidade * valor unitário).
                - `valor_por_unidade`: valor médio por unidade da peça.
        """
        # Validação simples de entrada
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")
        
        try:
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            subquery_secoes_str = subquery_secoes(lista_secoes)
            subquery_modelo_str = subquery_modelos(lista_modelos)
            subquery_ofcina_str = subquery_oficinas(lista_oficinas)
            subquery_pecas_str = subquery_pecas(lista_pecas)
                

            query = f"""
                  WITH pecas AS (
                SELECT DISTINCT ON (view_pecas_desconsiderando_combustivel."KEY_HASH")
                    "PRODUTO" AS nome_peca,
                    "QUANTIDADE",
                    "VALOR",
                    "OS",
                    "PRODUTO",
                    "DATA"
                FROM view_pecas_desconsiderando_combustivel
                LEFT JOIN os_dados 
                    ON "NUMERO DA OS" = "OS"
                WHERE "DATA"::DATE  BETWEEN DATE '{data_inicio}' AND DATE '{data_fim}'
                and "TIPO DE MANUTENCAO" = 'Corretiva'
                {subquery_secoes_str}
                {subquery_modelo_str}
                {subquery_ofcina_str}
                {subquery_pecas_str}
            ),
            -- CTE DE RANKING PARA ALGUNS VALORES
            ranked_pecas AS (
                SELECT
                    nome_peca,
                    SUM("QUANTIDADE") AS quantidade,
                    COUNT(*) AS frequencia,
                    SUM("VALOR") AS valor_total,
                    SUM("VALOR") / NULLIF(SUM("QUANTIDADE"), 0) AS valor_por_unidade,
                    RANK() OVER (ORDER BY SUM("VALOR") DESC) AS posicao
                FROM pecas
                GROUP BY nome_peca
            ),
            -- CTE INICIAL DO RETRABALHO DA OS
            retrabalho_os AS (
                SELECT *
                FROM mat_view_retrabalho_30_dias_distinct
                where "TIPO DE MANUTENCAO" = 'Corretiva'
            ),
            -- CTE INTERMEDIARIA QUE IDENTIFICA E RETIRA AS OS
            pecas_retrabalho_sem_duplicadas AS (
                SELECT *
                FROM (
                    SELECT 
                        pg.*,
                        r.*,
                        COUNT(*) OVER (
                            PARTITION BY pg."PRODUTO", r."NUMERO DA OS"
                        ) AS qtde_linhas
                    FROM pecas pg
                    LEFT JOIN retrabalho_os r
                        ON pg."OS" = r."NUMERO DA OS"
                ) sub
                WHERE qtde_linhas = 1  -- mantém apenas grupos que têm 1 linha
            ),
            -- CTE QUE REALIZA OS CÁLCULOS VALORES GASTOS COM RETRABALHO DADO A TABELA JÁ FILTRADA pecas_retrabalho_sem_duplicadas
            retrabalho_pecas AS (
                SELECT 
                    rp."PRODUTO" AS nome_peca,
                    COALESCE(SUM(CASE WHEN rp."retrabalho" THEN rp."VALOR" ELSE 0 END), 0) AS total_gasto_retrabalho,
                    COALESCE(SUM(rp."VALOR"), 0) AS total_gasto,
                    ROUND(
                        100 * SUM(CASE WHEN rp."retrabalho" IS NOT NULL THEN rp."VALOR" ELSE 0 END)::NUMERIC / NULLIF(SUM(rp."VALOR"), 0),
                        2
                    ) AS perc_gasto_retrabalho
                FROM pecas_retrabalho_sem_duplicadas rp
                GROUP BY rp."PRODUTO"
            ),
            -- CTE DE RETRABALHO "CRUA" QUE SERVE PARA IDENTIFICAR OS DUPLICADOS
            retrabalho_contagem AS (
                SELECT  
                    pg."PRODUTO" AS nome_peca,
                    pg."OS" AS numero_os,
                    r."DESCRICAO DO SERVICO" AS descricao_servico
                FROM pecas pg
                LEFT JOIN retrabalho_os r
                    ON pg."OS" = r."NUMERO DA OS"
            ),
            -- ESSA CTE REALIZA A CONTAGEM DE DUPLICADAS POR PEÇA E NUMERO DE OS. NA TEORIA DEVERIA TER UM NOME DE PÇ PARA CADA OS
            contagem AS (
                SELECT 
                    nome_peca,
                    numero_os,
                    COUNT(*) AS qtd_linhas
                FROM retrabalho_contagem
                GROUP BY nome_peca, numero_os
            ),
            -- ESSA CTE CLASSIFICA CADA COMBINAÇÃO DE NOME DE PEÇA E OS COMO UNICA (1) OU DUPLICADA (>1)
            classificacao AS (
                SELECT
                    nome_peca,
                    CASE WHEN qtd_linhas = 1 THEN 1 ELSE 0 END AS unica,
                    CASE WHEN qtd_linhas > 1 THEN 1 ELSE 0 END AS duplicada
                FROM contagem
            ),
            -- AQUI É CALCULADO A PORCENTAGEM DE (UNICO/DUPLICAD0) POR NOME_PEÇA 
            percentuais AS (
                SELECT
                    nome_peca,
                    ROUND(100.0 * SUM(unica) / COUNT(*), 2) AS perc_unica,
                    ROUND(100.0 * SUM(duplicada) / COUNT(*), 2) AS perc_duplicada
                FROM classificacao
                GROUP BY nome_peca
            )
            -- CÁLCULO FINAL
            SELECT 
                r.posicao,
                r.nome_peca,
                ROUND(r.quantidade, 2) AS quantidade,
                ROUND(r.frequencia, 2) AS frequencia,
                ROUND(r.valor_total, 2) AS valor_total,
                ROUND(r.valor_por_unidade, 2) AS valor_por_unidade,
                ROUND(COALESCE(rt.total_gasto_retrabalho, 0), 2) AS total_gasto_retrabalho,
                ROUND(COALESCE(rt.total_gasto, 0), 2) AS total_gasto_com_left,
                --COALESCE(rt.perc_gasto_retrabalho, 0) AS perc_gasto_retrabalho,
                COALESCE(
                ROUND(
                    (rt.total_gasto_retrabalho / NULLIF(r.valor_total, 0)) * 100,
                    2
                ),
                0
                ) AS perc_gasto_retrabalho,
                pt.perc_unica as indicador_confiabibilidade_retrabalho,
                pt.perc_duplicada
                --pt.perc_duplicada
            FROM ranked_pecas r
            LEFT JOIN retrabalho_pecas rt 
                ON r.nome_peca = rt.nome_peca
            left join percentuais pt
                on pt.nome_peca = r.nome_peca
            ORDER BY r.posicao;
            """
            return pd.read_sql(query, self.db_engine)
        
        except ValueError as e:
            logging.error(f"Erro ao converter datas: get_custo_mensal_pecas {e}")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Erro ao retornar os dados: get_custo_mensal_pecas {e}")
            return pd.DataFrame()
        
    def get_principais_pecas(
        self,
        datas: List[str],
        lista_modelos: List[str],
        lista_oficinas: List[str],
        lista_secoes: List[str],
        lista_pecas: List[str]
    )-> pd.DataFrame:
        """
            Retorna um ranking de peças mais utilizadas no período especificado, 
            com base em filtros aplicados por modelo de veículo, oficina, seção e peças.

            Parâmetros:
            -----------
            datas : List[str]
                Lista com duas datas no formato string (ex: ["01/01/2024", "31/03/2024"])
                representando o intervalo [data_inicial, data_final].

            lista_modelos : List[str]
                Lista de modelos de veículos a serem filtrados.

            lista_oficinas : List[str]
                Lista de oficinas a serem consideradas no filtro.

            lista_secoes : List[str]
                Lista de seções (ex: áreas, centros de custo, departamentos, etc.) para filtrar os dados.

            lista_pecas : List[str]
                Lista de nomes de peças para incluir no filtro.

            Retorno:
            --------
            pd.DataFrame
                Um DataFrame contendo o ranking das peças, incluindo:
                - `posicao`: posição no ranking com base no valor total gasto.
                - `nome_peca`: nome da peça.
                - `quantidade`: soma total das quantidades utilizadas.
                - `frequencia`: número de ocorrências (linhas) da peça.
                - `valor_total`: valor total gasto com a peça (quantidade * valor unitário).
                - `valor_por_unidade`: valor médio por unidade da peça.
        """
        # Validação simples de entrada
        if not datas or len(datas) != 2:
            raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")
        
        try:
            data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
            data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

            subquery_secoes_str = subquery_secoes(lista_secoes)
            subquery_modelo_str = subquery_modelos(lista_modelos)
            subquery_ofcina_str = subquery_oficinas(lista_oficinas)
            subquery_pecas_str = subquery_pecas(lista_pecas)
                

            query = f"""
            WITH pecas AS (
                SELECT DISTINCT ON (view_pecas_desconsiderando_combustivel."KEY_HASH")
                    "PRODUTO" AS nome_peca,
                    "QUANTIDADE",
                    "VALOR",
                    "OS",
                    "PRODUTO",
                    "DATA"
                FROM view_pecas_desconsiderando_combustivel
                LEFT JOIN os_dados 
                    ON "NUMERO DA OS" = "OS"
                WHERE "DATA"::DATE  BETWEEN DATE '{data_inicio}' AND DATE '{data_fim}'
                    and "TIPO DE MANUTENCAO" = 'Corretiva'
                {subquery_secoes_str}
                {subquery_modelo_str}
                {subquery_ofcina_str}
                {subquery_pecas_str}
            ),
            -- CTE DE RANKING PARA ALGUNS VALORES
            ranked_pecas AS (
                SELECT
                    nome_peca,
                    SUM("QUANTIDADE") AS quantidade,
                    COUNT(*) AS frequencia,
                    SUM("VALOR") AS valor_total,
                    SUM("VALOR") / NULLIF(SUM("QUANTIDADE"), 0) AS valor_por_unidade,
                    RANK() OVER (ORDER BY SUM("VALOR") DESC) AS posicao
                FROM pecas
                GROUP BY nome_peca
            ),
            -- CTE INICIAL DO RETRABALHO DA OS
            retrabalho_os AS (
                SELECT *
                FROM mat_view_retrabalho_30_dias_distinct
                where "TIPO DE MANUTENCAO" = 'Corretiva'
            ),
            -- CTE INTERMEDIARIA QUE IDENTIFICA E RETIRA AS OS
            pecas_retrabalho_sem_duplicadas AS (
                SELECT *
                FROM (
                    SELECT 
                        pg.*,
                        r.*,
                        COUNT(*) OVER (
                            PARTITION BY pg."PRODUTO", r."NUMERO DA OS"
                        ) AS qtde_linhas
                    FROM pecas pg
                    LEFT JOIN retrabalho_os r
                        ON pg."OS" = r."NUMERO DA OS"
                ) sub
                WHERE qtde_linhas = 1  -- mantém apenas grupos que têm 1 linha
            ),
            -- CTE QUE REALIZA OS CÁLCULOS VALORES GASTOS COM RETRABALHO DADO A TABELA JÁ FILTRADA pecas_retrabalho_sem_duplicadas
            retrabalho_pecas AS (
                SELECT 
                    rp."PRODUTO" AS nome_peca,
                    COALESCE(SUM(CASE WHEN rp."retrabalho" THEN rp."VALOR" ELSE 0 END), 0) AS total_gasto_retrabalho,
                    COALESCE(SUM(rp."VALOR"), 0) AS total_gasto,
                    ROUND(
                        100 * SUM(CASE WHEN rp."retrabalho" IS NOT NULL THEN rp."VALOR" ELSE 0 END)::NUMERIC / NULLIF(SUM(rp."VALOR"), 0),
                        2
                    ) AS perc_gasto_retrabalho
                FROM pecas_retrabalho_sem_duplicadas rp
                GROUP BY rp."PRODUTO"
            ),
            -- CTE DE RETRABALHO "CRUA" QUE SERVE PARA IDENTIFICAR OS DUPLICADOS
            retrabalho_contagem AS (
                SELECT  
                    pg."PRODUTO" AS nome_peca,
                    pg."OS" AS numero_os,
                    r."DESCRICAO DO SERVICO" AS descricao_servico
                FROM pecas pg
                LEFT JOIN retrabalho_os r
                    ON pg."OS" = r."NUMERO DA OS"
            ),
            -- ESSA CTE REALIZA A CONTAGEM DE DUPLICADAS POR PEÇA E NUMERO DE OS. NA TEORIA DEVERIA TER UM NOME DE PÇ PARA CADA OS
            contagem AS (
                SELECT 
                    nome_peca,
                    numero_os,
                    COUNT(*) AS qtd_linhas
                FROM retrabalho_contagem
                GROUP BY nome_peca, numero_os
            ),
            -- ESSA CTE CLASSIFICA CADA COMBINAÇÃO DE NOME DE PEÇA E OS COMO UNICA (1) OU DUPLICADA (>1)
            classificacao AS (
                SELECT
                    nome_peca,
                    CASE WHEN qtd_linhas = 1 THEN 1 ELSE 0 END AS unica,
                    CASE WHEN qtd_linhas > 1 THEN 1 ELSE 0 END AS duplicada
                FROM contagem
            ),
            -- AQUI É CALCULADO A PORCENTAGEM DE (UNICO/DUPLICAD0) POR NOME_PEÇA 
            percentuais AS (
                SELECT
                    nome_peca,
                    ROUND(100.0 * SUM(unica) / COUNT(*), 2) AS perc_unica,
                    ROUND(100.0 * SUM(duplicada) / COUNT(*), 2) AS perc_duplicada
                FROM classificacao
                GROUP BY nome_peca
            )
            -- CÁLCULO FINAL
            SELECT 
                r.posicao,
                r.nome_peca,
                ROUND(r.quantidade, 2) AS quantidade,
                ROUND(r.frequencia, 2) AS frequencia,
                ROUND(r.valor_total, 2) AS valor_total,
                ROUND(r.valor_por_unidade, 2) AS valor_por_unidade,
                ROUND(COALESCE(rt.total_gasto_retrabalho, 0), 2) AS total_gasto_retrabalho,
                ROUND(COALESCE(rt.total_gasto, 0), 2) AS total_gasto_com_left,
                --COALESCE(rt.perc_gasto_retrabalho, 0) AS perc_gasto_retrabalho,
                COALESCE(
                ROUND(
                    (rt.total_gasto_retrabalho / NULLIF(r.valor_total, 0)) * 100,
                    2
                ),
                0
                ) AS perc_gasto_retrabalho,
                pt.perc_unica as indicador_confiabibilidade_retrabalho,
                pt.perc_duplicada
                --pt.perc_duplicada
            FROM ranked_pecas r
            LEFT JOIN retrabalho_pecas rt 
                ON r.nome_peca = rt.nome_peca
            left join percentuais pt
                on pt.nome_peca = r.nome_peca
            ORDER BY r.posicao;
            """
            return pd.read_sql(query, self.db_engine)
        
        except ValueError as e:
            logging.error(f"Erro ao converter datas: get_custo_mensal_pecas {e}")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Erro ao retornar os dados: get_custo_mensal_pecas {e}")
            return pd.DataFrame()
    

# -----> Arrumar alguma forma de arrumar essas função        
    # def get_troca_pecas_rank(
    #     self,
    #     datas: List[str],
    #     lista_modelos: List[str],
    #     lista_oficinas: List[str],
    #     lista_secoes: List[str],
    #     lista_pecas: List[str]
    # )-> pd.DataFrame:
        
    #     # Validação simples de entrada
    #     if not datas or len(datas) != 2:
    #         raise ValueError("O parâmetro 'datas' deve conter duas datas: [data_inicial, data_final].")
        
    #     try:
    #         data_inicio = pd.to_datetime(datas[0]).strftime("%d/%m/%Y")
    #         data_fim = pd.to_datetime(datas[1]).strftime("%d/%m/%Y")

    #         subquery_secoes_str = subquery_secoes(lista_secoes)
    #         subquery_modelo_str = subquery_modelos(lista_modelos)
    #         subquery_ofcina_str = subquery_oficinas(lista_oficinas)
    #         subquery_pecas_str = subquery_pecas(lista_pecas)
                

    #         query = f"""
    #             select
    #                 "id",
    #                 "EQUIPAMENTO",
    #                 "MODELO",
    #                 "PRODUTO" AS nome_peca,
    #                 "QUANTIDADE",
    #                 "VALOR",
    #                 "DATA"
    #             FROM pecas_gerais pg
    #             LEFT JOIN os_dados od ON "NUMERO DA OS" = "OS"
    #             WHERE "DATA" BETWEEN '{data_inicio}' AND '{data_fim}'    
    #                 {subquery_secoes_str}
    #                 {subquery_modelo_str}
    #                 {subquery_ofcina_str}
    #                 {subquery_pecas_str};
    #         """
    #         df = pd.read_sql(query, self.db_engine)

    #         # Removendo duplicadas e convertendo para datetime antes do agrupamento
    #         df.drop_duplicates(subset="id", inplace=True)
    #         df["DATA"] = pd.to_datetime(df["DATA"], dayfirst=True, errors="coerce")

    #         # 1. Agrupar dados por EQUIPAMENTO, MODELO e nome_peca
    #         df["primeiro_mes"] = df.groupby(["EQUIPAMENTO", "MODELO", "nome_peca"])["DATA"].transform("min").dt.to_period("M").dt.to_timestamp()
    #         df["ultimo_mes"] = df.groupby(["EQUIPAMENTO", "MODELO", "nome_peca"])["DATA"].transform("max").dt.to_period("M").dt.to_timestamp()
    #          # Verificando se as colunas "primeiro_mes" e "ultimo_mes" foram criadas corretamente
    #         print(df[["EQUIPAMENTO", "MODELO", "nome_peca", "primeiro_mes", "ultimo_mes"]].head())  

    #         # 2. Calcular quantidade total e valor total
    #         agg = df.groupby(["EQUIPAMENTO", "MODELO", "nome_peca"]).agg(
    #             quantidade_total=("QUANTIDADE", "sum"),
    #             valor_total=("VALOR", lambda x: (x * df.loc[x.index, "QUANTIDADE"]).sum())
    #         ).reset_index()

    #         # 3. Calcular meses de diferença e média mensal
    #         agg["meses"] = ((agg["ultimo_mes"].dt.year - agg["primeiro_mes"].dt.year) * 12 +
    #                         (agg["ultimo_mes"].dt.month - agg["primeiro_mes"].dt.month))
    #         agg["media_mensal"] = agg["valor_total"] / agg["meses"].replace(0, pd.NA)

    #         # 4. Calcular média por modelo
    #         media_modelo = agg.groupby(["MODELO", "nome_peca"])["valor_total"].mean().reset_index(name="valor_medio_modelo")

    #         # 5. Adicionar média do modelo diretamente no agg
    #         agg = agg.merge(media_modelo, on=["MODELO", "nome_peca"], how="left")

    #         # 6. Calcular a diferença de valor
    #         agg["diferenca_valor"] = agg["valor_total"] - agg["valor_medio_modelo"]

    #         # 7. Ordenar os resultados por quantidade
    #         agg = agg.sort_values("quantidade_total", ascending=False)

    #         return agg
    #     except ValueError as e:
    #         logging.error(f"Erro ao converter datas: get_custo_mensal_pecas {e}")
    #         return pd.DataFrame()
    #     except Exception as e:
    #         logging.error(f"Erro ao retornar os dados: get_custo_mensal_pecas {e}")
    #         return pd.DataFrame()        
