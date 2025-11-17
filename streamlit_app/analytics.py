"""
ARGOS - Sistema de Análise de Mudança de Comportamento Tributário
Módulo de Análises Estatísticas Avançadas
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from typing import Dict, List, Tuple, Any, Optional
import logging

from config import ML_CONFIG, ALERT_WEIGHTS

logger = logging.getLogger(__name__)


# ============================================================================
# ANÁLISES ESTATÍSTICAS BÁSICAS
# ============================================================================

def calcular_estatisticas_descritivas(df: pd.DataFrame, coluna: str) -> Dict[str, float]:
    """
    Calcula estatísticas descritivas para uma coluna

    Args:
        df: DataFrame
        coluna: Nome da coluna

    Returns:
        Dicionário com estatísticas
    """
    if coluna not in df.columns or df[coluna].isna().all():
        return {}

    dados = df[coluna].dropna()

    return {
        'media': dados.mean(),
        'mediana': dados.median(),
        'moda': dados.mode()[0] if len(dados.mode()) > 0 else None,
        'desvio_padrao': dados.std(),
        'variancia': dados.var(),
        'minimo': dados.min(),
        'maximo': dados.max(),
        'q1': dados.quantile(0.25),
        'q3': dados.quantile(0.75),
        'iqr': dados.quantile(0.75) - dados.quantile(0.25),
        'coef_variacao': (dados.std() / dados.mean() * 100) if dados.mean() != 0 else 0,
        'assimetria': dados.skew(),
        'curtose': dados.kurtosis(),
        'contagem': len(dados)
    }


def calcular_distribuicao(df: pd.DataFrame, coluna: str, bins: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calcula distribuição de frequência

    Args:
        df: DataFrame
        coluna: Nome da coluna
        bins: Número de bins

    Returns:
        Tupla (contagens, bins)
    """
    dados = df[coluna].dropna()

    if len(dados) == 0:
        return np.array([]), np.array([])

    counts, bins = np.histogram(dados, bins=bins)
    return counts, bins


def teste_normalidade(df: pd.DataFrame, coluna: str) -> Dict[str, Any]:
    """
    Testa normalidade da distribuição (Shapiro-Wilk)

    Args:
        df: DataFrame
        coluna: Nome da coluna

    Returns:
        Dicionário com resultados do teste
    """
    dados = df[coluna].dropna()

    if len(dados) < 3:
        return {'erro': 'Amostra muito pequena'}

    # Limitar amostra para performance (Shapiro-Wilk é lento para grandes amostras)
    if len(dados) > 5000:
        dados = dados.sample(5000, random_state=ML_CONFIG['random_state'])

    try:
        statistic, p_value = stats.shapiro(dados)

        return {
            'estatistica': statistic,
            'p_valor': p_value,
            'normal': p_value > 0.05,
            'interpretacao': 'Normal' if p_value > 0.05 else 'Não-normal'
        }
    except Exception as e:
        logger.error(f"Erro no teste de normalidade: {str(e)}")
        return {'erro': str(e)}


# ============================================================================
# CORRELAÇÕES E RELACIONAMENTOS
# ============================================================================

def calcular_matriz_correlacao(
    df: pd.DataFrame,
    colunas: List[str] = None,
    metodo: str = 'pearson'
) -> pd.DataFrame:
    """
    Calcula matriz de correlação

    Args:
        df: DataFrame
        colunas: Lista de colunas (None = todas numéricas)
        metodo: pearson, spearman ou kendall

    Returns:
        DataFrame com matriz de correlação
    """
    if colunas is None:
        colunas = df.select_dtypes(include=[np.number]).columns.tolist()

    df_num = df[colunas].dropna()

    if len(df_num) == 0:
        return pd.DataFrame()

    try:
        corr_matrix = df_num.corr(method=metodo)
        return corr_matrix
    except Exception as e:
        logger.error(f"Erro ao calcular correlação: {str(e)}")
        return pd.DataFrame()


