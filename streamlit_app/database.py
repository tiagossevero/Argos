"""
ARGOS - Sistema de Análise de Mudança de Comportamento Tributário
Módulo de Conexão ao Banco de Dados e Cache
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any, List
from config import DATABASE_CONFIG, CACHE_CONFIG, QUERIES, PERFORMANCE_CONFIG

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Gerenciador de conexão com banco de dados Impala"""

    def __init__(self):
        self.engine = None
        self._initialize_connection()

    def _initialize_connection(self):
        """Inicializa conexão com o banco de dados"""
        try:
            # Tentar obter credenciais do secrets
            try:
                username = st.secrets["impala"]["username"]
                password = st.secrets["impala"]["password"]
            except:
                # Fallback para variáveis de ambiente ou padrão
                import os
                username = os.getenv('IMPALA_USER', 'default_user')
                password = os.getenv('IMPALA_PASSWORD', 'default_pass')

            # Criar connection string
            connection_string = (
                f"impala://{username}:{password}@"
                f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/"
                f"{DATABASE_CONFIG['database']}"
                f"?auth_mechanism={DATABASE_CONFIG['auth_mechanism']}"
            )

            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )

            logger.info("Conexão com banco de dados estabelecida com sucesso")

        except Exception as e:
            logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
            st.error(f"Erro na conexão: {str(e)}")
            self.engine = None

    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """
        Executa query e retorna DataFrame

        Args:
            query: SQL query para executar

        Returns:
            DataFrame com resultados ou None em caso de erro
        """
        if self.engine is None:
            st.error("Conexão com banco de dados não estabelecida")
            return None

        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(text(query), conn)
                logger.info(f"Query executada com sucesso. Registros: {len(df)}")
                return df

        except Exception as e:
            logger.error(f"Erro ao executar query: {str(e)}")
            st.error(f"Erro ao executar query: {str(e)}")
            return None

    def test_connection(self) -> bool:
        """Testa conexão com banco"""
        try:
            query = "SELECT 1 as test"
            result = self.execute_query(query)
            return result is not None and len(result) > 0
        except:
            return False


# Instância global de conexão
@st.cache_resource
def get_database_connection():
    """Retorna instância única de conexão (singleton com cache)"""
    return DatabaseConnection()


# ============================================================================
# FUNÇÕES DE CACHE DE DADOS
# ============================================================================

@st.cache_data(ttl=CACHE_CONFIG['dados_agregados_ttl'], max_entries=CACHE_CONFIG['max_entries'])
def carregar_dados_principais(periodo_inicio: str, periodo_fim: str, limit: int = None) -> pd.DataFrame:
    """
    Carrega dados principais com cache

    Args:
        periodo_inicio: Período inicial (formato YYYY-MM)
        periodo_fim: Período final (formato YYYY-MM)
        limit: Limite de registros (default: PERFORMANCE_CONFIG)

    Returns:
        DataFrame com dados principais
    """
    if limit is None:
        limit = PERFORMANCE_CONFIG['max_records_query']

    db = get_database_connection()

    query = QUERIES['dados_principais'].format(
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        limit=limit
    )

    df = db.execute_query(query)

    if df is not None and len(df) > 0:
        # Conversões e tratamentos
        df = _processar_dataframe(df)

    return df


@st.cache_data(ttl=CACHE_CONFIG['kpis_ttl'])
def carregar_kpis_agregados(periodo_inicio: str, periodo_fim: str) -> Dict[str, Any]:
    """
    Carrega KPIs agregados com cache

    Args:
        periodo_inicio: Período inicial
        periodo_fim: Período final

    Returns:
        Dicionário com KPIs
    """
    db = get_database_connection()

    query = QUERIES['kpis_agregados'].format(
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim
    )

    df = db.execute_query(query)

    if df is None or len(df) == 0:
        return {}

    # Converter primeira linha para dicionário
    kpis = df.iloc[0].to_dict()

    # Calcular métricas derivadas
    if kpis.get('aproximou', 0) + kpis.get('afastou', 0) > 0:
        kpis['taxa_correcao'] = (
            kpis.get('aproximou', 0) /
            (kpis.get('aproximou', 0) + kpis.get('afastou', 0)) * 100
        )
    else:
        kpis['taxa_correcao'] = 0

    if kpis.get('total_registros', 0) > 0:
        kpis['taxa_extremas'] = (
            kpis.get('extremas', 0) / kpis.get('total_registros', 0) * 100
        )
    else:
        kpis['taxa_extremas'] = 0

    return kpis


