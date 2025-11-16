import streamlit as st
import hashlib

# DEFINA A SENHA AQUI
SENHA = "tsevero258"  # ← TROQUE para cada projeto

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("<div style='text-align: center; padding: 50px;'><h1>🔐 Acesso Restrito</h1></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            senha_input = st.text_input("Digite a senha:", type="password", key="pwd_input")
            if st.button("Entrar", use_container_width=True):
                if senha_input == SENHA:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta")
        st.stop()

check_password()

"""
Sistema ARGOSC - Análise de Mudança de Comportamento Tributário
Receita Estadual de Santa Catarina
Versão 1.0 - Dashboard Streamlit
"""

# =============================================================================
# 1. IMPORTS E CONFIGURAÇÕES INICIAIS
# =============================================================================

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import warnings
import ssl

# Hack SSL
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="ARGOS - Sistema de Monitoramento Tributário",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# 2. ESTILOS CSS
# =============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }

        /* ESTILO DOS KPIs - BORDA PRETA */
    div[data-testid="stMetric"] {
        background-color: #ffffff;        /* Fundo branco */
        border: 2px solid #2c3e50;        /* Borda: 2px de largura, sólida, cor cinza-escuro */
        border-radius: 10px;              /* Cantos arredondados (10 pixels de raio) */
        padding: 15px;                    /* Espaçamento interno (15px em todos os lados) */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);  /* Sombra: horizontal=0, vertical=2px, blur=4px, cor preta 10% opacidade */
    }
    
    /* Título do métrica */
    div[data-testid="stMetric"] > label {
        font-weight: 600;                 /* Negrito médio */
        color: #2c3e50;                   /* Cor do texto */
    }
    
    /* Valor do métrica */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;                /* Tamanho da fonte do valor */
        font-weight: bold;                /* Negrito */
        color: #1f77b4;                   /* Cor azul */
    }
    
    /* Delta (variação) */
    div[data-testid="stMetricDelta"] {
        font-size: 0.9rem;                /* Tamanho menor para delta */
        
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .alert-critico {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 10px;
        border-radius: 5px;
    }
    .alert-alto {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 10px;
        border-radius: 5px;
    }
    .alert-positivo {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 10px;
        border-radius: 5px;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 2.5. FUNÇÕES AUXILIARES
# =============================================================================

def formatar_cnpj(cnpj):
    """Formata CNPJ para garantir 14 dígitos com zeros à esquerda."""
    if pd.isna(cnpj):
        return None
    cnpj_str = str(cnpj).strip()
    # Remove pontos, barras e traços se houver
    cnpj_str = cnpj_str.replace('.', '').replace('/', '').replace('-', '')
    # Garante 14 dígitos
    return cnpj_str.zfill(14)

def formatar_cnpj_visualizacao(cnpj):
    """Formata CNPJ para visualização (XX.XXX.XXX/XXXX-XX)."""
    cnpj_limpo = formatar_cnpj(cnpj)
    if not cnpj_limpo or len(cnpj_limpo) != 14:
        return cnpj
    return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:14]}"
    
# =============================================================================
# 3. FUNÇÕES DE CONEXÃO E CARREGAMENTO DE DADOS (VERSÃO OTIMIZADA)
# =============================================================================

IMPALA_HOST = 'bdaworkernode02.sef.sc.gov.br'
IMPALA_PORT = 21050
DATABASE = 'niat'

# Suas credenciais (carregadas de forma segura)
IMPALA_USER = st.secrets["impala_credentials"]["user"]
IMPALA_PASSWORD = st.secrets["impala_credentials"]["password"]

@st.cache_resource
def get_impala_engine():
    """Cria e retorna engine Impala (compartilhado entre sessões)."""
    try:
        engine = create_engine(
            f'impala://{IMPALA_HOST}:{IMPALA_PORT}/{DATABASE}',
            connect_args={
                'user': IMPALA_USER,
                'password': IMPALA_PASSWORD,
                'auth_mechanism': 'LDAP',
                'use_ssl': True
            }
        )
        return engine
    except Exception as e:
        st.error(f"❌ Erro ao criar engine Impala: {e}")
        return None

