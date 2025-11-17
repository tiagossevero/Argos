"""Dashboard Executivo - Visão Consolidada"""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import (
    carregar_dados_principais, carregar_kpis_agregados,
    carregar_evolucao_temporal, carregar_ranking_empresas
)
from utils import formatar_moeda, formatar_numero, formatar_percentual
from visualizations import (
    criar_grafico_classificacoes, criar_grafico_movimentos,
    criar_linha_temporal, criar_grafico_barras, criar_area_empilhada
)
import pandas as pd


def render():
    """Renderiza Dashboard Executivo"""
    st.title("📈 Dashboard Executivo")
    st.markdown("Visão consolidada para tomada de decisão estratégica")

    # Obter filtros
    periodo_inicio = st.session_state.get('periodo_inicio', '2023-01')
    periodo_fim = st.session_state.get('periodo_fim', '2025-12')

    # Abas
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Visão Geral",
        "📈 Tendências",
        "🏆 Rankings",
        "💰 Impacto Financeiro"
    ])

    with tab1:
        renderizar_visao_geral(periodo_inicio, periodo_fim)

    with tab2:
        renderizar_tendencias(periodo_inicio, periodo_fim)

    with tab3:
        renderizar_rankings(periodo_inicio, periodo_fim)

    with tab4:
        renderizar_impacto_financeiro(periodo_inicio, periodo_fim)


