"""Sistema de Alertas Inteligente"""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import carregar_ranking_empresas
from analytics import calcular_score_risco, classificar_nivel_alerta
from visualizations import criar_grafico_alertas, criar_gauge_chart
from utils import obter_badge_alerta, formatar_numero, formatar_moeda
from config import ALERT_LEVELS


def render():
    st.title("🚨 Sistema de Alertas Inteligente")
    st.markdown("Priorização automática baseada em múltiplos critérios de risco")

    periodo_inicio = st.session_state.get('periodo_inicio', '2023-01')
    periodo_fim = st.session_state.get('periodo_fim', '2025-12')

    with st.spinner("Calculando scores de risco..."):
        df = carregar_ranking_empresas(periodo_inicio, periodo_fim, 'extremas', 100)

    if df is None or len(df) == 0:
        st.warning("Sem dados")
        return

    # Calcular scores
    df = calcular_score_risco(df)
    df['nivel_alerta'] = df['risk_score'].apply(classificar_nivel_alerta)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Empresas", formatar_numero(len(df)))
    col2.metric("Alertas Críticos", formatar_numero(len(df[df['nivel_alerta'].isin(['CRITICAL', 'EMERGENCY'])])))
    col3.metric("Score Médio", formatar_numero(df['risk_score'].mean(), 1))
    col4.metric("Score Máximo", formatar_numero(df['risk_score'].max(), 1))

    # Distribuição de alertas
    col1, col2 = st.columns([1, 2])

    with col1:
        fig = criar_grafico_alertas(df)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Top 10 maiores scores
        st.markdown("### 🔝 Top 10 Empresas por Score de Risco")
        df_top = df.nlargest(10, 'risk_score')[['cnpj_formatado', 'risk_score', 'nivel_alerta', 'extremas', 'bc_total']]

        # Adicionar badges de alerta
        df_display = df_top.copy()
        st.dataframe(
            df_display.style.background_gradient(subset=['risk_score'], cmap='RdYlGn_r'),
            use_container_width=True,
            height=400
        )

    # Lista priorizada
    st.markdown("### 📋 Lista Priorizada de Empresas")

    # Filtro por nível
    nivel_filtro = st.multiselect(
        "Filtrar por nível:",
        list(ALERT_LEVELS.keys()),
        default=list(ALERT_LEVELS.keys())
    )

    df_filtrado = df[df['nivel_alerta'].isin(nivel_filtro)].sort_values('risk_score', ascending=False)

    st.dataframe(
        df_filtrado[[
            'cnpj_formatado', 'risk_score', 'nivel_alerta',
            'total_casos', 'extremas', 'taxa_afastamento', 'bc_total'
        ]],
        use_container_width=True,
        height=500
    )

    # Download
    csv = df_filtrado.to_csv(index=False, sep=';', encoding='utf-8-sig')
    st.download_button("📥 Download Lista Priorizada", csv, "alertas.csv", "text/csv")
