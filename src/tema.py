#!/usr/bin/env python
# coding: utf-8

# Cores do plotly
import plotly.express as px

# Arquivo com icones e cores do tema
# Ícones
ICONE_INDICADOR_SUBINDO = "emojione-monotone:up-right-arrow"
ICONE_INDICADOR_DESCENDO = "emojione-monotone:down-right-arrow"
ICONE_INDICADOR_PADRAO = "pajamas:dash"
ICONE_INDICADOR_TAMANHO = "radix-icons:size"
ICONE_ESTRADA = "vaadin:road"
ICONE_MEDIA = "icon-park:average"
ICONE_ONIBUS = "mdi:bus"
ICONE_FROTA_ONIBUS = "mdi:bus-multiple"
ICONE_VIAGEM = "bx:trip"
ICONE_DUVIDA = "mingcute:question-fill"
ICONE_ERRO = "material-symbols:error"

# Fontes do Tema
FONTE_GRAFICOS = "Source Sans Pro"
FONTE_TAMANHO = 14

# Paleta de Cores: D3
# https://plotly.com/python/discrete-color/
# Tema alternativo: Pastel2 -- https://loading.io/color/feature/Pastel2-8/

PALETA_CORES = px.colors.qualitative.D3
PALETA_CORES_DISCRETA = px.colors.qualitative.D3
PALETA_CORES_SEQUENCIAL = px.colors.sequential.Plasma_r

# Cores Notáveis
COR_PADRAO = px.colors.qualitative.D3[0]
COR_SUCESSO = px.colors.qualitative.D3[2]
COR_ERRO = px.colors.qualitative.D3[3]
COR_ALERTA = px.colors.qualitative.D3[1]
