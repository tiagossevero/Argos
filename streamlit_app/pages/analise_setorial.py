"""Análise Setorial"""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import carregar_analise_setorial
from visualizations import criar_grafico_barras, criar_treemap
from utils import formatar_numero, formatar_percentual


def render():
    st.title("🏭 Análise Setorial")
    st.markdown("Análise comparativa por setor (NCM 2 dígitos)")

    periodo_inicio = st.session_state.get('periodo_inicio', '2023-01')
    periodo_fim = st.session_state.get('periodo_fim', '2025-12')

    with st.spinner("Carregando análise setorial..."):
        df = carregar_analise_setorial(periodo_inicio, periodo_fim)

    if df is None or len(df) == 0:
        st.warning("Sem dados")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Setores", formatar_numero(len(df)))
    col2.metric("Taxa Correção Média", formatar_percentual(df['taxa_correcao'].mean()))
    col3.metric("Taxa Extremas Média", formatar_percentual(df['taxa_extremas'].mean()))

    # Gráficos comparativos
    col1, col2 = st.columns(2)

    with col1:
        fig = criar_grafico_barras(
            df.head(15), 'ncm_2dig', 'total_casos',
            'Top 15 Setores por Volume', mostrar_valores=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = criar_grafico_barras(
            df.nlargest(15, 'taxa_extremas'), 'ncm_2dig', 'taxa_extremas',
            'Top 15 Setores por Taxa de Extremas (%)', mostrar_valores=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # Treemap
    if len(df) > 0:
        fig = criar_treemap(df, ['ncm_2dig'], 'bc_total', 'Distribuição de BC por Setor')
        st.plotly_chart(fig, use_container_width=True)

    # Tabela completa
    st.dataframe(df, use_container_width=True, height=400)