@st.cache_data(ttl=CACHE_CONFIG['detalhes_empresa_ttl'])
def carregar_ranking_empresas(
    periodo_inicio: str,
    periodo_fim: str,
    order_by: str = 'extremas',
    limit: int = 50
) -> pd.DataFrame:
    """
    Carrega ranking de empresas

    Args:
        periodo_inicio: Período inicial
        periodo_fim: Período final
        order_by: Campo para ordenação
        limit: Limite de registros

    Returns:
        DataFrame com ranking
    """
    db = get_database_connection()

    query = QUERIES['ranking_empresas'].format(
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        order_by=order_by,
        limit=limit
    )

    df = db.execute_query(query)

    if df is not None and len(df) > 0:
        # Calcular taxa de correção
        df['taxa_correcao'] = (
            df['aproximou'] / (df['aproximou'] + df['afastou'] + 0.001) * 100
        )

        # Calcular taxa de afastamento
        df['taxa_afastamento'] = (
            df['afastou'] / (df['aproximou'] + df['afastou'] + 0.001) * 100
        )

        # Formatar CNPJ
        df['cnpj_formatado'] = df['cnpj'].apply(formatar_cnpj)

    return df


@st.cache_data(ttl=CACHE_CONFIG['detalhes_empresa_ttl'])
def carregar_detalhes_empresa(cnpj: str, periodo_inicio: str, periodo_fim: str) -> pd.DataFrame:
    """
    Carrega detalhes de uma empresa específica

    Args:
        cnpj: CNPJ da empresa
        periodo_inicio: Período inicial
        periodo_fim: Período final

    Returns:
        DataFrame com detalhes da empresa
    """
    db = get_database_connection()

    query = QUERIES['detalhes_empresa'].format(
        cnpj=cnpj,
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim
    )

    df = db.execute_query(query)

    if df is not None:
        df = _processar_dataframe(df)

    return df


@st.cache_data(ttl=CACHE_CONFIG['detalhes_periodo_ttl'])
def carregar_evolucao_temporal(periodo_inicio: str, periodo_fim: str) -> pd.DataFrame:
    """
    Carrega evolução temporal agregada

    Args:
        periodo_inicio: Período inicial
        periodo_fim: Período final

    Returns:
        DataFrame com evolução temporal
    """
    db = get_database_connection()

    query = QUERIES['evolucao_temporal'].format(
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim
    )

    df = db.execute_query(query)

    if df is not None and len(df) > 0:
        # Converter período para datetime
        df['periodo_dt'] = pd.to_datetime(df['periodo'], format='%Y-%m')

        # Calcular taxa de correção
        df['taxa_correcao'] = (
            df['aproximou'] / (df['aproximou'] + df['afastou'] + 0.001) * 100
        )

        # Ordenar por período
        df = df.sort_values('periodo')

    return df


@st.cache_data(ttl=CACHE_CONFIG['detalhes_periodo_ttl'])
def carregar_analise_produtos(
    periodo_inicio: str,
    periodo_fim: str,
    limit: int = 100
) -> pd.DataFrame:
    """
    Carrega análise de produtos

    Args:
        periodo_inicio: Período inicial
        periodo_fim: Período final
        limit: Limite de registros

    Returns:
        DataFrame com análise de produtos
    """
    db = get_database_connection()

    query = QUERIES['analise_produtos'].format(
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        limit=limit
    )

    df = db.execute_query(query)

    if df is not None and len(df) > 0:
        # Calcular coeficiente de variação
        df['coef_variacao'] = (df['desvio_padrao'] / (df['media_tarifa'] + 0.001)) * 100

        # Calcular range
        df['range_tarifa'] = df['max_tarifa'] - df['min_tarifa']

    return df


