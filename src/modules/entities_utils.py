#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import io


# Funções utilitárias para obtenção das principais entidades do sistema


def get_linhas(dbEngine):
    # Linhas
    return pd.read_sql(
        """
        SELECT 
            DISTINCT "linhanumero" AS "LABEL"
        FROM 
            rmtc_linha_info
        ORDER BY
            "linhanumero"
        """,
        dbEngine,
    )


def get_oficinas(dbEngine):
    # Oficinas
    return pd.read_sql(
        """
        SELECT 
            DISTINCT "DESCRICAO DA OFICINA" AS "LABEL"
        FROM 
            mat_view_retrabalho_10_dias mvrd 
        """,
        dbEngine,
    )


def get_secoes(dbEngine):
    # Seções
    return pd.read_sql(
        """
        SELECT 
            DISTINCT "DESCRICAO DA SECAO" AS "LABEL"
        FROM 
            mat_view_retrabalho_10_dias mvrd
        """,
        dbEngine,
    )


def get_mecanicos(dbEngine):
    # Colaboradores / Mecânicos
    return pd.read_sql("SELECT * FROM colaboradores_frotas_os", dbEngine)


def get_lista_os(dbEngine):
    # Lista de OS
    return pd.read_sql(
        """
        SELECT DISTINCT
            "DESCRICAO DA SECAO" as "SECAO",
            "DESCRICAO DO SERVICO" AS "LABEL"
        FROM 
            mat_view_retrabalho_10_dias mvrd 
        ORDER BY
            "DESCRICAO DO SERVICO"
        """,
        dbEngine,
    )


def get_modelos(dbEngine):
    # Lista de OS
    return pd.read_sql(
        """
        SELECT DISTINCT
            "DESCRICAO DO MODELO" AS "MODELO"
        FROM 
            mat_view_retrabalho_10_dias mvrd
        """,
        dbEngine,
    )

def gerar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Dados")
    output.seek(0)
    return output.getvalue()
