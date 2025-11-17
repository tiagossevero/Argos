"""
ARGOS - Sistema de Análise de Mudança de Comportamento Tributário
Aplicação Principal Streamlit
Versão 2.0 - Completamente Refatorada
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar diretório ao path
sys.path.append(str(Path(__file__).parent))

from config import MESSAGES, DESCRIPTIONS
from utils import check_password
from database import get_database_connection, limpar_cache

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="ARGOS - Análise Tributária",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.sef.sc.gov.br',
        'Report a bug': None,
        'About': "ARGOS v2.0 - Sistema de Análise de Mudança de Comportamento Tributário"
    }
)

# ============================================================================
# CSS CUSTOMIZADO
# ============================================================================

def aplicar_estilos():
    """Aplica estilos CSS customizados"""
    st.markdown("""
    <style>
    /* Tema Principal */
    .main {
        background-color: #f8f9fa;
    }

    /* Headers */
    h1 {
        color: #1f77b4;
        font-weight: 700;
        padding-bottom: 10px;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 20px;
    }

    h2 {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    h3 {
        color: #34495e;
        font-weight: 500;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    /* Cards de Métrica */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
    }

    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 500;
        color: #5a6c7d;
    }

    [data-testid="stMetricDelta"] {
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #2c3e50;
        padding-top: 20px;
    }

    [data-testid="stSidebar"] .element-container {
        color: white;
    }

    /* Botões */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        padding: 10px 20px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Tabelas */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Selectbox e Inputs */
    .stSelectbox, .stMultiSelect, .stTextInput {
        border-radius: 8px;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #ecf0f1;
        border-radius: 8px;
        font-weight: 600;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }

    /* Alertas */
    .stAlert {
        border-radius: 8px;
        border-left: 5px solid;
    }

    /* Footer */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #2c3e50;
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 0.85em;
        z-index: 999;
    }

    /* Ocultar elementos do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .element-container {
        animation: fadeIn 0.5s ease-in;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# NAVEGAÇÃO
# ============================================================================

def criar_sidebar():
    """Cria sidebar com navegação"""
    with st.sidebar:
        # Logo e título
        st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='color: white; margin: 0; font-size: 2.5em;'>🎯</h1>
            <h2 style='color: white; margin: 10px 0 0 0; font-size: 1.5em; border: none;'>ARGOS</h2>
            <p style='color: #95a5a6; margin: 5px 0; font-size: 0.9em;'>v2.0</p>
            <hr style='border: 1px solid #34495e; margin: 20px 0;'>
        </div>
        """, unsafe_allow_html=True)

        # Status da conexão
        db = get_database_connection()
        if db.test_connection():
            st.success("✅ Conectado ao banco")
        else:
            st.error("❌ Erro na conexão")

        st.markdown("---")

        # Navegação
        st.markdown("<h3 style='color: white; border: none;'>📊 Navegação</h3>", unsafe_allow_html=True)

        paginas = {
            "🏠 Home": "home",
            "📈 Dashboard Executivo": "dashboard",
            "🏢 Análise de Empresas": "empresas",
            "📦 Análise de Produtos": "produtos",
            "🏭 Análise Setorial": "setorial",
            "📅 Análise Temporal": "temporal",
            "🚨 Sistema de Alertas": "alertas",
            "📊 Análises Estatísticas": "estatisticas",
            "🤖 ML Insights": "ml",
            "📄 Relatórios": "relatorios"
        }

        pagina_selecionada = st.radio(
            "Selecione uma página:",
            list(paginas.keys()),
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Filtros Globais
        st.markdown("<h3 style='color: white; border: none;'>⚙️ Filtros Globais</h3>", unsafe_allow_html=True)

        # Período
        col1, col2 = st.columns(2)
        with col1:
            ano_inicio = st.selectbox(
                "Ano Inicial",
                options=['2023', '2024', '2025'],
                index=0,
                key='ano_inicio_global'
            )
            mes_inicio = st.selectbox(
                "Mês Inicial",
                options=['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'],
                index=0,
                key='mes_inicio_global'
            )

        with col2:
            ano_fim = st.selectbox(
                "Ano Final",
                options=['2023', '2024', '2025'],
                index=2,
                key='ano_fim_global'
            )
            mes_fim = st.selectbox(
                "Mês Final",
                options=['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'],
                index=11,
                key='mes_fim_global'
            )

        periodo_inicio = f"{ano_inicio}-{mes_inicio}"
        periodo_fim = f"{ano_fim}-{mes_fim}"

        # Salvar no session state
        st.session_state['periodo_inicio'] = periodo_inicio
        st.session_state['periodo_fim'] = periodo_fim

        st.markdown("---")

        # Ações
        st.markdown("<h3 style='color: white; border: none;'>🔧 Ações</h3>", unsafe_allow_html=True)

        if st.button("🔄 Limpar Cache", use_container_width=True):
            limpar_cache()
            st.success("Cache limpo!")
            st.rerun()

        if st.button("🚪 Sair", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")

        # Informações
        st.markdown("""
        <div style='color: #95a5a6; font-size: 0.8em; text-align: center;'>
            <p><strong>Sistema ARGOS</strong></p>
            <p>Receita Estadual - SC</p>
            <p>Desenvolvido por NIAT</p>
        </div>
        """, unsafe_allow_html=True)

        return paginas[pagina_selecionada]


# ============================================================================
# PÁGINAS
# ============================================================================

def pagina_home():
    """Página inicial com overview"""
    from pages import home
    home.render()


def pagina_dashboard():
    """Dashboard executivo"""
    from pages import dashboard_executivo
    dashboard_executivo.render()


def pagina_empresas():
    """Análise de empresas"""
    from pages import analise_empresas
    analise_empresas.render()


def pagina_produtos():
    """Análise de produtos"""
    from pages import analise_produtos
    analise_produtos.render()


def pagina_setorial():
    """Análise setorial"""
    from pages import analise_setorial
    analise_setorial.render()


def pagina_temporal():
    """Análise temporal"""
    from pages import analise_temporal
    analise_temporal.render()


def pagina_alertas():
    """Sistema de alertas"""
    from pages import sistema_alertas
    sistema_alertas.render()


def pagina_estatisticas():
    """Análises estatísticas"""
    from pages import analises_estatisticas
    analises_estatisticas.render()


def pagina_ml():
    """ML Insights"""
    from pages import ml_insights
    ml_insights.render()


def pagina_relatorios():
    """Relatórios"""
    from pages import relatorios
    relatorios.render()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Função principal"""
    # Aplicar estilos
    aplicar_estilos()

    # Verificar autenticação
    if not check_password():
        st.stop()

    # Criar sidebar e obter página selecionada
    pagina = criar_sidebar()

    # Roteamento
    paginas_funcoes = {
        'home': pagina_home,
        'dashboard': pagina_dashboard,
        'empresas': pagina_empresas,
        'produtos': pagina_produtos,
        'setorial': pagina_setorial,
        'temporal': pagina_temporal,
        'alertas': pagina_alertas,
        'estatisticas': pagina_estatisticas,
        'ml': pagina_ml,
        'relatorios': pagina_relatorios
    }

    # Renderizar página
    try:
        paginas_funcoes[pagina]()
    except Exception as e:
        st.error(f"Erro ao carregar página: {str(e)}")
        st.exception(e)

    # Footer
    st.markdown("""
    <div class='footer'>
        ARGOS v2.0 | Receita Estadual de Santa Catarina | Sistema de Análise de Comportamento Tributário
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
