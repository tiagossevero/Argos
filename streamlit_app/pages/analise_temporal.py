"""Análise Temporal"""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import carregar_evolucao_temporal
from visualizations import criar_linha_temporal, criar_area_empilhada
from analytics import calcular_tendencia_linear, calcular_media_movel
from utils import formatar_numero
import pandas as pd


def render():
    st.title("📅 Análise Temporal")
    st.markdown("Evolução temporal e identificação de tendências")

    periodo_inicio = st.session_state.get('periodo_inicio', '2023-01')
    periodo_fim = st.session_state.get('periodo_fim', '2025-12')

    with st.spinner("Carregando evolução temporal..."):
        df = carregar_evolucao_temporal(periodo_inicio, periodo_fim)

    if df is None or len(df) == 0:
        st.warning("Sem dados")
        return

    # Adicionar média móvel
    df['ma_casos'] = calcular_media_movel(df, 'total_casos', janela=3)
    df['ma_taxa_correcao'] = calcular_media_movel(df, 'taxa_correcao', janela=3)

    # Tendência
    if len(df) >= 2:
        df['periodo_num'] = range(len(df))
        tendencia = calcular_tendencia_linear(df, 'periodo_num', 'total_casos')

        if tendencia:
            st.info(f"📈 Tendência: {tendencia.get('interpretacao', 'N/A')} | R² = {tendencia.get('r_squared', 0):.3f}")

    # Gráficos
    fig = criar_linha_temporal(
        df, 'periodo', ['total_casos', 'ma_casos'],
        'Evolução de Casos (com Média Móvel)', mostrar_tendencia=True
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        fig = criar_linha_temporal(
            df, 'periodo', ['extremas', 'significativas'],
            'Evolução de Mudanças por Tipo'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = criar_linha_temporal(
            df, 'periodo', ['taxa_correcao', 'ma_taxa_correcao'],
            'Taxa de Correção com Média Móvel'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Área empilhada
    fig = criar_area_empilhada(
        df, 'periodo', ['aproximou', 'afastou'],
        'Movimentos Tarifários ao Longo do Tempo'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela
    st.dataframe(df[['periodo', 'total_casos', 'empresas', 'extremas', 'taxa_correcao', 'bc_total']], use_container_width=True)
