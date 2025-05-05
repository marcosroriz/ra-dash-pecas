#!/usr/bin/env python
# coding: utf-8

# Classe que centraliza os serviços para mostrar na página home

# Imports básicos
import re
import pandas as pd
import numpy as np

# Imports auxiliares
from modules.sql_utils import subquery_oficinas, subquery_secoes, subquery_os, subquery_modelos
from modules.entities_utils import get_mecanicos


# Classe do serviço
class HomeService:
    def __init__(self, dbEngine):
        self.dbEngine = dbEngine

    def get_sintese_geral(self, datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
        """Função para obter a síntese geral (que será usado para o gráfico de pizza)"""

        # Extraí a data inicial (já em string)
        data_inicio_str = datas[0]

        # Extraí a data final
        # Remove min_dias antes para evitar que a última OS não seja retrabalho
        data_fim = pd.to_datetime(datas[1])
        data_fim = data_fim - pd.DateOffset(days=min_dias + 1)
        data_fim_str = data_fim.strftime("%Y-%m-%d")

        # Subqueries
        subquery_modelos_str = subquery_modelos(lista_modelos, termo_all="TODOS")
        subquery_oficinas_str = subquery_oficinas(lista_oficinas)
        subquery_secoes_str = subquery_secoes(lista_secaos)
        subquery_os_str = subquery_os(lista_os)

        # Query
        query = f"""
            SELECT
                COUNT(*) AS "TOTAL_NUM_OS",
                SUM(CASE WHEN retrabalho THEN 1 ELSE 0 END) AS "TOTAL_RETRABALHO",
                SUM(CASE WHEN correcao THEN 1 ELSE 0 END) AS "TOTAL_CORRECAO",
                SUM(CASE WHEN correcao_primeira THEN 1 ELSE 0 END) AS "TOTAL_CORRECAO_PRIMEIRA",
                100 * ROUND(SUM(CASE WHEN retrabalho THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_RETRABALHO",
                100 * ROUND(SUM(CASE WHEN correcao THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_CORRECAO",
                100 * ROUND(SUM(CASE WHEN correcao_primeira THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_CORRECAO_PRIMEIRA"
            FROM
                mat_view_retrabalho_{min_dias}_dias_distinct
            WHERE
                "DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
                {subquery_modelos_str}
                {subquery_oficinas_str}
                {subquery_secoes_str}
                {subquery_os_str}
        """

        # Executa a query
        df = pd.read_sql(query, self.dbEngine)

        # Calcula o total de correções tardia
        df["TOTAL_CORRECAO_TARDIA"] = df["TOTAL_CORRECAO"] - df["TOTAL_CORRECAO_PRIMEIRA"]

        return df

    def get_retrabalho_por_modelo(self, datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
        """Função para obter o quantitativo de retrabalho e correções de primeira por modelo"""

        # Extraí a data inicial (já em string)
        data_inicio_str = datas[0]

        # Extraí a data final
        # Remove min_dias antes para evitar que a última OS não seja retrabalho
        data_fim = pd.to_datetime(datas[1])
        data_fim = data_fim - pd.DateOffset(days=min_dias + 1)
        data_fim_str = data_fim.strftime("%Y-%m-%d")

        # Subqueries
        subquery_modelos_str = subquery_modelos(lista_modelos, termo_all="TODOS")
        subquery_oficinas_str = subquery_oficinas(lista_oficinas)
        subquery_secoes_str = subquery_secoes(lista_secaos)
        subquery_os_str = subquery_os(lista_os)

        # Queries
        # Primeiro pegamos o total de veículos por modelo no período, não vamos restringir por problema
        query_total_frota = f"""
        SELECT 
            "DESCRICAO DO MODELO", 
            COUNT(DISTINCT "CODIGO DO VEICULO") AS "TOTAL_FROTA_PERIODO"
        FROM 
            mat_view_retrabalho_{min_dias}_dias_distinct
        WHERE
            "DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
            {subquery_modelos_str}
            {subquery_oficinas_str}
        GROUP BY 
            "DESCRICAO DO MODELO"
        """

        query_teve_problema = f"""
        SELECT 
            "DESCRICAO DO MODELO", 
            COUNT(DISTINCT "CODIGO DO VEICULO") AS "TOTAL_FROTA_TEVE_PROBLEMA"
        FROM 
            mat_view_retrabalho_{min_dias}_dias_distinct
        WHERE
            "DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
            {subquery_modelos_str}
            {subquery_oficinas_str}
            {subquery_secoes_str}
            {subquery_os_str}
        GROUP BY 
            "DESCRICAO DO MODELO"
        """

        query_teve_retrabalho = f"""
        SELECT 
            "DESCRICAO DO MODELO", 
            COUNT(DISTINCT "CODIGO DO VEICULO") AS "TOTAL_FROTA_TEVE_RETRABALHO"
        FROM 
            mat_view_retrabalho_{min_dias}_dias_distinct
        WHERE
            "DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
            {subquery_modelos_str}
            {subquery_oficinas_str}
            {subquery_secoes_str}
            {subquery_os_str}
            AND retrabalho = TRUE
        GROUP BY 
            "DESCRICAO DO MODELO"
        """

        # Executa Queries
        df_total_frota = pd.read_sql(query_total_frota, self.dbEngine)
        df_teve_problema = pd.read_sql(query_teve_problema, self.dbEngine)
        df_teve_retrabalho = pd.read_sql(query_teve_retrabalho, self.dbEngine)

        # Merge dos dataframes
        df = df_total_frota.merge(df_teve_problema, on="DESCRICAO DO MODELO", how="left")
        df = df.merge(df_teve_retrabalho, on="DESCRICAO DO MODELO", how="left")
        df.fillna(0, inplace=True)

        # Calcular campos
        df["NAO_TEVE_PROBLEMA"] = df["TOTAL_FROTA_PERIODO"] - df["TOTAL_FROTA_TEVE_PROBLEMA"]
        df["TEVE_PROBLEMA_SEM_RETRABALHO"] = df["TOTAL_FROTA_TEVE_PROBLEMA"] - df["TOTAL_FROTA_TEVE_RETRABALHO"]
        df["TEVE_PROBLEMA_E_RETRABALHO"] = df["TOTAL_FROTA_TEVE_RETRABALHO"]

        # Calcula as porcentagens
        df["PERC_NAO_TEVE_PROBLEMA"] = round(100 * df["NAO_TEVE_PROBLEMA"] / df["TOTAL_FROTA_PERIODO"], 1)
        df["PERC_TEVE_PROBLEMA_SEM_RETRABALHO"] = round(100 * df["TEVE_PROBLEMA_SEM_RETRABALHO"] / df["TOTAL_FROTA_PERIODO"], 1)
        df["PERC_TEVE_PROBLEMA_E_RETRABALHO"] = round(100 * df["TEVE_PROBLEMA_E_RETRABALHO"] / df["TOTAL_FROTA_PERIODO"], 1)

        return df

    def get_evolucao_retrabalho_por_modelo_por_mes(self, datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
        """Função para obter a evolução do retrabalho por modelo por mes"""
        # Extraí a data inicial (já em string)
        data_inicio_str = datas[0]

        # Extraí a data final
        # Remove min_dias antes para evitar que a última OS não seja retrabalho
        data_fim = pd.to_datetime(datas[1])
        data_fim = data_fim - pd.DateOffset(days=min_dias + 1)
        data_fim_str = data_fim.strftime("%Y-%m-%d")

        # Subqueries
        subquery_modelos_str = subquery_modelos(lista_modelos, termo_all="TODOS")
        subquery_oficinas_str = subquery_oficinas(lista_oficinas)
        subquery_secoes_str = subquery_secoes(lista_secaos)
        subquery_os_str = subquery_os(lista_os)

        query = f"""
        SELECT
            to_char(to_timestamp("DATA DO FECHAMENTO DA OS", 'YYYY-MM-DD"T"HH24:MI:SS'), 'YYYY-MM') AS year_month,
            "DESCRICAO DO MODELO",
            100 * ROUND(SUM(CASE WHEN retrabalho THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_RETRABALHO",
            100 * ROUND(SUM(CASE WHEN correcao_primeira THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_CORRECAO_PRIMEIRA"
        FROM
            mat_view_retrabalho_{min_dias}_dias_distinct
        WHERE
            "DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
            {subquery_modelos_str}
            {subquery_oficinas_str}
            {subquery_secoes_str}
            {subquery_os_str}
        GROUP BY
            year_month, "DESCRICAO DO MODELO"
        ORDER BY
            year_month;
        """

        # Executa query
        df = pd.read_sql(query, self.dbEngine)

        # Arruma dt
        df["year_month_dt"] = pd.to_datetime(df["year_month"], format="%Y-%m", errors="coerce")

        # Funde (melt) colunas de retrabalho e correção
        df_combinado = df.melt(
            id_vars=["year_month_dt", "DESCRICAO DO MODELO"],
            value_vars=["PERC_RETRABALHO", "PERC_CORRECAO_PRIMEIRA"],
            var_name="CATEGORIA",
            value_name="PERC",
        )

        # Renomeia as colunas
        df_combinado["CATEGORIA"] = df_combinado["CATEGORIA"].replace({"PERC_RETRABALHO": "RETRABALHO", "PERC_CORRECAO_PRIMEIRA": "CORRECAO_PRIMEIRA"})

        return df_combinado

    def get_evolucao_retrabalho_por_oficina_por_mes(self, datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
        """Função para obter a evolução do retrabalho por oficina por mes"""
        # Extraí a data inicial (já em string)
        data_inicio_str = datas[0]

        # Extraí a data final
        # Remove min_dias antes para evitar que a última OS não seja retrabalho
        data_fim = pd.to_datetime(datas[1])
        data_fim = data_fim - pd.DateOffset(days=min_dias + 1)
        data_fim_str = data_fim.strftime("%Y-%m-%d")

        # Subqueries
        subquery_modelos_str = subquery_modelos(lista_modelos, termo_all="TODOS")
        subquery_oficinas_str = subquery_oficinas(lista_oficinas)
        subquery_secoes_str = subquery_secoes(lista_secaos)
        subquery_os_str = subquery_os(lista_os)

        query = f"""
        SELECT
            to_char(to_timestamp("DATA DO FECHAMENTO DA OS", 'YYYY-MM-DD"T"HH24:MI:SS'), 'YYYY-MM') AS year_month,
            "DESCRICAO DA OFICINA",
            100 * ROUND(SUM(CASE WHEN retrabalho THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_RETRABALHO",
            100 * ROUND(SUM(CASE WHEN correcao_primeira THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_CORRECAO_PRIMEIRA"
        FROM
            mat_view_retrabalho_{min_dias}_dias_distinct
        WHERE
            "DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
            {subquery_modelos_str}
            {subquery_oficinas_str}
            {subquery_secoes_str}
            {subquery_os_str}
        GROUP BY
            year_month, "DESCRICAO DA OFICINA"
        ORDER BY
            year_month;
        """

        # Executa query
        df = pd.read_sql(query, self.dbEngine)

        # Arruma dt
        df["year_month_dt"] = pd.to_datetime(df["year_month"], format="%Y-%m", errors="coerce")

        # Funde (melt) colunas de retrabalho e correção
        df_combinado = df.melt(
            id_vars=["year_month_dt", "DESCRICAO DA OFICINA"],
            value_vars=["PERC_RETRABALHO", "PERC_CORRECAO_PRIMEIRA"],
            var_name="CATEGORIA",
            value_name="PERC",
        )

        # Renomeia as colunas
        df_combinado["CATEGORIA"] = df_combinado["CATEGORIA"].replace({"PERC_RETRABALHO": "RETRABALHO", "PERC_CORRECAO_PRIMEIRA": "CORRECAO_PRIMEIRA"})

        return df_combinado

    def get_evolucao_retrabalho_por_secao_por_mes(self, datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
        """Função para obter a evolução do retrabalho por seção por mes"""
        # Extraí a data inicial (já em string)
        data_inicio_str = datas[0]

        # Extraí a data final
        # Remove min_dias antes para evitar que a última OS não seja retrabalho
        data_fim = pd.to_datetime(datas[1])
        data_fim = data_fim - pd.DateOffset(days=min_dias + 1)
        data_fim_str = data_fim.strftime("%Y-%m-%d")

        # Subqueries
        subquery_modelos_str = subquery_modelos(lista_modelos, termo_all="TODOS")
        subquery_oficinas_str = subquery_oficinas(lista_oficinas)
        subquery_secoes_str = subquery_secoes(lista_secaos)
        subquery_os_str = subquery_os(lista_os)

        query = f"""
        SELECT
            to_char(to_timestamp("DATA DO FECHAMENTO DA OS", 'YYYY-MM-DD"T"HH24:MI:SS'), 'YYYY-MM') AS year_month,
            "DESCRICAO DA SECAO",
            100 * ROUND(SUM(CASE WHEN retrabalho THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_RETRABALHO",
            100 * ROUND(SUM(CASE WHEN correcao_primeira THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_CORRECAO_PRIMEIRA"
        FROM
            mat_view_retrabalho_{min_dias}_dias_distinct
        WHERE
            "DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
            {subquery_modelos_str}
            {subquery_oficinas_str}
            {subquery_secoes_str}
            {subquery_os_str}
        GROUP BY
            year_month, "DESCRICAO DA SECAO"
        ORDER BY
            year_month;
        """

        # Executa Query
        df = pd.read_sql(query, self.dbEngine)

        # Arruma dt
        df["year_month_dt"] = pd.to_datetime(df["year_month"], format="%Y-%m", errors="coerce")

        # Funde (melt) colunas de retrabalho e correção
        df_combinado = df.melt(
            id_vars=["year_month_dt", "DESCRICAO DA SECAO"],
            value_vars=["PERC_RETRABALHO", "PERC_CORRECAO_PRIMEIRA"],
            var_name="CATEGORIA",
            value_name="PERC",
        )

        # Renomeia as colunas
        df_combinado["CATEGORIA"] = df_combinado["CATEGORIA"].replace({"PERC_RETRABALHO": "RETRABALHO", "PERC_CORRECAO_PRIMEIRA": "CORRECAO_PRIMEIRA"})

        return df_combinado

    def get_evolucao_retrabalho_por_nota_por_mes(self, datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
        """Função para obter a evolução do retrabalho por nota por mes"""

        # Extraí a data inicial (já em string)
        data_inicio_str = datas[0]

        # Extraí a data final
        # Remove min_dias antes para evitar que a última OS não seja retrabalho
        data_fim = pd.to_datetime(datas[1])
        data_fim = data_fim - pd.DateOffset(days=min_dias + 1)
        data_fim_str = data_fim.strftime("%Y-%m-%d")

        # Subqueries
        subquery_modelos_str = subquery_modelos(lista_modelos, termo_all="TODOS")
        subquery_oficinas_str = subquery_oficinas(lista_oficinas)
        subquery_secoes_str = subquery_secoes(lista_secaos)
        subquery_os_str = subquery_os(lista_os)

        query = f"""
        SELECT
            to_char(to_timestamp("DATA DO FECHAMENTO DA OS", 'YYYY-MM-DD"T"HH24:MI:SS'), 'YYYY-MM') AS year_month,
            to_char(to_timestamp("DATA DO FECHAMENTO DA OS", 'YYYY-MM-DD"T"HH24:MI:SS'), 'YYYY-MM') AS year_month_str,
            AVG(CASE WHEN retrabalho THEN osclass."SCORE_SYMPTOMS_TEXT_QUALITY" ELSE NULL END) AS "NOTA_MEDIA_SINTOMA_COM_RETRABALHO",
            AVG(CASE WHEN retrabalho THEN osclass."SCORE_SOLUTION_TEXT_QUALITY" ELSE NULL END) AS "NOTA_MEDIA_SOLUCAO_COM_RETRABALHO",
            AVG(CASE WHEN correcao_primeira THEN osclass."SCORE_SYMPTOMS_TEXT_QUALITY" ELSE NULL END) AS "NOTA_MEDIA_SINTOMA_SOLUCAO",
            AVG(CASE WHEN correcao_primeira THEN osclass."SCORE_SOLUTION_TEXT_QUALITY" ELSE NULL END) AS "NOTA_MEDIA_SOLUCAO_SOLUCAO"
        FROM
            mat_view_retrabalho_{min_dias}_dias AS retview
        LEFT JOIN 
            os_dados_classificacao AS osclass
            ON retview."KEY_HASH" = osclass."KEY_HASH"
        WHERE
            "DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
            {subquery_modelos_str}
            {subquery_oficinas_str}
            {subquery_secoes_str}
            {subquery_os_str}
        GROUP BY
            year_month
        ORDER BY
            year_month;
        """

        # Executa Query
        df = pd.read_sql(query, self.dbEngine)

        # Arruma dt
        df["year_month_dt"] = pd.to_datetime(df["year_month"], format="%Y-%m", errors="coerce")

        # Funde (melt) colunas de retrabalho e correção dos sintomas
        df_sintoma = df.melt(
            id_vars=["year_month_dt"],
            value_vars=["NOTA_MEDIA_SINTOMA_COM_RETRABALHO", "NOTA_MEDIA_SINTOMA_SOLUCAO"],
            var_name="CATEGORIA",
            value_name="NOTA_MEDIA",
        )

        # Renomeia as colunas
        df_sintoma["CATEGORIA"] = df_sintoma["CATEGORIA"].replace(
            {"NOTA_MEDIA_SINTOMA_COM_RETRABALHO": "RETRABALHO", "NOTA_MEDIA_SINTOMA_SOLUCAO": "CORRECAO_PRIMEIRA"}
        )

        # Adiciona tipo
        df_sintoma["TIPO"] = "SINTOMA"

        # Funde (melt) colunas de retrabalho e correção das solucoes
        df_solucao = df.melt(
            id_vars=["year_month_dt"],
            value_vars=["NOTA_MEDIA_SOLUCAO_COM_RETRABALHO", "NOTA_MEDIA_SOLUCAO_SOLUCAO"],
            var_name="CATEGORIA",
            value_name="NOTA_MEDIA",
        )

        # Renomeia as colunas
        df_solucao["CATEGORIA"] = df_sintoma["CATEGORIA"].replace(
            {"NOTA_MEDIA_SOLUCAO_COM_RETRABALHO": "RETRABALHO", "NOTA_MEDIA_SOLUCAO_SOLUCAO": "CORRECAO_PRIMEIRA"}
        )

        # Adiciona tipo
        df_solucao["TIPO"] = "SOLUCAO"

        # Concatena os dfs
        df_combinado = pd.concat([df_sintoma, df_solucao])

        return df_combinado

    def get_evolucao_retrabalho_por_custo_por_mes(self, datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
        """Função para obter a evolução do retrabalho por custo por mes"""

        # Extraí a data inicial (já em string)
        data_inicio_str = datas[0]

        # Extraí a data final
        # Remove min_dias antes para evitar que a última OS não seja retrabalho
        data_fim = pd.to_datetime(datas[1])
        data_fim = data_fim - pd.DateOffset(days=min_dias + 1)
        data_fim_str = data_fim.strftime("%Y-%m-%d")

        # Subqueries
        subquery_modelos_str = subquery_modelos(lista_modelos, termo_all="TODOS")
        subquery_oficinas_str = subquery_oficinas(lista_oficinas)
        subquery_secoes_str = subquery_secoes(lista_secaos)
        subquery_os_str = subquery_os(lista_os)

        query = f"""
        SELECT
            to_char(to_timestamp("DATA DO FECHAMENTO DA OS", 'YYYY-MM-DD"T"HH24:MI:SS'), 'YYYY-MM') AS year_month,
            to_char(to_timestamp("DATA DO FECHAMENTO DA OS", 'YYYY-MM-DD"T"HH24:MI:SS'), 'YYYY-MM') AS year_month_str,
            SUM(pg."VALOR") AS "TOTAL_GASTO",
	        SUM(CASE WHEN retrabalho THEN pg."VALOR" ELSE NULL END) AS "TOTAL_GASTO_RETRABALHO"
        FROM
            mat_view_retrabalho_{min_dias}_dias_distinct AS main
        JOIN
            view_pecas_desconsiderando_combustivel pg 
        ON
            main."NUMERO DA OS" = pg."OS"
        WHERE
            "DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
            {subquery_modelos_str}
            {subquery_oficinas_str}
            {subquery_secoes_str}
            {subquery_os_str}
        GROUP BY
            year_month
        ORDER BY
            year_month;
        """

        # Executa Query
        df = pd.read_sql(query, self.dbEngine)

        # Arruma dt
        df["year_month_dt"] = pd.to_datetime(df["year_month"], format="%Y-%m", errors="coerce")

        # Computa Perc
        df["PERC_GASTO_RETRABALHO"] = df["TOTAL_GASTO_RETRABALHO"] / df["TOTAL_GASTO"]

        # Arredonda valores
        df["TOTAL_GASTO"] = df["TOTAL_GASTO"].round(2)
        df["TOTAL_GASTO_RETRABALHO"] = df["TOTAL_GASTO_RETRABALHO"].round(2)

        # Funde (melt) colunas de retrabalho e correção dos sintomas
        df_custo = df.melt(
            id_vars=["year_month_dt", "PERC_GASTO_RETRABALHO"],
            value_vars=["TOTAL_GASTO", "TOTAL_GASTO_RETRABALHO"],
            var_name="CATEGORIA",
            value_name="GASTO",
        )

        return df_custo

    def get_top_os_geral_retrabalho(self, datas, min_dias, lista_modelos, lista_oficinas, lista_secaos, lista_os):
        """Função para obter as OSs com mais retrabalho"""

        # Datas
        data_inicio_str = datas[0]

        # Remove min_dias antes para evitar que a última OS não seja retrabalho
        data_fim = pd.to_datetime(datas[1])
        data_fim = data_fim - pd.DateOffset(days=min_dias + 1)
        data_fim_str = data_fim.strftime("%Y-%m-%d")

        # Subqueries
        subquery_modelos_str = subquery_modelos(lista_modelos, termo_all="TODOS")
        subquery_oficinas_str = subquery_oficinas(lista_oficinas)
        subquery_secoes_str = subquery_secoes(lista_secaos)
        subquery_os_str = subquery_os(lista_os)

        inner_subquery_modelos_str = subquery_modelos(lista_modelos, "main.", termo_all="TODOS")
        inner_subquery_oficinas_str = subquery_oficinas(lista_oficinas, "main.")
        inner_subquery_secoes_str = subquery_secoes(lista_secaos, "main.")
        inner_subquery_os_str = subquery_os(lista_os, "main.")

        query = f"""
        WITH normaliza_problema AS (
            SELECT
                "DESCRICAO DA OFICINA",
                "DESCRICAO DA SECAO",
                "DESCRICAO DO SERVICO" as servico,
                "CODIGO DO VEICULO",
                "problem_no"
            FROM
                mat_view_retrabalho_{min_dias}_dias_distinct
            WHERE
                "DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
                {subquery_modelos_str}
                {subquery_oficinas_str}
                {subquery_secoes_str}
                {subquery_os_str}
            GROUP BY
                "DESCRICAO DA OFICINA",
                "DESCRICAO DA SECAO",
                "DESCRICAO DO SERVICO",
                "CODIGO DO VEICULO",
                "problem_no"
        ),
        os_problema AS (
            SELECT
                "DESCRICAO DA OFICINA",
                "DESCRICAO DA SECAO",
                servico,
                COUNT(*) AS num_problema
            FROM
                normaliza_problema
            GROUP BY
                "DESCRICAO DA OFICINA",
                "DESCRICAO DA SECAO",
                servico
        )
        SELECT
            main."DESCRICAO DA OFICINA",
            main."DESCRICAO DA SECAO",
            main."DESCRICAO DO SERVICO",
            COUNT(*) AS "TOTAL_OS",
            SUM(CASE WHEN main.retrabalho THEN 1 ELSE 0 END) AS "TOTAL_RETRABALHO",
            SUM(CASE WHEN main.correcao THEN 1 ELSE 0 END) AS "TOTAL_CORRECAO",
            SUM(CASE WHEN main.correcao_primeira THEN 1 ELSE 0 END) AS "TOTAL_CORRECAO_PRIMEIRA",
            100 * ROUND(SUM(CASE WHEN main.retrabalho THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_RETRABALHO",
            100 * ROUND(SUM(CASE WHEN main.correcao THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_CORRECAO",
            100 * ROUND(SUM(CASE WHEN main.correcao_primeira THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_CORRECAO_PRIMEIRA",
            COALESCE(op.num_problema, 0) AS "TOTAL_PROBLEMA"
        FROM
            mat_view_retrabalho_{min_dias}_dias_distinct AS main
        LEFT JOIN
            os_problema op
        ON
            main."DESCRICAO DA OFICINA" = op."DESCRICAO DA OFICINA"
            AND main."DESCRICAO DA SECAO" = op."DESCRICAO DA SECAO"
            AND main."DESCRICAO DO SERVICO" = op.servico
        WHERE
            main."DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
            {inner_subquery_modelos_str}
            {inner_subquery_oficinas_str}
            {inner_subquery_secoes_str}
            {inner_subquery_os_str}
        GROUP BY
            main."DESCRICAO DA OFICINA",
            main."DESCRICAO DA SECAO",
            main."DESCRICAO DO SERVICO",
            op.num_problema
        ORDER BY
            "PERC_RETRABALHO" DESC;
        """

        # Executa a query
        df = pd.read_sql(query, self.dbEngine)

        # Adiciona campo de relação entre OS e problemas
        df["REL_OS_PROBLEMA"] = round(df["TOTAL_OS"] / df["TOTAL_PROBLEMA"], 2)

        # Novo DF com notas LLM
        query_llm = f"""
        SELECT
            main."DESCRICAO DA OFICINA",
            main."DESCRICAO DA SECAO",
            main."DESCRICAO DO SERVICO",
            AVG(osclass."SCORE_SYMPTOMS_TEXT_QUALITY") AS "NOTA_MEDIA_SINTOMA",
            AVG(osclass."SCORE_SOLUTION_TEXT_QUALITY") AS "NOTA_MEDIA_SOLUCAO",
            100 * ROUND(SUM(CASE WHEN NOT osclass."SYMPTOMS_HAS_COHERENCE_TO_PROBLEM" THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_SINTOMA_NAO_COERENTE",
            100 * ROUND(SUM(CASE WHEN osclass."SYMPTOMS_HAS_COHERENCE_TO_PROBLEM" THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_SINTOMA_COERENTE",
            100 * ROUND(SUM(CASE WHEN NOT osclass."SOLUTION_HAS_COHERENCE_TO_PROBLEM" THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_SOLUCAO_NAO_COERENTE",
            100 * ROUND(SUM(CASE WHEN osclass."SOLUTION_HAS_COHERENCE_TO_PROBLEM" THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC, 4) AS "PERC_SOLUCAO_COERENTE"
        FROM
            mat_view_retrabalho_{min_dias}_dias_distinct AS main
        LEFT JOIN 
            os_dados_classificacao AS osclass
        ON 
            main."KEY_HASH" = osclass."KEY_HASH"
        WHERE
            main."DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
            {inner_subquery_modelos_str}
            {inner_subquery_oficinas_str}
            {inner_subquery_secoes_str}
            {inner_subquery_os_str}
        GROUP BY
            main."DESCRICAO DA OFICINA",
            main."DESCRICAO DA SECAO",
            main."DESCRICAO DO SERVICO"
        """
        # Executa a query
        df_llm = pd.read_sql(query_llm, self.dbEngine)

        # Lida com NaNs
        df_llm = df_llm.fillna(0)

        # Faz Merge
        df_combinado = pd.merge(df, df_llm, on=["DESCRICAO DA OFICINA", "DESCRICAO DA SECAO", "DESCRICAO DO SERVICO"], how="left")

        # Lida com NaNs após merge
        df_combinado = df_combinado.fillna(0)

        # Novo DF com custo
        query_custo = f"""
        SELECT
            main."DESCRICAO DA OFICINA",
            main."DESCRICAO DA SECAO",
            main."DESCRICAO DO SERVICO",
            SUM(pg."VALOR") AS "TOTAL_GASTO",
            SUM(CASE WHEN retrabalho THEN pg."VALOR" ELSE NULL END) AS "TOTAL_GASTO_RETRABALHO"
        FROM
            mat_view_retrabalho_{min_dias}_dias_distinct AS main
        JOIN
            view_pecas_desconsiderando_combustivel pg 
        ON
            main."NUMERO DA OS" = pg."OS"
        WHERE
            main."DATA DO FECHAMENTO DA OS" BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
            {inner_subquery_modelos_str}
            {inner_subquery_oficinas_str}
            {inner_subquery_secoes_str}
            {inner_subquery_os_str}
        GROUP BY
            main."DESCRICAO DA OFICINA",
            main."DESCRICAO DA SECAO",
            main."DESCRICAO DO SERVICO"
        """

        # Executa a query
        df_custo = pd.read_sql(query_custo, self.dbEngine)

        # Arredonda valores
        df_custo["TOTAL_GASTO"] = df_custo["TOTAL_GASTO"].round(2)
        df_custo["TOTAL_GASTO_RETRABALHO"] = df_custo["TOTAL_GASTO_RETRABALHO"].round(2)

        # Lida com NaNs
        df_custo = df_custo.fillna(0)

        # Faz merge novamente
        df_combinado = pd.merge(df_combinado, df_custo, on=["DESCRICAO DA OFICINA", "DESCRICAO DA SECAO", "DESCRICAO DO SERVICO"], how="left")

        # Lida com NaNs após merge
        df_combinado = df_combinado.fillna(0)

        return df_combinado