@st.cache_data(ttl=3600)
def carregar_dados_agregados(_engine):
    """Carrega apenas dados agregados para carregamento rápido inicial."""
    dados = {}
    
    if _engine is None:
        st.sidebar.error("❌ Engine não disponível")
        return {}
    
    # Testar conexão
    try:
        connection = _engine.connect()
        st.sidebar.success("✅ Conexão com Impala estabelecida!")
        connection.close()
    except Exception as e:
        st.sidebar.error(f"❌ Falha ao conectar ao Impala: {str(e)[:100]}")
        return {}

    st.sidebar.write("📊 Carregando dados agregados...")
    
    try:
        # 1. AGREGAÇÃO GERAL POR PERÍODO
        st.sidebar.write("⏳ Agregação por período...")
        query_periodo = f"""
            SELECT 
                periodo,
                COUNT(*) as total_registros,
                COUNT(DISTINCT LPAD(CAST(cnpj_emitente AS STRING), 14, '0')) as total_empresas,
                COUNT(DISTINCT CONCAT(gtin, '-', ncm)) as total_produtos,
                SUM(bc_total_periodo) as bc_total,
                SUM(CASE WHEN classificacao_mudanca = 'MUDANCA_EXTREMA' THEN 1 ELSE 0 END) as extremas,
                SUM(CASE WHEN movimento_vs_ia = 'APROXIMOU_DA_CORRETA' THEN 1 ELSE 0 END) as aproximou,
                AVG(diferenca_vs_ia_periodo) as diff_media
            FROM {DATABASE}.argos_mudanca_comportamento
            WHERE periodo >= '202301'
            GROUP BY periodo
            ORDER BY periodo DESC
        """
        dados['agregado_periodo'] = pd.read_sql(query_periodo, _engine)
        st.sidebar.success(f"✅ Agregado por período ({len(dados['agregado_periodo'])} períodos)")
        
        # 2. AGREGAÇÃO POR EMPRESA (TOP 500)
        st.sidebar.write("⏳ Top empresas...")
        query_empresas = f"""
            SELECT 
                LPAD(CAST(cnpj_emitente AS STRING), 14, '0') as cnpj_emitente,
                MAX(nm_razao_social) as nm_razao_social,
                COUNT(*) as total_casos,
                SUM(bc_total_periodo) as bc_total,
                SUM(CASE WHEN classificacao_mudanca = 'MUDANCA_EXTREMA' THEN 1 ELSE 0 END) as extremas,
                SUM(CASE WHEN movimento_vs_ia = 'APROXIMOU_DA_CORRETA' THEN 1 ELSE 0 END) as aproximou,
                SUM(CASE WHEN movimento_vs_ia = 'AFASTOU_DA_CORRETA' THEN 1 ELSE 0 END) as afastou,
                AVG(diferenca_vs_ia_periodo) as diff_media
            FROM {DATABASE}.argos_mudanca_comportamento
            WHERE periodo >= '202301'
            GROUP BY LPAD(CAST(cnpj_emitente AS STRING), 14, '0')
            ORDER BY bc_total DESC
            LIMIT 500
        """
        dados['agregado_empresas'] = pd.read_sql(query_empresas, _engine)
        st.sidebar.success(f"✅ Top empresas ({len(dados['agregado_empresas'])} empresas)")
        
        # 3. AGREGAÇÃO POR SETOR (2 dígitos NCM)
        st.sidebar.write("⏳ Agregação setorial...")
        query_setor = f"""
            SELECT 
                SUBSTR(ncm, 1, 2) as setor_ncm,
                COUNT(*) as total_casos,
                COUNT(DISTINCT LPAD(CAST(cnpj_emitente AS STRING), 14, '0')) as total_empresas,
                SUM(bc_total_periodo) as bc_total,
                SUM(CASE WHEN classificacao_mudanca = 'MUDANCA_EXTREMA' THEN 1 ELSE 0 END) as extremas,
                SUM(CASE WHEN movimento_vs_ia = 'APROXIMOU_DA_CORRETA' THEN 1 ELSE 0 END) as aproximou
            FROM {DATABASE}.argos_mudanca_comportamento
            WHERE periodo >= '202301'
            GROUP BY SUBSTR(ncm, 1, 2)
            HAVING COUNT(*) >= 100
            ORDER BY extremas DESC
        """
        dados['agregado_setor'] = pd.read_sql(query_setor, _engine)
        st.sidebar.success(f"✅ Agregado setorial ({len(dados['agregado_setor'])} setores)")
        
        # 4. AGREGAÇÃO POR PRODUTO (TOP 500)
        st.sidebar.write("⏳ Top produtos...")
        query_produtos = f"""
            SELECT 
                gtin,
                ncm,
                MAX(descricao) as descricao,
                MAX(aliquota_ia) as aliquota_ia,
                COUNT(DISTINCT LPAD(CAST(cnpj_emitente AS STRING), 14, '0')) as qtd_empresas,
                AVG(aliq_emitente_periodo) as aliq_media,
                STDDEV(aliq_emitente_periodo) as aliq_desvio,
                MIN(aliq_emitente_periodo) as aliq_min,
                MAX(aliq_emitente_periodo) as aliq_max,
                SUM(bc_total_periodo) as bc_total,
                SUM(CASE WHEN classificacao_mudanca IN ('MUDANCA_EXTREMA', 'MUDANCA_SIGNIFICATIVA') THEN 1 ELSE 0 END) as mudancas_relevantes
            FROM {DATABASE}.argos_mudanca_comportamento
            WHERE periodo >= '202301'
            GROUP BY gtin, ncm
            HAVING COUNT(DISTINCT LPAD(CAST(cnpj_emitente AS STRING), 14, '0')) >= 3
            ORDER BY aliq_desvio DESC
            LIMIT 500
        """
        dados['agregado_produtos'] = pd.read_sql(query_produtos, _engine)
        st.sidebar.success(f"✅ Top produtos ({len(dados['agregado_produtos'])} produtos)")
        
        # 5. LISTA DE EMPRESAS PARA DROPDOWN
        st.sidebar.write("⏳ Lista de empresas...")
        query_lista_empresas = f"""
            SELECT DISTINCT 
                LPAD(CAST(cnpj_emitente AS STRING), 14, '0') as cnpj_emitente,
                nm_razao_social
            FROM {DATABASE}.argos_mudanca_comportamento
            WHERE periodo >= '202301'
            ORDER BY nm_razao_social
        """
        dados['lista_empresas'] = pd.read_sql(query_lista_empresas, _engine)
        st.sidebar.success(f"✅ Lista de empresas ({len(dados['lista_empresas'])} empresas)")
        
        # 6. DISTRIBUIÇÕES GERAIS
        st.sidebar.write("⏳ Distribuições...")
        query_distribuicoes = f"""
            SELECT 
                classificacao_mudanca,
                movimento_vs_ia,
                COUNT(*) as quantidade
            FROM {DATABASE}.argos_mudanca_comportamento
            WHERE periodo >= '202301'
            GROUP BY classificacao_mudanca, movimento_vs_ia
        """
        dados['distribuicoes'] = pd.read_sql(query_distribuicoes, _engine)
        st.sidebar.success(f"✅ Distribuições carregadas")
        
        # Converter tipos
        for key, df in dados.items():
            df.columns = [col.lower() for col in df.columns]
            for col in df.select_dtypes(include=['object']).columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
        
        st.sidebar.success("✅ Todos os dados agregados carregados!")
        
    except Exception as e:
        st.sidebar.error(f"❌ Erro no carregamento agregado: {str(e)[:200]}")
        import traceback
        st.sidebar.text(traceback.format_exc()[:500])
        
    return dados

@st.cache_data(ttl=1800)
def carregar_detalhes_empresa(_engine, cnpj_emitente):
    """Carrega detalhes completos de uma empresa específica sob demanda."""
    if _engine is None:
        return pd.DataFrame()
    
    # Garantir que CNPJ tenha 14 dígitos
    cnpj_formatado = formatar_cnpj(cnpj_emitente)
    
    try:
        query = f"""
            SELECT *
            FROM {DATABASE}.argos_mudanca_comportamento
            WHERE LPAD(CAST(cnpj_emitente AS STRING), 14, '0') = '{cnpj_formatado}'
            AND periodo >= '202301'
            ORDER BY periodo DESC
        """
        df = pd.read_sql(query, _engine)
        df.columns = [col.lower() for col in df.columns]
        
        # ✅ Garantir que periodo seja string
        if 'periodo' in df.columns:
            df['periodo'] = df['periodo'].astype(str)
        
        # Formatar CNPJ na saída
        if not df.empty and 'cnpj_emitente' in df.columns:
            df['cnpj_emitente'] = df['cnpj_emitente'].apply(formatar_cnpj)
        
        # Converter tipos
        for col in df.select_dtypes(include=['object']).columns:
            if col != 'periodo':  # Não converter periodo para numérico
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar detalhes da empresa: {str(e)[:100]}")
        import traceback
        st.text(traceback.format_exc()[:500])
        return pd.DataFrame()

