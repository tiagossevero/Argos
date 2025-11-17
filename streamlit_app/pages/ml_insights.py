"""ML Insights - Machine Learning"""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import carregar_dados_principais
from analytics import (
    criar_clusters, detectar_outliers_isolation_forest,
    calcular_elbow_score
)
from visualizations import criar_scatter_plot
from utils import formatar_numero
import plotly.express as px


def render():
    st.title("🤖 ML Insights")
    st.markdown("Machine Learning para detecção de padrões e anomalias")

    periodo_inicio = st.session_state.get('periodo_inicio', '2023-01')
    periodo_fim = st.session_state.get('periodo_fim', '2025-12')

    with st.spinner("Carregando dados..."):
        df = carregar_dados_principais(periodo_inicio, periodo_fim, limit=5000)

    if df is None or len(df) == 0:
        st.warning("Sem dados")
        return

    tabs = st.tabs(["🎯 Clustering", "⚠️ Detecção de Anomalias"])

    with tabs[0]:
        st.markdown("### 🎯 Clustering (K-Means)")

        n_clusters = st.slider("Número de Clusters:", 2, 10, 5)

        colunas = ['tarifa_praticada', 'bc_total', 'diferenca_ia']
        df_clean = df[colunas].dropna()

        if len(df_clean) > 10:
            df_clustered = criar_clusters(df_clean.reset_index(), colunas, n_clusters)

            # Visualização
            fig = px.scatter_3d(
                df_clustered,
                x='tarifa_praticada',
                y='bc_total',
                z='diferenca_ia',
                color='cluster',
                title='Clusters 3D',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Distribuição de clusters
            dist = df_clustered['cluster'].value_counts()
            st.bar_chart(dist)
        else:
            st.warning("Dados insuficientes para clustering")

    with tabs[1]:
        st.markdown("### ⚠️ Detecção de Anomalias (Isolation Forest)")

        contamination = st.slider("Contaminação Esperada:", 0.01, 0.3, 0.1, 0.01)

        colunas = ['tarifa_praticada', 'bc_total', 'diferenca_ia']
        df_anomalias = detectar_outliers_isolation_forest(df, colunas, contamination)

        num_anomalias = df_anomalias['is_outlier'].sum()
        pct_anomalias = (num_anomalias / len(df_anomalias)) * 100

        col1, col2 = st.columns(2)
        col1.metric("Anomalias Detectadas", formatar_numero(num_anomalias))
        col2.metric("Percentual", f"{pct_anomalias:.2f}%")

        # Top anomalias
        df_top_anomalias = df_anomalias[df_anomalias['is_outlier']].nlargest(20, 'anomaly_score')

        if len(df_top_anomalias) > 0:
            st.markdown("#### 🔝 Top 20 Anomalias Mais Severas")
            st.dataframe(
                df_top_anomalias[['cnpj', 'produto', 'tarifa_praticada', 'bc_total', 'anomaly_score']],
                use_container_width=True
            )

            # Visualização
            fig = criar_scatter_plot(
                df_anomalias,
                'tarifa_praticada',
                'bc_total',
                'anomaly_score',
                'is_outlier',
                'Anomalias Detectadas (cor=outlier, tamanho=score)'
            )
            st.plotly_chart(fig, use_container_width=True)
