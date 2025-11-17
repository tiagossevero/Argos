"""Análise de Empresas - Drill-down Detalhado"""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import carregar_ranking_empresas, carregar_detalhes_empresa
from utils import formatar_cnpj, formatar_moeda, formatar_numero, formatar_percentual
from visualizations import criar_grafico_evolucao_empresa, criar_grafico_barras
from analytics import calcular_score_risco, classificar_nivel_alerta


def render():
    """Renderiza Análise de Empresas"""
    st.title("🏢 Análise de Empresas")
    st.markdown("Análise detalhada por empresa com drill-down completo")

    periodo_inicio = st.session_state.get('periodo_inicio', '2023-01')
    periodo_fim = st.session_state.get('periodo_fim', '2025-12')

    tab1, tab2 = st.tabs(["🏆 Ranking de Empresas", "🔍 Drill-Down por Empresa"])

    with tab1:
        renderizar_ranking(periodo_inicio, periodo_fim)

    with tab2:
        renderizar_drilldown(periodo_inicio, periodo_fim)


def renderizar_ranking(periodo_inicio, periodo_fim):
    """Renderiza ranking de empresas"""
    st.markdown("### 🏆 Ranking de Empresas")

    col1, col2 = st.columns([2, 1])

    with col1:
        ordenar_por = st.selectbox(
            "Ordenar por:",
            ['extremas', 'afastou', 'bc_total', 'total_casos', 'volatilidade'],
            format_func=lambda x: {
                'extremas': 'Mudanças Extremas',
                'afastou': 'Afastamentos',
                'bc_total': 'Base de Cálculo',
                'total_casos': 'Total de Casos',
                'volatilidade': 'Volatilidade'
            }[x]
        )

    with col2:
        limite = st.number_input("Quantidade:", 10, 100, 50, 10)

    with st.spinner("Carregando ranking..."):
        df_ranking = carregar_ranking_empresas(periodo_inicio, periodo_fim, ordenar_por, limite)

    if df_ranking is None or len(df_ranking) == 0:
        st.warning("Sem dados")
        return

    # Calcular score de risco
    df_ranking = calcular_score_risco(df_ranking)
    df_ranking['nivel_alerta'] = df_ranking['risk_score'].apply(classificar_nivel_alerta)

    # Exibir tabela
    st.dataframe(
        df_ranking[[
            'cnpj_formatado', 'total_casos', 'extremas', 'aproximou', 'afastou',
            'taxa_correcao', 'bc_total', 'risk_score'
        ]].style.background_gradient(subset=['risk_score'], cmap='RdYlGn_r'),
        use_container_width=True,
        height=400
    )

    # Download
    csv = df_ranking.to_csv(index=False, sep=';', encoding='utf-8-sig')
    st.download_button(
        "📥 Download CSV",
        csv,
        "ranking_empresas.csv",
        "text/csv",
        use_container_width=False
    )


def renderizar_drilldown(periodo_inicio, periodo_fim):
    """Renderiza drill-down por empresa"""
    st.markdown("### 🔍 Análise Detalhada por Empresa")

    # Input CNPJ
    cnpj_input = st.text_input("Digite o CNPJ (apenas números):", max_chars=14)

    if not cnpj_input or len(cnpj_input) < 14:
        st.info("Digite um CNPJ para visualizar os detalhes")
        return

    with st.spinner("Carregando dados da empresa..."):
        df_empresa = carregar_detalhes_empresa(cnpj_input, periodo_inicio, periodo_fim)

    if df_empresa is None or len(df_empresa) == 0:
        st.warning(f"Sem dados para o CNPJ {formatar_cnpj(cnpj_input)}")
        return

    # Header da empresa
    st.markdown(f"## CNPJ: {formatar_cnpj(cnpj_input)}")

    # KPIs da empresa
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Casos", formatar_numero(len(df_empresa)))

    with col2:
        extremas = len(df_empresa[df_empresa['classificacao_mudanca'] == 'MUDANCA_EXTREMA'])
        st.metric("Mudanças Extremas", formatar_numero(extremas))

    with col3:
        bc_total = df_empresa['bc_total'].sum()
        st.metric("BC Total", formatar_moeda(bc_total))

    with col4:
        media_tarifa = df_empresa['tarifa_praticada'].mean()
        st.metric("Tarifa Média", formatar_numero(media_tarifa, 2) + "%")

    st.markdown("---")

    # Gráfico de evolução
    fig = criar_grafico_evolucao_empresa(df_empresa, cnpj_input)
    st.plotly_chart(fig, use_container_width=True)

    # Top produtos
    st.markdown("### 📦 Top Produtos da Empresa")

    df_produtos = df_empresa.groupby(['produto', 'gtin']).agg({
        'bc_total': 'sum',
        'cnpj': 'count'
    }).reset_index()
    df_produtos.columns = ['Produto', 'GTIN', 'BC Total', 'Casos']
    df_produtos = df_produtos.sort_values('BC Total', ascending=False).head(10)

    st.dataframe(df_produtos, use_container_width=True)

    # Detalhes completos
    with st.expander("📋 Ver Dados Detalhados"):
        st.dataframe(df_empresa, use_container_width=True, height=400)