def renderizar_visao_geral(periodo_inicio, periodo_fim):
    """Renderiza visão geral"""
    st.markdown("### 📊 Visão Geral do Período")

    # Carregar dados
    with st.spinner("Carregando dados..."):
        df = carregar_dados_principais(periodo_inicio, periodo_fim, limit=10000)
        kpis = carregar_kpis_agregados(periodo_inicio, periodo_fim)

    if df is None or len(df) == 0:
        st.warning("Sem dados para o período selecionado")
        return

    # KPIs em destaque
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total de Casos",
            formatar_numero(kpis.get('total_registros', 0)),
            help="Total de registros analisados"
        )

    with col2:
        st.metric(
            "Empresas",
            formatar_numero(kpis.get('total_empresas', 0)),
            help="Empresas distintas monitoradas"
        )

    with col3:
        st.metric(
            "Taxa Correção",
            formatar_percentual(kpis.get('taxa_correcao', 0)),
            help="% que aproximou da tarifa correta"
        )

    with col4:
        st.metric(
            "Taxa Extremas",
            formatar_percentual(kpis.get('taxa_extremas', 0)),
            delta=f"{formatar_numero(kpis.get('extremas', 0))} casos",
            help="% de mudanças extremas"
        )

    with col5:
        st.metric(
            "Base Cálculo",
            formatar_moeda(kpis.get('bc_total', 0)),
            help="Soma da base de cálculo"
        )

    st.markdown("---")

    # Gráficos de distribuição
    col1, col2 = st.columns(2)

    with col1:
        if 'classificacao_mudanca' in df.columns:
            fig = criar_grafico_classificacoes(df)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 'movimento_tarifario' in df.columns:
            fig = criar_grafico_movimentos(df)
            st.plotly_chart(fig, use_container_width=True)

    # Análise por NCM (Top 10)
    st.markdown("### 🏭 Top 10 Setores (NCM 2 dígitos)")

    df_ncm = df.groupby('ncm_2dig').agg({
        'cnpj': 'count',
        'bc_total': 'sum'
    }).reset_index()
    df_ncm.columns = ['NCM', 'Casos', 'BC Total']
    df_ncm = df_ncm.sort_values('Casos', ascending=False).head(10)

    col1, col2 = st.columns(2)

    with col1:
        fig = criar_grafico_barras(
            df_ncm,
            'NCM',
            'Casos',
            'Top 10 Setores por Quantidade de Casos',
            mostrar_valores=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = criar_grafico_barras(
            df_ncm,
            'NCM',
            'BC Total',
            'Top 10 Setores por Base de Cálculo (R$)',
            mostrar_valores=False
        )
        st.plotly_chart(fig, use_container_width=True)


def renderizar_tendencias(periodo_inicio, periodo_fim):
    """Renderiza análise de tendências"""
    st.markdown("### 📈 Análise de Tendências Temporais")

    with st.spinner("Carregando evolução temporal..."):
        df_evolucao = carregar_evolucao_temporal(periodo_inicio, periodo_fim)

    if df_evolucao is None or len(df_evolucao) == 0:
        st.warning("Sem dados temporais")
        return

    # Gráfico de evolução de casos
    fig = criar_linha_temporal(
        df_evolucao,
        'periodo',
        ['total_casos', 'extremas'],
        'Evolução de Casos Totais e Extremos',
        mostrar_tendencia=True
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Taxa de correção ao longo do tempo
        fig = criar_linha_temporal(
            df_evolucao,
            'periodo',
            ['taxa_correcao'],
            'Evolução da Taxa de Correção (%)',
            mostrar_tendencia=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Base de cálculo ao longo do tempo
        fig = criar_linha_temporal(
            df_evolucao,
            'periodo',
            ['bc_total'],
            'Evolução da Base de Cálculo (R$)',
            mostrar_tendencia=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # Área empilhada de movimentos
    df_movimentos = df_evolucao[['periodo', 'aproximou', 'afastou']].copy()

    fig = criar_area_empilhada(
        df_movimentos,
        'periodo',
        ['aproximou', 'afastou'],
        'Evolução de Movimentos Tarifários (Empilhado)'
    )
    st.plotly_chart(fig, use_container_width=True)


def renderizar_rankings(periodo_inicio, periodo_fim):
    """Renderiza rankings"""
    st.markdown("### 🏆 Rankings de Empresas")

    # Seletor de métrica
    metrica = st.selectbox(
        "Ordenar por:",
        [
            ('extremas', 'Mudanças Extremas'),
            ('afastou', 'Afastamentos da Tarifa Correta'),
            ('bc_total', 'Base de Cálculo'),
            ('total_casos', 'Total de Casos'),
            ('volatilidade', 'Volatilidade')
        ],
        format_func=lambda x: x[1]
    )

    limit = st.slider("Quantidade de empresas:", 10, 100, 20, 10)

    with st.spinner("Carregando ranking..."):
        df_ranking = carregar_ranking_empresas(
            periodo_inicio,
            periodo_fim,
            order_by=metrica[0],
            limit=limit
        )

    if df_ranking is None or len(df_ranking) == 0:
        st.warning("Sem dados para ranking")
        return

    # Exibir ranking
    st.dataframe(
        df_ranking[[
            'cnpj_formatado', 'total_casos', 'extremas', 'significativas',
            'aproximou', 'afastou', 'taxa_correcao', 'bc_total'
        ]].rename(columns={
            'cnpj_formatado': 'CNPJ',
            'total_casos': 'Total Casos',
            'extremas': 'Extremas',
            'significativas': 'Significativas',
            'aproximou': 'Aproximou',
            'afastou': 'Afastou',
            'taxa_correcao': 'Taxa Correção (%)',
            'bc_total': 'Base Cálculo (R$)'
        }),
        use_container_width=True,
        height=500
    )

    # Top 10 em gráfico
    df_top10 = df_ranking.head(10)

    fig = criar_grafico_barras(
        df_top10,
        'cnpj_formatado',
        metrica[0],
        f'Top 10 Empresas - {metrica[1]}',
        orientacao='h',
        mostrar_valores=True
    )
    st.plotly_chart(fig, use_container_width=True)


def renderizar_impacto_financeiro(periodo_inicio, periodo_fim):
    """Renderiza análise de impacto financeiro"""
    st.markdown("### 💰 Análise de Impacto Financeiro")

    with st.spinner("Carregando dados..."):
        df = carregar_dados_principais(periodo_inicio, periodo_fim, limit=10000)
        kpis = carregar_kpis_agregados(periodo_inicio, periodo_fim)

    if df is None or len(df) == 0:
        st.warning("Sem dados")
        return

    # KPIs Financeiros
    col1, col2, col3 = st.columns(3)

    with col1:
        bc_total = kpis.get('bc_total', 0)
        st.metric(
            "Base de Cálculo Total",
            formatar_moeda(bc_total),
            help="Soma total da base de cálculo"
        )

    with col2:
        # Estimativa de impacto (diferença média * bc_total * alíquota média estimada)
        media_dif = kpis.get('media_diferenca_ia', 0)
        impacto_estimado = bc_total * (media_dif / 100) * 0.17  # Alíquota média de 17%
        st.metric(
            "Impacto Estimado",
            formatar_moeda(impacto_estimado),
            help="Estimativa de impacto fiscal (BC * dif_média * 17%)"
        )

    with col3:
        # BC de casos extremos
        df_extremos = df[df['classificacao_mudanca'] == 'MUDANCA_EXTREMA']
        bc_extremos = df_extremos['bc_total'].sum() if len(df_extremos) > 0 else 0
        st.metric(
            "BC de Casos Extremos",
            formatar_moeda(bc_extremos),
            help="Base de cálculo dos casos extremos"
        )

    st.markdown("---")

    # Análise por faixa de BC
    st.markdown("#### 📊 Distribuição por Faixa de Base de Cálculo")

    # Criar faixas
    df['faixa_bc'] = pd.cut(
        df['bc_total'],
        bins=[0, 1000, 10000, 100000, 1000000, float('inf')],
        labels=['< R$ 1k', 'R$ 1k-10k', 'R$ 10k-100k', 'R$ 100k-1M', '> R$ 1M']
    )

    df_faixas = df.groupby('faixa_bc').agg({
        'cnpj': 'count',
        'bc_total': 'sum'
    }).reset_index()
    df_faixas.columns = ['Faixa', 'Quantidade', 'BC Total']

    col1, col2 = st.columns(2)

    with col1:
        fig = criar_grafico_barras(
            df_faixas,
            'Faixa',
            'Quantidade',
            'Quantidade de Casos por Faixa de BC',
            mostrar_valores=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = criar_grafico_barras(
            df_faixas,
            'Faixa',
            'BC Total',
            'Base de Cálculo Total por Faixa (R$)',
            mostrar_valores=False
        )
        st.plotly_chart(fig, use_container_width=True)
