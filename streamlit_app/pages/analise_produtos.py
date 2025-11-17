"""Análise de Produtos"""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import carregar_analise_produtos
from visualizations import criar_scatter_plot, criar_boxplot
from utils import formatar_numero, formatar_moeda


def render():
    st.title("📦 Análise de Produtos")
    st.markdown("Identificação de produtos com comportamento volátil e anômalo")

    periodo_inicio = st.session_state.get('periodo_inicio', '2023-01')
    periodo_fim = st.session_state.get('periodo_fim', '2025-12')

    with st.spinner("Carregando análise de produtos..."):
        df = carregar_analise_produtos(periodo_inicio, periodo_fim, limit=200)

    if df is None or len(df) == 0:
        st.warning("Sem dados")
        return

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Produtos", formatar_numero(len(df)))
    col2.metric("BC Total", formatar_moeda(df['bc_total'].sum()))
    col3.metric("Média Volatilidade", formatar_numero(df['desvio_padrao'].mean(), 2))
    col4.metric("Com Casos Extremos", formatar_numero(len(df[df['casos_extremos'] > 0])))

    # Scatter plot volatilidade
    st.markdown("### 📊 Análise de Volatilidade")
    fig = criar_scatter_plot(
        df, 'media_tarifa', 'desvio_padrao', 'bc_total', 'casos_extremos',
        'Volatilidade vs Tarifa Média (tamanho=BC, cor=extremos)'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Top produtos mais voláteis
    st.markdown("### 🔝 Top 20 Produtos Mais Voláteis")
    df_top = df.nlargest(20, 'desvio_padrao')[['produto', 'gtin', 'num_empresas', 'media_tarifa', 'desvio_padrao', 'coef_variacao', 'bc_total']]
    st.dataframe(df_top, use_container_width=True, height=400)