def identificar_correlacoes_fortes(
    corr_matrix: pd.DataFrame,
    threshold: float = 0.7
) -> List[Tuple[str, str, float]]:
    """
    Identifica correlações fortes na matriz

    Args:
        corr_matrix: Matriz de correlação
        threshold: Threshold para correlação forte

    Returns:
        Lista de tuplas (var1, var2, correlação)
    """
    correlacoes = []

    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            corr_val = corr_matrix.iloc[i, j]

            if abs(corr_val) >= threshold:
                correlacoes.append((
                    corr_matrix.columns[i],
                    corr_matrix.columns[j],
                    corr_val
                ))

    # Ordenar por valor absoluto de correlação
    correlacoes.sort(key=lambda x: abs(x[2]), reverse=True)

    return correlacoes


# ============================================================================
# DETECÇÃO DE OUTLIERS
# ============================================================================

def detectar_outliers_iqr(df: pd.DataFrame, coluna: str, fator: float = 1.5) -> pd.DataFrame:
    """
    Detecta outliers usando método IQR

    Args:
        df: DataFrame
        coluna: Nome da coluna
        fator: Fator multiplicador do IQR (padrão 1.5)

    Returns:
        DataFrame com coluna 'is_outlier'
    """
    df_result = df.copy()

    q1 = df[coluna].quantile(0.25)
    q3 = df[coluna].quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - fator * iqr
    upper_bound = q3 + fator * iqr

    df_result['is_outlier'] = (
        (df[coluna] < lower_bound) | (df[coluna] > upper_bound)
    )
    df_result['outlier_score'] = np.abs(
        (df[coluna] - df[coluna].median()) / (iqr + 0.001)
    )

    return df_result


def detectar_outliers_zscore(df: pd.DataFrame, coluna: str, threshold: float = 3.0) -> pd.DataFrame:
    """
    Detecta outliers usando Z-score

    Args:
        df: DataFrame
        coluna: Nome da coluna
        threshold: Threshold de Z-score

    Returns:
        DataFrame com coluna 'is_outlier'
    """
    df_result = df.copy()

    mean = df[coluna].mean()
    std = df[coluna].std()

    if std == 0:
        df_result['is_outlier'] = False
        df_result['z_score'] = 0
        return df_result

    z_scores = np.abs((df[coluna] - mean) / std)

    df_result['is_outlier'] = z_scores > threshold
    df_result['z_score'] = z_scores

    return df_result


def detectar_outliers_isolation_forest(
    df: pd.DataFrame,
    colunas: List[str],
    contamination: float = None
) -> pd.DataFrame:
    """
    Detecta outliers multivariados usando Isolation Forest

    Args:
        df: DataFrame
        colunas: Lista de colunas para análise
        contamination: Proporção esperada de outliers

    Returns:
        DataFrame com coluna 'is_outlier' e 'anomaly_score'
    """
    if contamination is None:
        contamination = ML_CONFIG['outlier_contamination']

    df_result = df.copy()
    df_analysis = df[colunas].dropna()

    if len(df_analysis) < 10:
        df_result['is_outlier'] = False
        df_result['anomaly_score'] = 0
        return df_result

    try:
        # Padronizar dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_analysis)

        # Treinar Isolation Forest
        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=ML_CONFIG['random_state'],
            n_estimators=100
        )

        predictions = iso_forest.fit_predict(X_scaled)
        scores = iso_forest.score_samples(X_scaled)

        # Mapear resultados de volta ao DataFrame original
        df_result.loc[df_analysis.index, 'is_outlier'] = predictions == -1
        df_result.loc[df_analysis.index, 'anomaly_score'] = -scores  # Inverter para maior = mais anômalo

        # Preencher NaN
        df_result['is_outlier'] = df_result['is_outlier'].fillna(False)
        df_result['anomaly_score'] = df_result['anomaly_score'].fillna(0)

    except Exception as e:
        logger.error(f"Erro na detecção de outliers: {str(e)}")
        df_result['is_outlier'] = False
        df_result['anomaly_score'] = 0

    return df_result


# ============================================================================
# CLUSTERING E SEGMENTAÇÃO
# ============================================================================

