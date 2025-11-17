"""Análises Estatísticas Avançadas"""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import carregar_dados_principais
from analytics import (
    calcular_matriz_correlacao, calcular_estatisticas_descritivas,
    detectar_outliers_iqr, teste_normalidade
)
from visualizations import criar_heatmap_correlacao, criar_histograma, criar_boxplot
from utils import formatar_numero


def render():
    st.title("📊 Análises Estatísticas Avançadas")
    st.markdown("Correlações, distribuições e testes estatísticos")

    periodo_inicio = st.session_state.get('periodo_inicio', '2023-01')
    periodo_fim = st.session_state.get('periodo_fim', '2025-12')

    with st.spinner("Carregando dados..."):
        df = carregar_dados_principais(periodo_inicio, periodo_fim, limit=5000)

    if df is None or len(df) == 0:
        st.warning("Sem dados")
        return

    tabs = st.tabs(["📈 Estatísticas Descritivas", "🔗 Correlações", "📊 Distribuições", "🎯 Outliers"])

    with tabs[0]:
        st.markdown("### 📈 Estatísticas Descritivas")
        coluna = st.selectbox("Selecione a variável:", ['tarifa_praticada', 'bc_total', 'diferenca_ia'])
        stats = calcular_estatisticas_descritivas(df, coluna)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Média", formatar_numero(stats.get('media', 0), 2))
        col2.metric("Mediana", formatar_numero(stats.get('mediana', 0), 2))
        col3.metric("Desvio Padrão", formatar_numero(stats.get('desvio_padrao', 0), 2))
        col4.metric("Coef. Variação", formatar_numero(stats.get('coef_variacao', 0), 2) + "%")

        st.json(stats)

    with tabs[1]:
        st.markdown("### 🔗 Matriz de Correlação")
        colunas_num = ['tarifa_praticada', 'tarifa_media_historica', 'tarifa_ia', 'bc_total', 'diferenca_ia']
        corr = calcular_matriz_correlacao(df, colunas_num)

        if not corr.empty:
            fig = criar_heatmap_correlacao(corr)
            st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        st.markdown("### 📊 Distribuições")
        coluna = st.selectbox("Variável:", ['tarifa_praticada', 'bc_total', 'diferenca_ia'], key='dist')
        fig = criar_histograma(df, coluna, bins=30, mostrar_curva_normal=True)
        st.plotly_chart(fig, use_container_width=True)

        # Teste de normalidade
        teste = teste_normalidade(df, coluna)
        if 'p_valor' in teste:
            st.info(f"Teste de Normalidade: {teste['interpretacao']} (p-valor: {teste['p_valor']:.4f})")

    with tabs[3]:
        st.markdown("### 🎯 Detecção de Outliers")
        coluna = st.selectbox("Variável:", ['tarifa_praticada', 'bc_total'], key='out')
        df_out = detectar_outliers_iqr(df, coluna)

        num_outliers = df_out['is_outlier'].sum()
        pct_outliers = (num_outliers / len(df_out)) * 100

        st.metric("Outliers Detectados", f"{num_outliers} ({pct_outliers:.1f}%)")

        fig = criar_boxplot(df, coluna, titulo=f"Boxplot - {coluna}")
        st.plotly_chart(fig, use_container_width=True)
