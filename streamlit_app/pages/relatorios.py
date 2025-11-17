"""Geração de Relatórios"""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import (
    carregar_dados_principais, carregar_kpis_agregados,
    carregar_ranking_empresas, carregar_analise_produtos
)
from utils import exportar_dataframe_excel, exportar_dataframe_csv
from datetime import datetime


def render():
    st.title("📄 Geração de Relatórios")
    st.markdown("Exportação de dados e relatórios personalizados")

    periodo_inicio = st.session_state.get('periodo_inicio', '2023-01')
    periodo_fim = st.session_state.get('periodo_fim', '2025-12')

    st.markdown("### 📥 Exportar Dados")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Dados Principais")
        if st.button("Exportar Dados Principais", use_container_width=True):
            with st.spinner("Gerando..."):
                df = carregar_dados_principais(periodo_inicio, periodo_fim, limit=10000)
                if df is not None and len(df) > 0:
                    excel = exportar_dataframe_excel(df, 'dados_principais.xlsx')
                    st.download_button(
                        "📥 Download Excel",
                        excel,
                        f"argos_dados_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("Sem dados")

    with col2:
        st.markdown("#### Ranking de Empresas")
        if st.button("Exportar Ranking", use_container_width=True):
            with st.spinner("Gerando..."):
                df = carregar_ranking_empresas(periodo_inicio, periodo_fim, 'extremas', 100)
                if df is not None and len(df) > 0:
                    csv = exportar_dataframe_csv(df)
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        f"argos_ranking_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
                else:
                    st.warning("Sem dados")

    st.markdown("---")

    st.markdown("### 📊 Relatório Consolidado")

    if st.button("Gerar Relatório Consolidado", use_container_width=True, type="primary"):
        with st.spinner("Gerando relatório consolidado..."):
            # Carregar todos os dados
            kpis = carregar_kpis_agregados(periodo_inicio, periodo_fim)
            df_ranking = carregar_ranking_empresas(periodo_inicio, periodo_fim, 'extremas', 50)
            df_produtos = carregar_analise_produtos(periodo_inicio, periodo_fim, 50)

            # Criar relatório
            st.success("✅ Relatório gerado com sucesso!")

            # Exibir resumo
            st.markdown("#### 📋 Resumo Executivo")

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Registros", f"{kpis.get('total_registros', 0):,.0f}")
            col2.metric("Total Empresas", f"{kpis.get('total_empresas', 0):,.0f}")
            col3.metric("Taxa Correção", f"{kpis.get('taxa_correcao', 0):.2f}%")

            # Downloads individuais
            st.markdown("#### 📥 Downloads")

            col1, col2, col3 = st.columns(3)

            with col1:
                if df_ranking is not None and len(df_ranking) > 0:
                    excel = exportar_dataframe_excel(df_ranking)
                    st.download_button(
                        "Ranking Empresas",
                        excel,
                        f"ranking_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        use_container_width=True
                    )

            with col2:
                if df_produtos is not None and len(df_produtos) > 0:
                    excel = exportar_dataframe_excel(df_produtos)
                    st.download_button(
                        "Análise Produtos",
                        excel,
                        f"produtos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        use_container_width=True
                    )

    st.markdown("---")

    st.markdown("""
    ### ℹ️ Informações sobre Exportação

    - **Formato Excel**: Inclui formatação e é ideal para análises no Excel
    - **Formato CSV**: Arquivo texto separado por ponto-e-vírgula, ideal para importação em outros sistemas
    - **Limite de Registros**: Por padrão, são exportados até 10.000 registros para otimizar performance
    - **Período**: Os dados exportados correspondem ao período selecionado nos filtros globais

    **Dica:** Para exportar dados de empresas específicas, use a página "Análise de Empresas"
    """)