def criar_clusters(
    df: pd.DataFrame,
    colunas: List[str],
    n_clusters: int = None
) -> pd.DataFrame:
    """
    Cria clusters usando K-Means

    Args:
        df: DataFrame
        colunas: Lista de colunas para clustering
        n_clusters: Número de clusters (None = automático)

    Returns:
        DataFrame com coluna 'cluster'
    """
    if n_clusters is None:
        n_clusters = ML_CONFIG['n_clusters']

    df_result = df.copy()
    df_analysis = df[colunas].dropna()

    if len(df_analysis) < n_clusters:
        df_result['cluster'] = 0
        return df_result

    try:
        # Padronizar dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_analysis)

        # K-Means
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=ML_CONFIG['random_state'],
            n_init=10
        )

        clusters = kmeans.fit_predict(X_scaled)

        # Mapear resultados
        df_result.loc[df_analysis.index, 'cluster'] = clusters
        df_result['cluster'] = df_result['cluster'].fillna(-1).astype(int)

    except Exception as e:
        logger.error(f"Erro no clustering: {str(e)}")
        df_result['cluster'] = 0

    return df_result


def calcular_elbow_score(df: pd.DataFrame, colunas: List[str], max_k: int = 10) -> List[float]:
    """
    Calcula inércia para diferentes valores de K (método do cotovelo)

    Args:
        df: DataFrame
        colunas: Lista de colunas
        max_k: Máximo de clusters para testar

    Returns:
        Lista com inércia para cada K
    """
    df_analysis = df[colunas].dropna()

    if len(df_analysis) < 2:
        return []

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_analysis)

    inertias = []

    for k in range(1, min(max_k + 1, len(df_analysis))):
        kmeans = KMeans(n_clusters=k, random_state=ML_CONFIG['random_state'], n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)

    return inertias


# ============================================================================
# ANÁLISE DE TENDÊNCIAS
# ============================================================================

def calcular_tendencia_linear(df: pd.DataFrame, coluna_x: str, coluna_y: str) -> Dict[str, float]:
    """
    Calcula regressão linear simples

    Args:
        df: DataFrame
        coluna_x: Variável independente
        coluna_y: Variável dependente

    Returns:
        Dicionário com coeficientes e métricas
    """
    df_clean = df[[coluna_x, coluna_y]].dropna()

    if len(df_clean) < 2:
        return {}

    try:
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            df_clean[coluna_x],
            df_clean[coluna_y]
        )

        return {
            'coeficiente_angular': slope,
            'intercepto': intercept,
            'r_squared': r_value ** 2,
            'p_valor': p_value,
            'erro_padrao': std_err,
            'interpretacao': _interpretar_tendencia(slope, p_value)
        }

    except Exception as e:
        logger.error(f"Erro no cálculo de tendência: {str(e)}")
        return {}


def _interpretar_tendencia(slope: float, p_value: float, alpha: float = 0.05) -> str:
    """Interpreta tendência linear"""
    if p_value > alpha:
        return "Sem tendência significativa"

    if slope > 0:
        magnitude = "forte" if abs(slope) > 1 else "moderada" if abs(slope) > 0.5 else "fraca"
        return f"Tendência crescente {magnitude}"
    else:
        magnitude = "forte" if abs(slope) > 1 else "moderada" if abs(slope) > 0.5 else "fraca"
        return f"Tendência decrescente {magnitude}"


def calcular_media_movel(
    df: pd.DataFrame,
    coluna: str,
    janela: int = 3,
    centro: bool = True
) -> pd.Series:
    """
    Calcula média móvel

    Args:
        df: DataFrame
        coluna: Nome da coluna
        janela: Tamanela da média móvel
        centro: Se True, centraliza a janela

    Returns:
        Series com média móvel
    """
    return df[coluna].rolling(window=janela, center=centro, min_periods=1).mean()


# ============================================================================
# SISTEMA DE SCORING E ALERTAS
# ============================================================================

