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

def get_pecas(dbEngine):
    """Retorna todas as pecas"""
    return pd.read_sql(
        """
        SELECT 
            DISTINCT "PRODUTO" AS "LABEL"
        FROM 
            pecas_gerais
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
    try:
    # Lista de OS
        with dbEngine.begin() as conn: 
            df = pd.read_sql("""
                SELECT DISTINCT
                    "MODELO" AS "MODELO"
                FROM pecas_gerais
            """, conn)
            return df
        
    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")
        raise

def get_modelos_pecas_odometro(dbEngine):
    # Lista de OS
    df = pd.read_sql(
        """
        SELECT DISTINCT
            "modelo_frota" AS "MODELO"
        FROM 
            mat_view_os_pecas_hodometro_v3
        """,
        dbEngine,
    )
    df = df.dropna(subset=["MODELO"])
    return df

def gerar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Dados")
    output.seek(0)
    return output.getvalue()
