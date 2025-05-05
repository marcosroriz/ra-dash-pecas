#!/usr/bin/env python
# coding: utf-8

# Funções utilitárias para construção das queries SQL


# Subqueries para filtrar as oficinas, seções e ordens de serviço quando TODAS não for selecionado
def subquery_oficinas(lista_oficinas, prefix="", termo_all="TODAS"):
    query = ""
    if termo_all not in lista_oficinas:
        query = f"""AND {prefix}"DESCRICAO DA OFICINA" IN ({', '.join([f"'{x}'" for x in lista_oficinas])})"""

    return query


def subquery_secoes(lista_secaos, prefix="", termo_all="TODAS"):
    query = ""
    if termo_all not in lista_secaos:
        query = f"""AND {prefix}"DESCRICAO DA SECAO" IN ({', '.join([f"'{x}'" for x in lista_secaos])})"""

    return query


def subquery_os(lista_os, prefix="", termo_all="TODAS"):
    if not lista_os or termo_all in lista_os:
        return ""
    valores = ", ".join([f"'{x}'" for x in lista_os if x])  
    if not valores:  
        return ""

    return f'AND {prefix}"DESCRICAO DO SERVICO" IN ({valores})'



def subquery_modelos(lista_modelos, prefix="", termo_all="TODAS"):
    query = ""
    if termo_all not in lista_modelos:
        query = f"""AND {prefix}"DESCRICAO DO MODELO" IN ({', '.join([f"'{x}'" for x in lista_modelos])})"""

    return query


def subquery_veiculos(lista_veiculos, prefix="", termo_all="TODAS"):
    query = ""
    if termo_all not in lista_veiculos:
        query = f"""AND {prefix}"CODIGO DO VEICULO" IN ({', '.join([f"'{x}'" for x in lista_veiculos])})"""

    return query

def subquery_equipamentos(lista_veiculos, prefix=""):
    query = ""
    if "TODAS" not in lista_veiculos:
        query = f"""AND {prefix}"EQUIPAMENTO" IN ({', '.join([f"'{x}'" for x in lista_veiculos])})"""
    return query

def subquery_modelos_veiculos(lista_modelos, prefix=""):
    #query = ""
    if not lista_modelos or "TODOS" in lista_modelos:
        return ""  # Não adiciona a cláusula IN se a lista estiver vazia ou for "TODOS":
    query = f"""AND {prefix}"DESCRICAO DO MODELO" IN ({', '.join([f"'{x}'" for x in lista_modelos])})"""
    return query

def subquery_modelos_pecas(lista_modelos, prefix=""):
    #query = ""
    if not lista_modelos or "TODOS" in lista_modelos:
        return ""  # Não adiciona a cláusula IN se a lista estiver vazia ou for "TODOS":
    query = f"""AND {prefix}"MODELO" IN ({', '.join([f"'{x}'" for x in lista_modelos])})"""
    return query

def subquery_modelos_combustivel(lista_modelos, prefix=""):
    #query = ""
    if not lista_modelos or "TODOS" in lista_modelos:
        return ""  # Não adiciona a cláusula IN se a lista estiver vazia ou for "TODOS":
    query = f"""AND {prefix} vec_model IN ({', '.join([f"'{x}'" for x in [lista_modelos]])})"""
    return query

def subquery_linha_combustivel(lista_linhas, prefix=""):
    #query = ""
    if not lista_linhas or "TODAS" in lista_linhas:
        return ""  # Não adiciona a cláusula IN se a lista estiver vazia ou for "TODOS":
    query = f"""AND {prefix} encontrou_numero_linha IN ({', '.join([f"'{x}'" for x in lista_linhas])})"""
    return query

def subquery_sentido_combustivel(sentido_linha, prefix=""):
    #query = ""
    if not sentido_linha or "IDA_VOLTA" in sentido_linha:
        return ""  # Não adiciona a cláusula IN se a lista estiver vazia ou for "TODOS":
    query = f"""AND {prefix} encontrou_numero_linha IN ({', '.join([f"'{x}'" for x in sentido_linha])})"""
    return query