def calcular_score_risco(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula score de risco para cada registro

    Args:
        df: DataFrame com dados de empresas

    Returns:
        DataFrame com coluna 'risk_score'
    """
    df_result = df.copy()

    # Inicializar score
    df_result['risk_score'] = 0

    # Componente 1: Mudanças Extremas (peso 40)
    if 'extremas' in df.columns and 'total_casos' in df.columns:
        taxa_extremas = (df['extremas'] / (df['total_casos'] + 0.001)) * 100
        # Normalizar para 0-40
        extremas_score = np.clip(taxa_extremas / 100 * ALERT_WEIGHTS['mudancas_extremas'], 0, ALERT_WEIGHTS['mudancas_extremas'])
        df_result['risk_score'] += extremas_score

    # Componente 2: Taxa de Afastamento (peso 30)
    if 'afastou' in df.columns and 'aproximou' in df.columns:
        total_mov = df['afastou'] + df['aproximou'] + 0.001
        taxa_afastamento = (df['afastou'] / total_mov) * 100
        # Normalizar para 0-30
        afastamento_score = np.clip(taxa_afastamento / 100 * ALERT_WEIGHTS['taxa_afastamento'], 0, ALERT_WEIGHTS['taxa_afastamento'])
        df_result['risk_score'] += afastamento_score

    # Componente 3: Base de Cálculo (peso 20)
    if 'bc_total' in df.columns:
        # Normalizar base de cálculo (percentil)
        bc_percentile = df['bc_total'].rank(pct=True) * 100
        bc_score = np.clip(bc_percentile / 100 * ALERT_WEIGHTS['base_calculo'], 0, ALERT_WEIGHTS['base_calculo'])
        df_result['risk_score'] += bc_score

    # Componente 4: Volatilidade (peso 10)
    if 'volatilidade' in df.columns:
        # Normalizar volatilidade
        vol_percentile = df['volatilidade'].rank(pct=True) * 100
        vol_score = np.clip(vol_percentile / 100 * ALERT_WEIGHTS['volatilidade'], 0, ALERT_WEIGHTS['volatilidade'])
        df_result['risk_score'] += vol_score

    # Garantir score entre 0-100
    df_result['risk_score'] = np.clip(df_result['risk_score'], 0, 100)

    return df_result


def classificar_nivel_alerta(score: float) -> str:
    """
    Classifica nível de alerta baseado no score

    Args:
        score: Score de risco (0-100)

    Returns:
        Nível de alerta (LOW, MEDIUM, HIGH, CRITICAL, EMERGENCY)
    """
    from config import ALERT_LEVELS

    for nivel, config in sorted(
        ALERT_LEVELS.items(),
        key=lambda x: x[1]['priority']
    ):
        if score >= config['min_score']:
            return nivel

    return 'LOW'


# ============================================================================
# ANÁLISES COMPARATIVAS
# ============================================================================

def comparar_periodos(
    df: pd.DataFrame,
    periodo_col: str,
    metrica_col: str,
    periodo1: str,
    periodo2: str
) -> Dict[str, Any]:
    """
    Compara métrica entre dois períodos

    Args:
        df: DataFrame
        periodo_col: Nome da coluna de período
        metrica_col: Nome da coluna de métrica
        periodo1: Primeiro período
        periodo2: Segundo período

    Returns:
        Dicionário com resultados da comparação
    """
    dados_p1 = df[df[periodo_col] == periodo1][metrica_col]
    dados_p2 = df[df[periodo_col] == periodo2][metrica_col]

    if len(dados_p1) == 0 or len(dados_p2) == 0:
        return {'erro': 'Períodos sem dados'}

    media_p1 = dados_p1.mean()
    media_p2 = dados_p2.mean()

    variacao_abs = media_p2 - media_p1
    variacao_pct = (variacao_abs / (media_p1 + 0.001)) * 100

    # Teste t para verificar se diferença é significativa
    try:
        t_stat, p_value = stats.ttest_ind(dados_p1, dados_p2)
        significativo = p_value < 0.05
    except:
        t_stat, p_value, significativo = None, None, None

    return {
        'periodo1': periodo1,
        'periodo2': periodo2,
        'media_periodo1': media_p1,
        'media_periodo2': media_p2,
        'variacao_absoluta': variacao_abs,
        'variacao_percentual': variacao_pct,
        't_statistic': t_stat,
        'p_valor': p_value,
        'diferenca_significativa': significativo,
        'interpretacao': _interpretar_variacao(variacao_pct, significativo)
    }


def _interpretar_variacao(variacao_pct: float, significativo: Optional[bool]) -> str:
    """Interpreta variação percentual"""
    if significativo is False:
        return "Sem mudança significativa"

    if abs(variacao_pct) < 5:
        return "Mudança mínima"
    elif abs(variacao_pct) < 15:
        magnitude = "Aumento moderado" if variacao_pct > 0 else "Redução moderada"
    elif abs(variacao_pct) < 30:
        magnitude = "Aumento considerável" if variacao_pct > 0 else "Redução considerável"
    else:
        magnitude = "Aumento expressivo" if variacao_pct > 0 else "Redução expressiva"

    return magnitude