@st.cache_data(ttl=1800)
def carregar_detalhes_periodo(_engine, periodo_inicio, periodo_fim, filtros):
    """Carrega detalhes de um período específico com filtros aplicados."""
    if _engine is None:
        return pd.DataFrame()
    
    try:
        # Construir WHERE clause
        where_clauses = [f"periodo >= '{periodo_inicio}'", f"periodo <= '{periodo_fim}'"]
        
        if filtros.get('classificacoes'):
            class_list = "', '".join(filtros['classificacoes'])
            where_clauses.append(f"classificacao_mudanca IN ('{class_list}')")
        
        if filtros.get('movimentos'):
            mov_list = "', '".join(filtros['movimentos'])
            where_clauses.append(f"movimento_vs_ia IN ('{mov_list}')")
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
            SELECT *
            FROM {DATABASE}.argos_mudanca_comportamento
            WHERE {where_clause}
            ORDER BY periodo DESC, bc_total_periodo DESC
            LIMIT 10000
        """
        
        df = pd.read_sql(query, _engine)
        df.columns = [col.lower() for col in df.columns]
        
        # Converter tipos
        for col in df.select_dtypes(include=['object']).columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar detalhes do período: {str(e)[:100]}")
        return pd.DataFrame()

@st.cache_data(ttl=1800)
def carregar_top_casos_criticos(_engine, limite=100):
    """Carrega os casos mais críticos para sistema de alertas."""
    if _engine is None:
        return pd.DataFrame()
    
    try:
        query = f"""
            SELECT 
                cnpj_emitente,
                nm_razao_social,
                periodo,
                gtin,
                ncm,
                descricao,
                bc_total_periodo,
                classificacao_mudanca,
                movimento_vs_ia,
                diferenca_vs_ia_periodo,
                aliq_emitente_periodo,
                aliquota_ia
            FROM {DATABASE}.argos_mudanca_comportamento
            WHERE classificacao_mudanca IN ('MUDANCA_EXTREMA', 'MUDANCA_SIGNIFICATIVA')
            AND movimento_vs_ia = 'AFASTOU_DA_CORRETA'
            AND periodo >= '202301'
            ORDER BY bc_total_periodo DESC
            LIMIT {limite}
        """
        
        df = pd.read_sql(query, _engine)
        df.columns = [col.lower() for col in df.columns]
        
        # Converter tipos
        for col in df.select_dtypes(include=['object']).columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar casos críticos: {str(e)[:100]}")
        return pd.DataFrame()

# =============================================================================
# 4. FUNÇÕES DE PROCESSAMENTO (VERSÃO OTIMIZADA)
# =============================================================================

def calcular_kpis_agregados(dados_agregados):
    """Calcula KPIs a partir dos dados agregados por período."""
    df_periodo = dados_agregados.get('agregado_periodo', pd.DataFrame())
    
    if df_periodo.empty:
        return {
            'total_registros': 0,
            'empresas': 0,
            'periodos': 0,
            'produtos': 0,
            'bc_total': 0.0,
            'taxa_correcao': 0.0,
            'aproximou': 0,
            'extremas': 0,
            'taxa_extremas': 0.0,
            'diff_media': 0.0
        }
    
    total_registros = int(df_periodo['total_registros'].sum())
    empresas = int(df_periodo['total_empresas'].max())  # Pegamos o máximo pois pode haver sobreposição
    periodos = len(df_periodo)
    produtos = int(df_periodo['total_produtos'].max())
    bc_total = float(df_periodo['bc_total'].sum())
    aproximou = int(df_periodo['aproximou'].sum())
    extremas = int(df_periodo['extremas'].sum())
    
    taxa_correcao = (aproximou / total_registros * 100) if total_registros > 0 else 0
    taxa_extremas = (extremas / total_registros * 100) if total_registros > 0 else 0
    diff_media = float(df_periodo['diff_media'].mean())
    
    return {
        'total_registros': total_registros,
        'empresas': empresas,
        'periodos': periodos,
        'produtos': produtos,
        'bc_total': bc_total,
        'taxa_correcao': taxa_correcao,
        'aproximou': aproximou,
        'extremas': extremas,
        'taxa_extremas': taxa_extremas,
        'diff_media': diff_media
    }

def get_evolucao_temporal_agregada(dados_agregados):
    """Retorna evolução temporal dos dados agregados."""
    df_periodo = dados_agregados.get('agregado_periodo', pd.DataFrame())
    
    if df_periodo.empty:
        return pd.DataFrame()
    
    evolucao = df_periodo.copy()
    evolucao['periodo_dt'] = pd.to_datetime(evolucao['periodo'], format='%Y%m')
    evolucao['taxa_correcao'] = (evolucao['aproximou'] / evolucao['total_registros'] * 100)
    
    evolucao = evolucao.rename(columns={
        'total_empresas': 'empresas',
        'total_registros': 'total_casos'
    })
    
    return evolucao

# =============================================================================
# 5. FUNÇÕES DE FILTROS (VERSÃO REFATORADA - FILTROS POR PÁGINA)
# =============================================================================

def criar_filtros_pagina(dados, pagina_nome):
    """Cria filtros no topo da página específica."""
    filtros = {}
    
    st.markdown("---")
    st.subheader("🔍 Filtros de Análise")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Filtro de período
    df_periodo = dados.get('agregado_periodo', pd.DataFrame())
    if not df_periodo.empty:
        # Garantir que periodos são strings
        periodos = sorted([str(p) for p in df_periodo['periodo'].unique()])
        
        with col1:
            filtros['periodo_inicio'] = st.selectbox(
                "📅 Período Inicial",
                periodos,
                index=0,
                key=f'periodo_inicio_{pagina_nome}'
            )
        
        with col2:
            filtros['periodo_fim'] = st.selectbox(
                "📅 Período Final",
                periodos,
                index=len(periodos)-1,
                key=f'periodo_fim_{pagina_nome}'
            )
    else:
        filtros['periodo_inicio'] = '202301'
        filtros['periodo_fim'] = '202412'
    
    # Filtro de classificação
    with col3:
        filtros['classificacoes'] = st.multiselect(
            "📊 Classificações",
            ['MUDANCA_EXTREMA', 'MUDANCA_SIGNIFICATIVA', 'COMPORTAMENTO_NORMAL', 'PRODUTO_ESTAVEL'],
            default=['MUDANCA_EXTREMA', 'MUDANCA_SIGNIFICATIVA'],
            key=f'classificacoes_{pagina_nome}'
        )
    
    # Filtro de movimento
    with col4:
        filtros['movimentos'] = st.multiselect(
            "🔄 Movimento vs IA",
            ['APROXIMOU_DA_CORRETA', 'AFASTOU_DA_CORRETA', 'MANTEVE_DISTANCIA'],
            default=['APROXIMOU_DA_CORRETA', 'AFASTOU_DA_CORRETA', 'MANTEVE_DISTANCIA'],
            key=f'movimentos_{pagina_nome}'
        )
    
    # Tema dos gráficos (apenas na sidebar)
    filtros['tema'] = st.session_state.get('tema_graficos', 'plotly_white')
    
    st.markdown("---")
    
    return filtros

def criar_filtros_sidebar_simples():
    """Cria apenas configurações visuais na sidebar."""
    with st.sidebar.expander("🎨 Configurações Visuais", expanded=False):
        tema = st.selectbox(
            "Tema dos Gráficos",
            ["plotly", "plotly_white", "plotly_dark"],
            index=1,
            key='tema_graficos_sidebar'
        )
        st.session_state['tema_graficos'] = tema
    
    return {'tema': tema}

def aplicar_filtros_agregados(dados, filtros):
    """Aplica filtros em todos os dados agregados e retorna cópia filtrada."""
    dados_filtrados = {}
    
    periodo_inicio = filtros.get('periodo_inicio')
    periodo_fim = filtros.get('periodo_fim')
    
    # 1. Filtrar agregado_periodo
    df_periodo = dados.get('agregado_periodo', pd.DataFrame())
    if not df_periodo.empty and periodo_inicio and periodo_fim:
        # Garantir que periodo no dataframe seja string para comparação
        df_periodo_copy = df_periodo.copy()
        df_periodo_copy['periodo'] = df_periodo_copy['periodo'].astype(str)
        
        df_periodo_filtrado = df_periodo_copy[
            (df_periodo_copy['periodo'] >= str(periodo_inicio)) &
            (df_periodo_copy['periodo'] <= str(periodo_fim))
        ].copy()
        dados_filtrados['agregado_periodo'] = df_periodo_filtrado
    else:
        dados_filtrados['agregado_periodo'] = df_periodo
    
    # 2. Manter outros dados (não dependem de filtros ou serão filtrados na página)
    dados_filtrados['agregado_empresas'] = dados.get('agregado_empresas', pd.DataFrame())
    dados_filtrados['agregado_produtos'] = dados.get('agregado_produtos', pd.DataFrame())
    dados_filtrados['agregado_setor'] = dados.get('agregado_setor', pd.DataFrame())
    dados_filtrados['lista_empresas'] = dados.get('lista_empresas', pd.DataFrame())
    dados_filtrados['distribuicoes'] = dados.get('distribuicoes', pd.DataFrame())
    
    return dados_filtrados
    
# =============================================================================
# 6. PÁGINAS DO DASHBOARD
# =============================================================================

def dashboard_executivo(dados, filtros_globais):
    """Dashboard executivo principal usando dados agregados."""
    st.markdown("<h1 class='main-header'>🎯 Dashboard Executivo ARGOS</h1>", unsafe_allow_html=True)
    
    # Criar filtros da página
    filtros = criar_filtros_pagina(dados, 'dashboard')
    
    # Aplicar filtros
    dados_filtrados = aplicar_filtros_agregados(dados, filtros)
    df_periodo_filtrado = dados_filtrados['agregado_periodo']
    
    if df_periodo_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
        return
    
    # KPIs dos dados filtrados
    kpis = calcular_kpis_agregados({'agregado_periodo': df_periodo_filtrado})
    
    st.subheader("📊 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Registros",
            f"{kpis.get('total_registros', 0):,}",
            help="Total de registros analisados"
        )
    
    with col2:
        st.metric(
            "Empresas Monitoradas",
            f"{kpis.get('empresas', 0):,}",
            help="Quantidade de empresas únicas"
        )
    
    with col3:
        st.metric(
            "Taxa de Correção",
            f"{kpis.get('taxa_correcao', 0):.1f}%",
            delta=f"{kpis.get('aproximou', 0):,} casos",
            help="Percentual de casos que aproximaram da alíquota correta"
        )
    
    with col4:
        st.metric(
            "Base de Cálculo Total",
            f"R$ {kpis.get('bc_total', 0)/1e6:.1f}M",
            help="Soma da base de cálculo de todos os registros"
        )
    
    # Segunda linha de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Produtos Distintos",
            f"{kpis.get('produtos', 0):,}",
            help="Quantidade de produtos únicos (GTIN + NCM)"
        )
    
    with col2:
        st.metric(
            "Mudanças Extremas",
            f"{kpis.get('extremas', 0):,}",
            delta=f"{kpis.get('taxa_extremas', 0):.1f}%",
            delta_color="inverse",
            help="Casos com mudança extrema de comportamento"
        )
    
    with col3:
        st.metric(
            "Períodos Analisados",
            f"{kpis.get('periodos', 0)}",
            help="Quantidade de meses analisados"
        )
    
    with col4:
        diff_media = kpis.get('diff_media', 0) * 100
        st.metric(
            "Diferença Média vs IA",
            f"{diff_media:+.2f}%",
            help="Diferença média entre alíquota praticada e IA"
        )
    
    # Gráficos
    st.subheader("📈 Análises Visuais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por classificação
        df_dist = dados.get('distribuicoes', pd.DataFrame())
        if not df_dist.empty:
            dist_class = df_dist.groupby('classificacao_mudanca')['quantidade'].sum().reset_index()
            dist_class.columns = ['Classificação', 'Quantidade']
            
            # Filtrar por classificações selecionadas
            if filtros.get('classificacoes'):
                dist_class = dist_class[dist_class['Classificação'].isin(filtros['classificacoes'])]
            
            if not dist_class.empty:
                fig_class = px.pie(
                    dist_class,
                    values='Quantidade',
                    names='Classificação',
                    title='Distribuição por Classificação',
                    template=filtros['tema'],
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_class, use_container_width=True)
    
    with col2:
        # Distribuição por movimento
        if not df_dist.empty:
            dist_mov = df_dist.groupby('movimento_vs_ia')['quantidade'].sum().reset_index()
            dist_mov.columns = ['Movimento', 'Quantidade']
            
            # Filtrar por movimentos selecionados
            if filtros.get('movimentos'):
                dist_mov = dist_mov[dist_mov['Movimento'].isin(filtros['movimentos'])]
            
            if not dist_mov.empty:
                fig_mov = px.bar(
                    dist_mov,
                    x='Quantidade',
                    y='Movimento',
                    orientation='h',
                    title='Distribuição por Movimento vs IA',
                    template=filtros['tema'],
                    color='Movimento',
                    color_discrete_map={
                        'APROXIMOU_DA_CORRETA': '#4caf50',
                        'MANTEVE_DISTANCIA': '#ff9800',
                        'AFASTOU_DA_CORRETA': '#f44336'
                    }
                )
                st.plotly_chart(fig_mov, use_container_width=True)
    
    # Evolução temporal
    st.subheader("📅 Evolução Temporal")
    
    evolucao = get_evolucao_temporal_agregada({'agregado_periodo': df_periodo_filtrado})
    
    if not evolucao.empty:
        fig_temporal = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Evolução de Casos e Empresas', 'Taxa de Correção ao Longo do Tempo'),
            vertical_spacing=0.15
        )
        
        # Gráfico 1: Casos
        fig_temporal.add_trace(
            go.Scatter(
                x=evolucao['periodo_dt'],
                y=evolucao['total_casos'],
                name='Total de Casos',
                line=dict(color='royalblue', width=2)
            ),
            row=1, col=1
        )
        
        fig_temporal.add_trace(
            go.Bar(
                x=evolucao['periodo_dt'],
                y=evolucao['empresas'],
                name='Empresas Ativas',
                marker_color='lightblue',
                opacity=0.6,
                yaxis='y2'
            ),
            row=1, col=1
        )
        
        # Gráfico 2: Taxa de correção
        fig_temporal.add_trace(
            go.Scatter(
                x=evolucao['periodo_dt'],
                y=evolucao['taxa_correcao'],
                name='Taxa de Correção (%)',
                line=dict(color='green', width=3),
                fill='tozeroy',
                fillcolor='rgba(76, 175, 80, 0.2)'
            ),
            row=2, col=1
        )
        
        fig_temporal.update_xaxes(title_text="Período", row=2, col=1)
        fig_temporal.update_yaxes(title_text="Quantidade", row=1, col=1)
        fig_temporal.update_yaxes(title_text="Taxa de Correção (%)", row=2, col=1)
        
        fig_temporal.update_layout(
            height=700,
            showlegend=True,
            template=filtros['tema']
        )
        
        st.plotly_chart(fig_temporal, use_container_width=True)

def ranking_empresas(dados, filtros_globais):
    """Ranking de empresas usando dados agregados."""
    st.markdown("<h1 class='main-header'>🏆 Ranking de Empresas</h1>", unsafe_allow_html=True)
    
    # Criar filtros da página
    filtros = criar_filtros_pagina(dados, 'ranking')
    
    df_empresas = dados.get('agregado_empresas', pd.DataFrame())
    
    if df_empresas.empty:
        st.error("⚠️ Dados não carregados.")
        return
    
    # Garantir formatação de CNPJ
    if 'cnpj_emitente' in df_empresas.columns:
        df_empresas['cnpj_emitente'] = df_empresas['cnpj_emitente'].apply(formatar_cnpj)
    
    st.subheader("🎛️ Configurações do Ranking")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metrica_rank = st.selectbox(
            "Ordenar por",
            ['Taxa de Correção', 'Mudanças Extremas', 'Base de Cálculo', 'Quantidade de Casos'],
            index=0,
            key='metrica_rank'
        )
    
    with col2:
        top_n = st.slider("Top N empresas", 10, 100, 20, 5, key='top_n_rank')
    
    with col3:
        ordem = st.radio("Ordem", ['Decrescente', 'Crescente'], index=0, key='ordem_rank')
    
    # Calcular ranking
    ranking = df_empresas.copy()
    ranking['taxa_correcao'] = (ranking['aproximou'] / ranking['total_casos'] * 100)
    
    # Formatar CNPJ para visualização
    ranking['cnpj_formatado'] = ranking['cnpj_emitente'].apply(formatar_cnpj_visualizacao)
    
    # Renomear colunas
    ranking = ranking.rename(columns={
        'cnpj_formatado': 'CNPJ',
        'nm_razao_social': 'Razão Social',
        'bc_total': 'BC Total',
        'extremas': 'Mudanças Extremas',
        'aproximou': 'Aproximou IA',
        'total_casos': 'Total Casos',
        'taxa_correcao': 'Taxa Correção (%)'
    })
    
    # Ordenar
    mapa_metrica = {
        'Taxa de Correção': 'Taxa Correção (%)',
        'Mudanças Extremas': 'Mudanças Extremas',
        'Base de Cálculo': 'BC Total',
        'Quantidade de Casos': 'Total Casos'
    }
    
    col_ordenacao = mapa_metrica[metrica_rank]
    ascending = (ordem == 'Crescente')
    
    ranking = ranking.sort_values(col_ordenacao, ascending=ascending).head(top_n)
    ranking.insert(0, 'Posição', range(1, len(ranking) + 1))
    
    # Exibir tabela
    st.subheader(f"📋 Top {top_n} Empresas por {metrica_rank}")
    st.dataframe(
        ranking[['Posição', 'CNPJ', 'Razão Social', 'BC Total', 'Mudanças Extremas', 
                 'Aproximou IA', 'Total Casos', 'Taxa Correção (%)']].style.format({
            'BC Total': 'R$ {:,.2f}',
            'Taxa Correção (%)': '{:.1f}%'
        }),
        use_container_width=True,
        height=600
    )
    
    # Gráfico
    fig_ranking = px.bar(
        ranking.head(15),
        x=col_ordenacao,
        y='Razão Social',
        orientation='h',
        title=f'Top 15: {metrica_rank}',
        template=filtros['tema'],
        color=col_ordenacao,
        color_continuous_scale='RdYlGn' if metrica_rank == 'Taxa de Correção' else 'Reds'
    )
    
    st.plotly_chart(fig_ranking, use_container_width=True)

def analise_produtos(dados, filtros_globais):
    """Análise de produtos voláteis usando dados agregados."""
    st.markdown("<h1 class='main-header'>📦 Análise de Produtos</h1>", unsafe_allow_html=True)
    
    # Criar filtros da página
    filtros = criar_filtros_pagina(dados, 'produtos')
    
    produtos_vol = dados.get('agregado_produtos', pd.DataFrame())
    
    if produtos_vol.empty:
        st.error("⚠️ Dados não carregados.")
        return
    
    st.subheader("🔍 Produtos com Maior Volatilidade")
    
    # Filtro adicional
    col1, col2 = st.columns(2)
    with col1:
        min_empresas = st.slider("Mínimo de empresas", 3, 20, 5, key='min_empresas_prod')
    with col2:
        top_produtos = st.slider("Top N produtos", 10, 100, 30, 5, key='top_produtos')
    
    # Filtrar por mínimo de empresas
    produtos_vol = produtos_vol[produtos_vol['qtd_empresas'] >= min_empresas]
    
    # Ordenar por desvio
    produtos_vol = produtos_vol.sort_values('aliq_desvio', ascending=False).head(top_produtos)
    
    # Exibir tabela
    st.dataframe(
        produtos_vol[[
            'descricao', 'ncm', 'gtin', 'qtd_empresas',
            'aliq_media', 'aliq_desvio', 'aliq_min', 'aliq_max',
            'bc_total', 'mudancas_relevantes'
        ]].style.format({
            'aliq_media': '{:.4f}',
            'aliq_desvio': '{:.4f}',
            'aliq_min': '{:.4f}',
            'aliq_max': '{:.4f}',
            'bc_total': 'R$ {:,.2f}'
        }),
        use_container_width=True,
        height=500
    )
    
    # Gráfico
    fig_vol = px.bar(
        produtos_vol.head(15),
        x='aliq_desvio',
        y='descricao',
        orientation='h',
        title='Top 15 Produtos por Desvio Padrão da Alíquota',
        template=filtros['tema'],
        color='aliq_desvio',
        color_continuous_scale='Reds'
    )
    
    st.plotly_chart(fig_vol, use_container_width=True)

def analise_setorial(dados, filtros_globais):
    """Análise setorial por NCM usando dados agregados."""
    st.markdown("<h1 class='main-header'>🏭 Análise Setorial</h1>", unsafe_allow_html=True)
    
    # Criar filtros da página
    filtros = criar_filtros_pagina(dados, 'setorial')
    
    setores = dados.get('agregado_setor', pd.DataFrame())
    
    if setores.empty:
        st.error("⚠️ Dados não carregados.")
        return
    
    # Calcular taxas
    setores['taxa_correcao'] = (setores['aproximou'] / setores['total_casos'] * 100)
    setores['taxa_extremas'] = (setores['extremas'] / setores['total_casos'] * 100)
    
    # Renomear
    setores = setores.rename(columns={
        'setor_ncm': 'Setor NCM',
        'total_empresas': 'Empresas',
        'bc_total': 'BC Total',
        'extremas': 'Mudanças Extremas',
        'aproximou': 'Aproximou IA',
        'total_casos': 'Total Casos',
        'taxa_correcao': 'Taxa Correção (%)',
        'taxa_extremas': 'Taxa Extremas (%)'
    })
    
    # Filtro adicional
    top_setores = st.slider("Top N setores", 10, 50, 20, 5, key='top_setores')
    
    # Ordenar por taxa de extremas
    setores = setores.sort_values('Taxa Extremas (%)', ascending=False).head(top_setores)
    
    st.subheader(f"📊 Top {top_setores} Setores Críticos")
    
    # Exibir tabela
    st.dataframe(
        setores.style.format({
            'BC Total': 'R$ {:,.2f}',
            'Taxa Correção (%)': '{:.1f}%',
            'Taxa Extremas (%)': '{:.1f}%'
        }),
        use_container_width=True
    )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig_extremas = px.bar(
            setores.head(10),
            x='Taxa Extremas (%)',
            y='Setor NCM',
            orientation='h',
            title='Top 10 Setores por Taxa de Mudanças Extremas',
            template=filtros['tema'],
            color='Taxa Extremas (%)',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_extremas, use_container_width=True)
    
    with col2:
        fig_correcao = px.bar(
            setores.sort_values('Taxa Correção (%)', ascending=False).head(10),
            x='Taxa Correção (%)',
            y='Setor NCM',
            orientation='h',
            title='Top 10 Setores por Taxa de Correção',
            template=filtros['tema'],
            color='Taxa Correção (%)',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_correcao, use_container_width=True)

def drill_down_empresa(dados, filtros_globais):
    """Análise detalhada de uma empresa específica - carrega sob demanda."""
    st.markdown("<h1 class='main-header'>🔬 Análise Detalhada por Empresa</h1>", unsafe_allow_html=True)
    
    # Criar filtros da página (apenas tema)
    filtros = {'tema': filtros_globais.get('tema', 'plotly_white')}
    
    lista_empresas = dados.get('lista_empresas', pd.DataFrame())
    
    if lista_empresas.empty:
        st.error("⚠️ Lista de empresas não carregada.")
        return
    
    # Garantir que CNPJs estão formatados
    if 'cnpj_emitente' in lista_empresas.columns:
        lista_empresas['cnpj_emitente'] = lista_empresas['cnpj_emitente'].apply(formatar_cnpj)
    
    # Seleção da empresa
    st.subheader("🎯 Seleção da Empresa")
    
    lista_empresas = lista_empresas.sort_values('nm_razao_social')
    
    # Criar dicionário para lookup
    empresa_dict = dict(zip(lista_empresas['cnpj_emitente'], lista_empresas['nm_razao_social']))
    
    empresa_selecionada = st.selectbox(
        "Selecione a empresa:",
        lista_empresas['cnpj_emitente'].tolist(),
        format_func=lambda x: f"{formatar_cnpj_visualizacao(x)} - {empresa_dict.get(x, 'N/A')}",
        key='select_empresa_drill'
    )
    
    if not empresa_selecionada:
        st.info("Selecione uma empresa para análise.")
        return
    
    # Filtros de período para a empresa - USAR PERÍODOS DINÂMICOS
    st.markdown("---")
    
    # Obter períodos disponíveis dinamicamente
    df_periodo = dados.get('agregado_periodo', pd.DataFrame())
    if not df_periodo.empty:
        periodos_disponiveis = sorted([str(p) for p in df_periodo['periodo'].unique()])
    else:
        periodos_disponiveis = [
            '202301', '202302', '202303', '202304', '202305', '202306',
            '202307', '202308', '202309', '202310', '202311', '202312',
            '202401', '202402', '202403', '202404', '202405', '202406',
            '202407', '202408', '202409', '202410', '202411', '202412'
        ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        periodo_inicio_empresa = st.selectbox(
            "📅 Período Inicial (análise)",
            periodos_disponiveis,
            index=0,
            key='periodo_inicio_empresa'
        )
    
    with col2:
        periodo_fim_empresa = st.selectbox(
            "📅 Período Final (análise)",
            periodos_disponiveis,
            index=len(periodos_disponiveis)-1,
            key='periodo_fim_empresa'
        )
    
    st.markdown("---")
    
    # Botão para carregar detalhes
    if st.button("🔍 Carregar Análise Detalhada", type="primary"):
        with st.spinner(f'🔄 Carregando dados detalhados da empresa {formatar_cnpj_visualizacao(empresa_selecionada)}...'):
            engine = get_impala_engine()
            if engine is None:
                st.error("❌ Erro ao conectar ao banco de dados.")
                return
            
            df_empresa = carregar_detalhes_empresa(engine, empresa_selecionada)
        
        if df_empresa.empty:
            st.error("⚠️ Não foi possível carregar os dados da empresa.")
            st.info("💡 Possíveis causas: CNPJ não existe na base ou erro na consulta.")
            
            # Debug: tentar consulta simples
            try:
                cnpj_formatado = formatar_cnpj(empresa_selecionada)
                st.write(f"🔍 Debug - CNPJ formatado: {cnpj_formatado}")
                
                query_debug = f"""
                    SELECT COUNT(*) as total 
                    FROM {DATABASE}.argos_mudanca_comportamento 
                    WHERE LPAD(CAST(cnpj_emitente AS STRING), 14, '0') = '{cnpj_formatado}'
                """
                debug_result = pd.read_sql(query_debug, engine)
                st.write(f"📊 Total de registros encontrados: {debug_result['total'].iloc[0]}")
                
            except Exception as e:
                st.error(f"Erro na consulta debug: {str(e)}")
            return
        
        # ✅ CORREÇÃO: Garantir que periodo seja string antes da comparação
        df_empresa['periodo'] = df_empresa['periodo'].astype(str)
        
        # Filtrar por período selecionado
        df_empresa = df_empresa[
            (df_empresa['periodo'] >= str(periodo_inicio_empresa)) &
            (df_empresa['periodo'] <= str(periodo_fim_empresa))
        ]
        
        if df_empresa.empty:
            st.warning("⚠️ Nenhum dado encontrado para o período selecionado.")
            return
        
        razao_social = df_empresa['nm_razao_social'].iloc[0]
        
        st.markdown(f"### 🏢 {razao_social}")
        st.caption(f"CNPJ: {formatar_cnpj_visualizacao(empresa_selecionada)} | Período: {periodo_inicio_empresa} a {periodo_fim_empresa}")
        
        # KPIs da empresa
        st.subheader("📊 Indicadores da Empresa")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total de Registros",
                f"{len(df_empresa):,}"
            )
        
        with col2:
            produtos = df_empresa[['gtin', 'ncm']].drop_duplicates().shape[0]
            st.metric(
                "Produtos Distintos",
                f"{produtos:,}"
            )
        
        with col3:
            bc_total = float(df_empresa['bc_total_periodo'].sum())
            st.metric(
                "Base de Cálculo",
                f"R$ {bc_total/1e6:.1f}M"
            )
        
        with col4:
            taxa_corr = (df_empresa['movimento_vs_ia'] == 'APROXIMOU_DA_CORRETA').sum() / len(df_empresa) * 100
            st.metric(
                "Taxa de Correção",
                f"{taxa_corr:.1f}%"
            )
        
        # Evolução temporal da empresa
        st.subheader("📈 Evolução Temporal")
        
        evolucao_empresa = df_empresa.groupby('periodo').agg({
            'bc_total_periodo': 'sum',
            'classificacao_mudanca': lambda x: (x == 'MUDANCA_EXTREMA').sum(),
            'movimento_vs_ia': lambda x: (x == 'APROXIMOU_DA_CORRETA').sum()
        }).reset_index()
        
        evolucao_empresa['periodo_dt'] = pd.to_datetime(evolucao_empresa['periodo'], format='%Y%m')
        
        casos_periodo_emp = df_empresa.groupby('periodo').size().reset_index(name='total_casos')
        evolucao_empresa = evolucao_empresa.merge(casos_periodo_emp, on='periodo')
        evolucao_empresa['taxa_correcao'] = (evolucao_empresa['movimento_vs_ia'] / evolucao_empresa['total_casos'] * 100)
        
        fig_evolucao = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Base de Cálculo ao Longo do Tempo', 'Taxa de Correção Mensal'),
            vertical_spacing=0.15
        )
        
        fig_evolucao.add_trace(
            go.Bar(
                x=evolucao_empresa['periodo_dt'],
                y=evolucao_empresa['bc_total_periodo'],
                name='Base de Cálculo',
                marker_color='royalblue'
            ),
            row=1, col=1
        )
        
        fig_evolucao.add_trace(
            go.Scatter(
                x=evolucao_empresa['periodo_dt'],
                y=evolucao_empresa['taxa_correcao'],
                name='Taxa de Correção (%)',
                line=dict(color='green', width=3),
                fill='tozeroy'
            ),
            row=2, col=1
        )
        
        fig_evolucao.update_xaxes(title_text="Período", row=2, col=1)
        fig_evolucao.update_yaxes(title_text="Base de Cálculo (R$)", row=1, col=1)
        fig_evolucao.update_yaxes(title_text="Taxa de Correção (%)", row=2, col=1)
        
        fig_evolucao.update_layout(
            height=600,
            showlegend=True,
            template=filtros['tema']
        )
        
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        # Top produtos da empresa
        st.subheader("🏆 Top 10 Produtos")
        
        top_produtos = df_empresa.groupby(['descricao', 'ncm', 'gtin']).agg({
            'bc_total_periodo': 'sum',
            'classificacao_mudanca': lambda x: (x == 'MUDANCA_EXTREMA').sum(),
            'diferenca_vs_ia_periodo': 'mean'
        }).reset_index()
        
        top_produtos = top_produtos.sort_values('bc_total_periodo', ascending=False).head(10)
        top_produtos.columns = ['Descrição', 'NCM', 'GTIN', 'BC Total', 'Mudanças Extremas', 'Diff IA Média']
        
        st.dataframe(
            top_produtos.style.format({
                'BC Total': 'R$ {:,.2f}',
                'Diff IA Média': '{:+.2%}'
            }),
            use_container_width=True
        )
        
        # Distribuições
        col1, col2 = st.columns(2)
        
        with col1:
            dist_class_emp = df_empresa['classificacao_mudanca'].value_counts().reset_index()
            dist_class_emp.columns = ['Classificação', 'Quantidade']
            
            fig_class_emp = px.pie(
                dist_class_emp,
                values='Quantidade',
                names='Classificação',
                title='Distribuição por Classificação',
                template=filtros['tema']
            )
            st.plotly_chart(fig_class_emp, use_container_width=True)
        
        with col2:
            dist_mov_emp = df_empresa['movimento_vs_ia'].value_counts().reset_index()
            dist_mov_emp.columns = ['Movimento', 'Quantidade']
            
            fig_mov_emp = px.bar(
                dist_mov_emp,
                x='Quantidade',
                y='Movimento',
                orientation='h',
                title='Distribuição por Movimento',
                template=filtros['tema'],
                color='Movimento',
                color_discrete_map={
                    'APROXIMOU_DA_CORRETA': '#4caf50',
                    'MANTEVE_DISTANCIA': '#ff9800',
                    'AFASTOU_DA_CORRETA': '#f44336'
                }
            )
            st.plotly_chart(fig_mov_emp, use_container_width=True)

def comparativo_temporal(dados, filtros_globais):
    """Análise comparativa entre períodos usando dados agregados."""
    st.markdown("<h1 class='main-header'>⏱️ Análise Comparativa Temporal</h1>", unsafe_allow_html=True)
    
    # Criar filtros da página
    filtros = criar_filtros_pagina(dados, 'comparativo')
    
    # Aplicar filtros
    dados_filtrados = aplicar_filtros_agregados(dados, filtros)
    df_periodo = dados_filtrados['agregado_periodo']
    
    if df_periodo.empty:
        st.error("⚠️ Dados não carregados.")
        return
    
    # Dividir em períodos
    periodos = sorted(df_periodo['periodo'].unique())
    
    if len(periodos) < 6:
        st.warning("É necessário ter pelo menos 6 períodos para análise comparativa.")
        return
    
    # Primeiros 6 e últimos 6 períodos
    primeiros_6 = periodos[:6]
    ultimos_6 = periodos[-6:]
    
    df_inicial = df_periodo[df_periodo['periodo'].isin(primeiros_6)]
    df_final = df_periodo[df_periodo['periodo'].isin(ultimos_6)]
    
    st.subheader("📊 Comparativo: Período Inicial vs Período Final")
    
    # Calcular métricas
    metricas_inicial = {
        'casos': int(df_inicial['total_registros'].sum()),
        'empresas': int(df_inicial['total_empresas'].max()),
        'bc_total': float(df_inicial['bc_total'].sum()),
        'taxa_correcao': (df_inicial['aproximou'].sum() / df_inicial['total_registros'].sum() * 100) if df_inicial['total_registros'].sum() > 0 else 0,
        'taxa_extremas': (df_inicial['extremas'].sum() / df_inicial['total_registros'].sum() * 100) if df_inicial['total_registros'].sum() > 0 else 0
    }
    
    metricas_final = {
        'casos': int(df_final['total_registros'].sum()),
        'empresas': int(df_final['total_empresas'].max()),
        'bc_total': float(df_final['bc_total'].sum()),
        'taxa_correcao': (df_final['aproximou'].sum() / df_final['total_registros'].sum() * 100) if df_final['total_registros'].sum() > 0 else 0,
        'taxa_extremas': (df_final['extremas'].sum() / df_final['total_registros'].sum() * 100) if df_final['total_registros'].sum() > 0 else 0
    }
    
    # Exibir comparativo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📅 Período Inicial")
        st.caption(f"{primeiros_6[0]} a {primeiros_6[-1]}")
        st.metric("Casos", f"{metricas_inicial['casos']:,}")
        st.metric("Empresas", f"{metricas_inicial['empresas']:,}")
        st.metric("BC Total", f"R$ {metricas_inicial['bc_total']/1e6:.1f}M")
        st.metric("Taxa Correção", f"{metricas_inicial['taxa_correcao']:.1f}%")
        st.metric("Taxa Extremas", f"{metricas_inicial['taxa_extremas']:.1f}%")
    
    with col2:
        st.markdown("### 📈 Evolução")
        st.caption("Variação percentual")
        
        var_casos = ((metricas_final['casos'] - metricas_inicial['casos']) / metricas_inicial['casos'] * 100) if metricas_inicial['casos'] > 0 else 0
        st.metric("Casos", f"{var_casos:+.1f}%")
        
        var_empresas = ((metricas_final['empresas'] - metricas_inicial['empresas']) / metricas_inicial['empresas'] * 100) if metricas_inicial['empresas'] > 0 else 0
        st.metric("Empresas", f"{var_empresas:+.1f}%")
        
        var_bc = ((metricas_final['bc_total'] - metricas_inicial['bc_total']) / metricas_inicial['bc_total'] * 100) if metricas_inicial['bc_total'] > 0 else 0
        st.metric("BC Total", f"{var_bc:+.1f}%")
        
        var_corr = metricas_final['taxa_correcao'] - metricas_inicial['taxa_correcao']
        st.metric("Taxa Correção", f"{var_corr:+.1f} p.p.")
        
        var_ext = metricas_final['taxa_extremas'] - metricas_inicial['taxa_extremas']
        st.metric("Taxa Extremas", f"{var_ext:+.1f} p.p.", delta_color="inverse")
    
    with col3:
        st.markdown("### 📅 Período Final")
        st.caption(f"{ultimos_6[0]} a {ultimos_6[-1]}")
        st.metric("Casos", f"{metricas_final['casos']:,}")
        st.metric("Empresas", f"{metricas_final['empresas']:,}")
        st.metric("BC Total", f"R$ {metricas_final['bc_total']/1e6:.1f}M")
        st.metric("Taxa Correção", f"{metricas_final['taxa_correcao']:.1f}%")
        st.metric("Taxa Extremas", f"{metricas_final['taxa_extremas']:.1f}%")
    
    # Interpretação
    st.subheader("💡 Interpretação")
    
    if var_corr > 0:
        st.success(f"✅ A taxa de correção aumentou {var_corr:.1f} pontos percentuais, indicando melhoria no comportamento tributário.")
    else:
        st.warning(f"⚠️ A taxa de correção diminuiu {abs(var_corr):.1f} pontos percentuais.")
    
    if var_ext < 0:
        st.success(f"✅ A taxa de mudanças extremas reduziu {abs(var_ext):.1f} pontos percentuais, indicando maior estabilidade.")
    else:
        st.warning(f"⚠️ A taxa de mudanças extremas aumentou {var_ext:.1f} pontos percentuais.")

def sistema_alertas(dados, filtros_globais):
    """Sistema de alertas e priorização para fiscalização usando dados agregados."""
    st.markdown("<h1 class='main-header'>🚨 Sistema de Alertas</h1>", unsafe_allow_html=True)
    
    # Criar filtros da página
    filtros = criar_filtros_pagina(dados, 'alertas')
    
    df_empresas = dados.get('agregado_empresas', pd.DataFrame())
    
    if df_empresas.empty:
        st.error("⚠️ Dados não carregados.")
        return
    
    # Garantir formatação de CNPJ
    if 'cnpj_emitente' in df_empresas.columns:
        df_empresas['cnpj_emitente'] = df_empresas['cnpj_emitente'].apply(formatar_cnpj)
    
    st.subheader("⚙️ Configuração de Scoring")
    
    # Pesos para o score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        peso_classificacao = st.slider("Peso Classificação", 0, 50, 40, key='peso_class_alert')
    with col2:
        peso_movimento = st.slider("Peso Movimento", 0, 50, 30, key='peso_mov_alert')
    with col3:
        peso_magnitude = st.slider("Peso Magnitude", 0, 50, 20, key='peso_mag_alert')
    
    # Calcular score por empresa
    scoring = df_empresas.copy()
    
    # Componentes do score
    scoring['score_classificacao'] = (scoring['extremas'] / scoring['total_casos'] * 100) * (peso_classificacao / 100)
    scoring['score_movimento'] = (scoring['afastou'] / scoring['total_casos'] * 100) * (peso_movimento / 100)
    scoring['score_magnitude'] = scoring['diff_media'].abs() * 100 * (peso_magnitude / 100)
    
    # Score total
    scoring['score_total'] = scoring['score_classificacao'] + scoring['score_movimento'] + scoring['score_magnitude']
    
    # Formatar CNPJ para visualização
    scoring['cnpj_formatado'] = scoring['cnpj_emitente'].apply(formatar_cnpj_visualizacao)
    
    # Renomear colunas
    scoring = scoring.rename(columns={
        'cnpj_formatado': 'CNPJ',
        'nm_razao_social': 'Razão Social',
        'bc_total': 'BC Total',
        'extremas': 'Mudanças Extremas',
        'afastou': 'Afastou IA',
        'diff_media': 'Diff IA Média',
        'total_casos': 'Total Casos',
        'score_classificacao': 'Score Classificação',
        'score_movimento': 'Score Movimento',
        'score_magnitude': 'Score Magnitude',
        'score_total': 'Score Total'
    })
    
    # Criar coluna Nível Alerta
    scoring['Nível Alerta'] = pd.cut(
        scoring['Score Total'],
        bins=[0, 35, 50, 65, 80, 1000],
        labels=['BAIXO', 'MÉDIO', 'ALTO', 'CRÍTICO', 'EMERGENCIAL']
    )
    
    # Ordenar
    scoring = scoring.sort_values('Score Total', ascending=False)
    
    # Distribuição de alertas
    st.subheader("📊 Distribuição de Alertas")
    
    dist_alertas = scoring['Nível Alerta'].value_counts().reset_index()
    dist_alertas.columns = ['Nível', 'Quantidade']
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        for _, row in dist_alertas.iterrows():
            nivel = row['Nível']
            qtd = row['Quantidade']
            bc_nivel = scoring[scoring['Nível Alerta'] == nivel]['BC Total'].sum()
            
            if nivel == 'EMERGENCIAL':
                st.markdown(f"<div class='alert-critico'>🔴 <b>{nivel}</b>: {qtd} empresas | BC: R$ {bc_nivel/1e6:.1f}M</div>", unsafe_allow_html=True)
            elif nivel == 'CRÍTICO':
                st.markdown(f"<div class='alert-critico'>🟠 <b>{nivel}</b>: {qtd} empresas | BC: R$ {bc_nivel/1e6:.1f}M</div>", unsafe_allow_html=True)
            elif nivel == 'ALTO':
                st.markdown(f"<div class='alert-alto'>🟡 <b>{nivel}</b>: {qtd} empresas | BC: R$ {bc_nivel/1e6:.1f}M</div>", unsafe_allow_html=True)
            else:
                st.info(f"**{nivel}**: {qtd} empresas | BC: R$ {bc_nivel/1e6:.1f}M")
    
    with col2:
        fig_alertas = px.pie(
            dist_alertas,
            values='Quantidade',
            names='Nível',
            title='Distribuição por Nível de Alerta',
            template=filtros['tema'],
            color='Nível',
            color_discrete_map={
                'EMERGENCIAL': '#8b0000',
                'CRÍTICO': '#d62728',
                'ALTO': '#ff9800',
                'MÉDIO': '#ffdd70',
                'BAIXO': '#4caf50'
            }
        )
        st.plotly_chart(fig_alertas, use_container_width=True)
    
    # Top empresas prioritárias
    st.subheader("🎯 Top 20 Empresas Prioritárias para Fiscalização")
    
    top_priorizacao = scoring.head(20)
    
    st.dataframe(
        top_priorizacao[[
            'Razão Social', 'CNPJ', 'Nível Alerta', 'Score Total',
            'Mudanças Extremas', 'Afastou IA', 'BC Total'
        ]].style.format({
            'Score Total': '{:.1f}',
            'BC Total': 'R$ {:,.2f}'
        }).background_gradient(subset=['Score Total'], cmap='Reds'),
        use_container_width=True,
        height=600
    )
    
    # Gráfico de priorização
    fig_prior = px.scatter(
        scoring.head(100),
        x='Score Total',
        y='BC Total',
        color='Nível Alerta',
        size='Mudanças Extremas',
        hover_data=['Razão Social', 'Total Casos'],
        title='Matriz de Priorização: Score vs Impacto Financeiro',
        template=filtros['tema'],
        color_discrete_map={
            'EMERGENCIAL': '#8b0000',
            'CRÍTICO': '#d62728',
            'ALTO': '#ff9800',
            'MÉDIO': '#ffdd70',
            'BAIXO': '#4caf50'
        },
        log_y=True
    )
    
    st.plotly_chart(fig_prior, use_container_width=True)

# =============================================================================
# 7. FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    # Cabeçalho
    st.sidebar.title("🎯 Sistema ARGOS")
    st.sidebar.caption("Análise de Mudança de Comportamento Tributário")
    
    # Menu de navegação
    st.sidebar.markdown("---")
    st.sidebar.subheader("📑 Navegação")
    
    paginas = [
        "📊 Dashboard Executivo",
        "🏆 Ranking de Empresas",
        "📦 Análise de Produtos",
        "🏭 Análise Setorial",
        "🔬 Drill-Down Empresa",
        "⏱️ Comparativo Temporal",
        "🚨 Sistema de Alertas"
    ]
    
    pagina_selecionada = st.sidebar.radio(
        "Selecione uma página", 
        paginas,
        label_visibility="collapsed"
    )
    
    # Criar engine (cached)
    engine = get_impala_engine()
    
    if engine is None:
        st.error("❌ Não foi possível conectar ao banco de dados.")
        return
    
    # Carregar dados agregados com spinner
    with st.spinner('🔄 Conectando ao Impala e carregando dados agregados...'):
        dados = carregar_dados_agregados(engine)
    
    # Validação apropriada para dicionário
    if not isinstance(dados, dict) or len(dados) == 0 or dados.get('agregado_periodo') is None or dados.get('agregado_periodo').empty:
        st.error("❌ Falha no carregamento dos dados. Verifique a conexão com o banco de dados.")
        st.info("💡 Dica: Verifique suas credenciais em `st.secrets` e a conectividade com o servidor Impala.")
        return
    
    # Mostrar informações da base
    df_periodo = dados.get('agregado_periodo', pd.DataFrame())
    if not df_periodo.empty:
        total_registros = int(df_periodo['total_registros'].sum())
        st.sidebar.success(f"✅ {total_registros:,} registros (agregados)")
        periodo_min = df_periodo['periodo'].min()
        periodo_max = df_periodo['periodo'].max()
        st.sidebar.info(f"📅 Período: {periodo_min} até {periodo_max}")
    
    # Criar filtros simples na sidebar (apenas tema)
    filtros_globais = criar_filtros_sidebar_simples()
    
    # Roteamento de páginas
    paginas_funcoes = {
        "📊 Dashboard Executivo": dashboard_executivo,
        "🏆 Ranking de Empresas": ranking_empresas,
        "📦 Análise de Produtos": analise_produtos,
        "🏭 Análise Setorial": analise_setorial,
        "🔬 Drill-Down Empresa": drill_down_empresa,
        "⏱️ Comparativo Temporal": comparativo_temporal,
        "🚨 Sistema de Alertas": sistema_alertas
    }
    
    # Executar página selecionada
    try:
        paginas_funcoes[pagina_selecionada](dados, filtros_globais)
    except Exception as e:
        st.error(f"❌ Erro ao carregar a página: {str(e)}")
        st.exception(e)
    
    # Rodapé
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Sistema ARGOS v1.0 | Receita Estadual de Santa Catarina | "
        f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        "</div>",
        unsafe_allow_html=True
    )

# =============================================================================
# 8. EXECUÇÃO
# =============================================================================

if __name__ == "__main__":
    main()