@st.cache_data(ttl=CACHE_CONFIG['detalhes_periodo_ttl'])
def carregar_analise_setorial(periodo_inicio: str, periodo_fim: str) -> pd.DataFrame:
    """
    Carrega análise setorial (por NCM 2 dígitos)

    Args:
        periodo_inicio: Período inicial
        periodo_fim: Período final

    Returns:
        DataFrame com análise setorial
    """
    db = get_database_connection()

    query = QUERIES['analise_setorial'].format(
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim
    )

    df = db.execute_query(query)

    if df is not None and len(df) > 0:
        # Calcular taxa de correção
        df['taxa_correcao'] = (
            df['aproximou'] / (df['aproximou'] + df['afastou'] + 0.001) * 100
        )

        # Calcular taxa de extremas
        df['taxa_extremas'] = (
            df['extremas'] / (df['total_casos'] + 0.001) * 100
        )

    return df


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def _processar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa DataFrame com conversões e tratamentos padrão

    Args:
        df: DataFrame para processar

    Returns:
        DataFrame processado
    """
    # Converter colunas numéricas
    numeric_cols = [
        'tarifa_praticada', 'tarifa_media_historica', 'desvio_padrao',
        'tarifa_ia', 'diferenca_ia', 'diferenca_percentual_ia', 'bc_total'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Tratar valores nulos
    df = df.fillna({
        'classificacao_mudanca': 'NAO_CLASSIFICADO',
        'movimento_tarifario': 'NAO_DEFINIDO',
        'desvio_padrao': 0,
        'diferenca_ia': 0
    })

    # Converter período para datetime se existir
    if 'periodo' in df.columns:
        df['periodo_dt'] = pd.to_datetime(df['periodo'], format='%Y-%m', errors='coerce')

    return df


def formatar_cnpj(cnpj: str) -> str:
    """
    Formata CNPJ para exibição

    Args:
        cnpj: CNPJ sem formatação

    Returns:
        CNPJ formatado (00.000.000/0000-00)
    """
    if pd.isna(cnpj) or cnpj is None:
        return ''

    cnpj = str(cnpj).zfill(14)

    if len(cnpj) != 14:
        return cnpj

    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def formatar_moeda(valor: float) -> str:
    """Formata valor como moeda brasileira"""
    if pd.isna(valor):
        return 'R$ 0,00'
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')


def formatar_percentual(valor: float) -> str:
    """Formata valor como percentual"""
    if pd.isna(valor):
        return '0,00%'
    return f"{valor:.2f}%".replace('.', ',')


def calcular_periodo_range(meses_atras: int = 12) -> tuple:
    """
    Calcula range de períodos

    Args:
        meses_atras: Quantos meses atrás buscar

    Returns:
        Tupla (periodo_inicio, periodo_fim) no formato YYYY-MM
    """
    hoje = datetime.now()
    periodo_fim = hoje.strftime('%Y-%m')

    inicio = hoje - timedelta(days=meses_atras * 30)
    periodo_inicio = inicio.strftime('%Y-%m')

    return periodo_inicio, periodo_fim


def limpar_cache():
    """Limpa todo o cache de dados"""
    st.cache_data.clear()
    logger.info("Cache limpo com sucesso")


def obter_periodos_disponiveis() -> List[str]:
    """
    Obtém lista de períodos disponíveis no banco

    Returns:
        Lista de períodos no formato YYYY-MM
    """
    # Por padrão, retorna últimos 24 meses
    periodos = []
    hoje = datetime.now()

    for i in range(24):
        data = hoje - timedelta(days=i * 30)
        periodos.append(data.strftime('%Y-%m'))

    return sorted(periodos, reverse=True)
