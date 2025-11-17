"""Página Home - Overview do Sistema"""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import carregar_kpis_agregados, carregar_evolucao_temporal
from utils import formatar_moeda, formatar_numero, formatar_percentual, exibir_metrica_customizada
from visualizations import criar_grafico_pizza, criar_linha_temporal
import pandas as pd


def render():
    """Renderiza página Home"""
    st.title("🏠 ARGOS - Sistema de Análise de Comportamento Tributário")

    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px;'>
        <h2 style='margin: 0; color: white; border: none;'>Bem-vindo ao ARGOS v2.0</h2>
        <p style='margin: 10px 0 0 0; font-size: 1.1em;'>
            Sistema Inteligente de Monitoramento de Mudanças de Comportamento Tributário
        </p>
        <p style='margin: 10px 0 0 0; opacity: 0.9;'>
            Detecte anomalias, identifique padrões e tome decisões baseadas em dados
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Obter período dos filtros globais
    periodo_inicio = st.session_state.get('periodo_inicio', '2023-01')
    periodo_fim = st.session_state.get('periodo_fim', '2025-12')

    # Carregar KPIs
    with st.spinner("Carregando indicadores..."):
        kpis = carregar_kpis_agregados(periodo_inicio, periodo_fim)

    if not kpis:
        st.warning("Nenhum dado disponível para o período selecionado.")
        return

    # KPIs Principais
    st.markdown("### 📊 Indicadores Principais")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total de Registros",
            formatar_numero(kpis.get('total_registros', 0)),
            help="Total de casos analisados no período"
        )

    with col2:
        st.metric(
            "Empresas Monitoradas",
            formatar_numero(kpis.get('total_empresas', 0)),
            help="Quantidade de empresas distintas"
        )

    with col3:
        st.metric(
            "Taxa de Correção",
            formatar_percentual(kpis.get('taxa_correcao', 0)),
            help="Percentual de casos que aproximaram da tarifa correta"
        )

    with col4:
        st.metric(
            "Base de Cálculo Total",
            formatar_moeda(kpis.get('bc_total', 0)),
            help="Soma total da base de cálculo do ICMS"
        )

    st.markdown("---")

    # Segunda linha de KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Mudanças Extremas",
            formatar_numero(kpis.get('extremas', 0)),
            delta=f"{formatar_percentual(kpis.get('taxa_extremas', 0))} do total",
            help="Casos com mudança extrema de comportamento"
        )

    with col2:
        st.metric(
            "Mudanças Significativas",
            formatar_numero(kpis.get('significativas', 0)),
            help="Casos com mudança significativa"
        )

    with col3:
        st.metric(
            "Aproximou da Correta",
            formatar_numero(kpis.get('aproximou', 0)),
            help="Casos que melhoraram em relação à tarifa IA"
        )

    with col4:
        st.metric(
            "Afastou da Correta",
            formatar_numero(kpis.get('afastou', 0)),
            help="Casos que pioraram em relação à tarifa IA"
        )

    st.markdown("---")

    # Evolução Temporal
    st.markdown("### 📈 Evolução Temporal")

    with st.spinner("Carregando evolução temporal..."):
        df_evolucao = carregar_evolucao_temporal(periodo_inicio, periodo_fim)

    if df_evolucao is not None and len(df_evolucao) > 0:
        col1, col2 = st.columns(2)

        with col1:
            fig = criar_linha_temporal(
                df_evolucao,
                'periodo',
                ['total_casos'],
                'Total de Casos por Período',
                mostrar_tendencia=True
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = criar_linha_temporal(
                df_evolucao,
                'periodo',
                ['taxa_correcao'],
                'Taxa de Correção por Período (%)',
                mostrar_tendencia=True
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Informações e Recursos
    st.markdown("### 🎯 Recursos do Sistema")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='background-color: #e3f2fd; padding: 20px; border-radius: 10px;
                    border-left: 5px solid #2196f3;'>
            <h4 style='color: #1976d2; margin-top: 0;'>📊 Dashboards Interativos</h4>
            <p>Visualizações avançadas com Plotly para análise exploratória completa</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background-color: #f3e5f5; padding: 20px; border-radius: 10px;
                    border-left: 5px solid #9c27b0;'>
            <h4 style='color: #7b1fa2; margin-top: 0;'>🤖 Machine Learning</h4>
            <p>Detecção automática de padrões e anomalias com algoritmos avançados</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='background-color: #e8f5e9; padding: 20px; border-radius: 10px;
                    border-left: 5px solid #4caf50;'>
            <h4 style='color: #388e3c; margin-top: 0;'>🚨 Alertas Inteligentes</h4>
            <p>Sistema de priorização automática baseado em múltiplos critérios</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Guia Rápido
    with st.expander("📘 Guia Rápido de Navegação"):
        st.markdown("""
        **Como usar o ARGOS:**

        1. **Dashboard Executivo**: Visão geral consolidada com gráficos e análises de alto nível
        2. **Análise de Empresas**: Rankings, drill-down detalhado e evolução por empresa
        3. **Análise de Produtos**: Identificação de produtos voláteis e com comportamento anômalo
        4. **Análise Setorial**: Comparação entre setores (NCM) e benchmarking
        5. **Análise Temporal**: Tendências, sazonalidades e previsões
        6. **Sistema de Alertas**: Priorização automática de casos críticos
        7. **Análises Estatísticas**: Correlações, distribuições e testes estatísticos
        8. **ML Insights**: Clustering, detecção de anomalias e padrões
        9. **Relatórios**: Exportação de dados em Excel e CSV

        **Filtros Globais:**
        Use a barra lateral para selecionar o período de análise. Os filtros serão aplicados em todas as páginas.

        **Performance:**
        O sistema usa cache inteligente para otimizar o carregamento.
        Use o botão "Limpar Cache" se precisar atualizar os dados.
        """)

    # Estatísticas Adicionais
    st.markdown("### 📌 Resumo Estatístico")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        **Período Analisado:** {periodo_inicio} a {periodo_fim}

        **Cobertura:**
        - Produtos Únicos: {formatar_numero(kpis.get('total_produtos', 0))}
        - Média de Diferença IA: {formatar_numero(kpis.get('media_diferenca_ia', 0), 2)}%
        - Média Tarifa Praticada: {formatar_numero(kpis.get('media_tarifa_praticada', 0), 2)}%
        """)

    with col2:
        # Calcular métricas derivadas
        total = kpis.get('total_registros', 0)
        if total > 0:
            pct_extremas = (kpis.get('extremas', 0) / total) * 100
            pct_significativas = (kpis.get('significativas', 0) / total) * 100
            pct_normais = 100 - pct_extremas - pct_significativas
        else:
            pct_extremas = pct_significativas = pct_normais = 0

        st.markdown(f"""
        **Distribuição de Classificações:**
        - Normal: {formatar_percentual(pct_normais)}
        - Significativa: {formatar_percentual(pct_significativas)}
        - Extrema: {formatar_percentual(pct_extremas)}
        """)
