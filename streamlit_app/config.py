"""
ARGOS - Sistema de Análise de Mudança de Comportamento Tributário
Módulo de Configuração e Constantes
"""

# ============================================================================
# CONFIGURAÇÕES DO BANCO DE DADOS
# ============================================================================

DATABASE_CONFIG = {
    'host': 'bdaworkernode02.sef.sc.gov.br',
    'port': 21050,
    'database': 'niat',
    'use_ldap': True,
    'auth_mechanism': 'LDAP'
}

# ============================================================================
# CONFIGURAÇÕES DE CACHE
# ============================================================================

CACHE_CONFIG = {
    'dados_agregados_ttl': 3600,  # 1 hora
    'detalhes_empresa_ttl': 1800,  # 30 minutos
    'detalhes_periodo_ttl': 1800,  # 30 minutos
    'kpis_ttl': 600,  # 10 minutos
    'max_entries': 100
}

# ============================================================================
# CONFIGURAÇÕES DE PERFORMANCE
# ============================================================================

PERFORMANCE_CONFIG = {
    'max_records_query': 50000,  # Aumentado para mais dados
    'batch_size': 10000,
    'min_periods_analysis': 3,
    'parallel_queries': True
}

# ============================================================================
# CLASSIFICAÇÕES E CATEGORIAS
# ============================================================================

CLASSIFICACOES = {
    'COMPORTAMENTO_NORMAL': {
        'label': 'Normal',
        'color': '#28a745',
        'icon': '✓',
        'description': 'Comportamento dentro do esperado'
    },
    'MUDANCA_SIGNIFICATIVA': {
        'label': 'Significativa',
        'color': '#ffc107',
        'icon': '⚠',
        'description': 'Mudança significativa detectada'
    },
    'MUDANCA_EXTREMA': {
        'label': 'Extrema',
        'color': '#dc3545',
        'icon': '⚠',
        'description': 'Mudança extrema - alta prioridade'
    },
    'PRODUTO_ESTAVEL': {
        'label': 'Estável',
        'color': '#17a2b8',
        'icon': '●',
        'description': 'Produto sem variação histórica'
    }
}

MOVIMENTOS = {
    'APROXIMOU_DA_CORRETA': {
        'label': 'Aproximou',
        'color': '#28a745',
        'icon': '↗',
        'description': 'Aproximou da tarifa correta'
    },
    'AFASTOU_DA_CORRETA': {
        'label': 'Afastou',
        'color': '#dc3545',
        'icon': '↘',
        'description': 'Afastou da tarifa correta'
    },
    'MANTEVE_DISTANCIA': {
        'label': 'Manteve',
        'color': '#6c757d',
        'icon': '→',
        'description': 'Manteve a distância'
    },
    'SEM_REFERENCIA_IA': {
        'label': 'Sem Ref.',
        'color': '#adb5bd',
        'icon': '?',
        'description': 'Sem referência IA'
    }
}

# ============================================================================
# SISTEMA DE ALERTAS
# ============================================================================

ALERT_LEVELS = {
    'EMERGENCY': {
        'label': 'EMERGENCIAL',
        'color': '#8B0000',
        'min_score': 80,
        'icon': '🔴',
        'priority': 1
    },
    'CRITICAL': {
        'label': 'CRÍTICO',
        'color': '#dc3545',
        'min_score': 60,
        'icon': '🔴',
        'priority': 2
    },
    'HIGH': {
        'label': 'ALTO',
        'color': '#fd7e14',
        'min_score': 40,
        'icon': '🟠',
        'priority': 3
    },
    'MEDIUM': {
        'label': 'MÉDIO',
        'color': '#ffc107',
        'min_score': 20,
        'icon': '🟡',
        'priority': 4
    },
    'LOW': {
        'label': 'BAIXO',
        'color': '#28a745',
        'min_score': 0,
        'icon': '🟢',
        'priority': 5
    }
}

ALERT_WEIGHTS = {
    'mudancas_extremas': 40,
    'taxa_afastamento': 30,
    'base_calculo': 20,
    'volatilidade': 10
}

# ============================================================================
# CONFIGURAÇÕES DE VISUALIZAÇÃO
# ============================================================================

CHART_COLORS = {
    'primary': '#1f77b4',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'secondary': '#6c757d',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

CHART_TEMPLATES = {
    'default': 'plotly_white',
    'dark': 'plotly_dark',
    'presentation': 'presentation'
}

# ============================================================================
# TEMAS PERSONALIZADOS
# ============================================================================

THEME_LIGHT = {
    'backgroundColor': '#ffffff',
    'secondaryBackgroundColor': '#f8f9fa',
    'textColor': '#262730',
    'primaryColor': '#1f77b4',
    'font': 'sans-serif'
}

THEME_DARK = {
    'backgroundColor': '#0e1117',
    'secondaryBackgroundColor': '#262730',
    'textColor': '#fafafa',
    'primaryColor': '#1f77b4',
    'font': 'sans-serif'
}

# ============================================================================
# QUERIES SQL
# ============================================================================

QUERIES = {
    'dados_principais': """
        SELECT
            cnpj,
            periodo,
            gtin,
            ncm,
            ncm_2dig,
            produto,
            classificacao_mudanca,
            movimento_tarifario,
            tarifa_praticada,
            tarifa_media_historica,
            desvio_padrao,
            tarifa_ia,
            diferenca_ia,
            diferenca_percentual_ia,
            bc_total,
            qtd_nfce
        FROM niat.argos_vw_evolucao_nfce
        WHERE periodo >= '{periodo_inicio}'
          AND periodo <= '{periodo_fim}'
        LIMIT {limit}
    """,

    'kpis_agregados': """
        SELECT
            COUNT(*) as total_registros,
            COUNT(DISTINCT cnpj) as total_empresas,
            COUNT(DISTINCT CONCAT(gtin, ncm)) as total_produtos,
            SUM(CASE WHEN movimento_tarifario = 'APROXIMOU_DA_CORRETA' THEN 1 ELSE 0 END) as aproximou,
            SUM(CASE WHEN movimento_tarifario = 'AFASTOU_DA_CORRETA' THEN 1 ELSE 0 END) as afastou,
            SUM(CASE WHEN classificacao_mudanca = 'MUDANCA_EXTREMA' THEN 1 ELSE 0 END) as extremas,
            SUM(CASE WHEN classificacao_mudanca = 'MUDANCA_SIGNIFICATIVA' THEN 1 ELSE 0 END) as significativas,
            SUM(bc_total) as bc_total,
            AVG(ABS(diferenca_ia)) as media_diferenca_ia,
            AVG(tarifa_praticada) as media_tarifa_praticada
        FROM niat.argos_vw_evolucao_nfce
        WHERE periodo >= '{periodo_inicio}'
          AND periodo <= '{periodo_fim}'
    """,

    'ranking_empresas': """
        SELECT
            cnpj,
            COUNT(*) as total_casos,
            SUM(CASE WHEN movimento_tarifario = 'APROXIMOU_DA_CORRETA' THEN 1 ELSE 0 END) as aproximou,
            SUM(CASE WHEN movimento_tarifario = 'AFASTOU_DA_CORRETA' THEN 1 ELSE 0 END) as afastou,
            SUM(CASE WHEN classificacao_mudanca = 'MUDANCA_EXTREMA' THEN 1 ELSE 0 END) as extremas,
            SUM(CASE WHEN classificacao_mudanca = 'MUDANCA_SIGNIFICATIVA' THEN 1 ELSE 0 END) as significativas,
            SUM(bc_total) as bc_total,
            AVG(ABS(diferenca_ia)) as media_diferenca_ia,
            STDDEV(tarifa_praticada) as volatilidade
        FROM niat.argos_vw_evolucao_nfce
        WHERE periodo >= '{periodo_inicio}'
          AND periodo <= '{periodo_fim}'
        GROUP BY cnpj
        ORDER BY {order_by} DESC
        LIMIT {limit}
    """,

    'detalhes_empresa': """
        SELECT *
        FROM niat.argos_vw_evolucao_nfce
        WHERE cnpj = '{cnpj}'
          AND periodo >= '{periodo_inicio}'
          AND periodo <= '{periodo_fim}'
        ORDER BY periodo, gtin, ncm
    """,

    'evolucao_temporal': """
        SELECT
            periodo,
            COUNT(*) as total_casos,
            COUNT(DISTINCT cnpj) as empresas,
            SUM(CASE WHEN movimento_tarifario = 'APROXIMOU_DA_CORRETA' THEN 1 ELSE 0 END) as aproximou,
            SUM(CASE WHEN movimento_tarifario = 'AFASTOU_DA_CORRETA' THEN 1 ELSE 0 END) as afastou,
            SUM(CASE WHEN classificacao_mudanca = 'MUDANCA_EXTREMA' THEN 1 ELSE 0 END) as extremas,
            SUM(bc_total) as bc_total,
            AVG(tarifa_praticada) as media_tarifa
        FROM niat.argos_vw_evolucao_nfce
        WHERE periodo >= '{periodo_inicio}'
          AND periodo <= '{periodo_fim}'
        GROUP BY periodo
        ORDER BY periodo
    """,

    'analise_produtos': """
        SELECT
            gtin,
            ncm,
            produto,
            COUNT(DISTINCT cnpj) as num_empresas,
            COUNT(DISTINCT periodo) as num_periodos,
            AVG(tarifa_praticada) as media_tarifa,
            STDDEV(tarifa_praticada) as desvio_padrao,
            MIN(tarifa_praticada) as min_tarifa,
            MAX(tarifa_praticada) as max_tarifa,
            SUM(bc_total) as bc_total,
            SUM(CASE WHEN classificacao_mudanca = 'MUDANCA_EXTREMA' THEN 1 ELSE 0 END) as casos_extremos
        FROM niat.argos_vw_evolucao_nfce
        WHERE periodo >= '{periodo_inicio}'
          AND periodo <= '{periodo_fim}'
        GROUP BY gtin, ncm, produto
        HAVING COUNT(DISTINCT periodo) >= 3
        ORDER BY desvio_padrao DESC
        LIMIT {limit}
    """,

    'analise_setorial': """
        SELECT
            ncm_2dig,
            COUNT(*) as total_casos,
            COUNT(DISTINCT cnpj) as empresas,
            COUNT(DISTINCT CONCAT(gtin, ncm)) as produtos,
            SUM(CASE WHEN movimento_tarifario = 'APROXIMOU_DA_CORRETA' THEN 1 ELSE 0 END) as aproximou,
            SUM(CASE WHEN movimento_tarifario = 'AFASTOU_DA_CORRETA' THEN 1 ELSE 0 END) as afastou,
            SUM(CASE WHEN classificacao_mudanca = 'MUDANCA_EXTREMA' THEN 1 ELSE 0 END) as extremas,
            SUM(bc_total) as bc_total,
            AVG(tarifa_praticada) as media_tarifa
        FROM niat.argos_vw_evolucao_nfce
        WHERE periodo >= '{periodo_inicio}'
          AND periodo <= '{periodo_fim}'
        GROUP BY ncm_2dig
        ORDER BY total_casos DESC
    """
}

# ============================================================================
# FORMATAÇÃO
# ============================================================================

FORMAT_CONFIG = {
    'moeda_br': 'R$ {:,.2f}',
    'percentual': '{:.2f}%',
    'numero': '{:,.0f}',
    'decimal': '{:.4f}',
    'cnpj': '{}.{}.{}/{}-{}',
    'data': '%Y-%m'
}

# ============================================================================
# MENSAGENS E TEXTOS
# ============================================================================

MESSAGES = {
    'welcome': '🎯 Sistema ARGOS - Análise de Comportamento Tributário',
    'loading': 'Carregando dados...',
    'no_data': 'Nenhum dado disponível para o período selecionado.',
    'error_db': 'Erro ao conectar ao banco de dados. Verifique as credenciais.',
    'success_export': 'Relatório exportado com sucesso!',
    'updating': 'Atualizando visualizações...',
}

DESCRIPTIONS = {
    'overview': 'Visão geral consolidada do sistema com principais KPIs e métricas.',
    'executive': 'Dashboard executivo com análises de alto nível para tomada de decisão.',
    'companies': 'Análise detalhada por empresa com rankings e drill-down completo.',
    'products': 'Análise de produtos com identificação de volatilidade e riscos.',
    'sectors': 'Análise setorial por NCM com comparações e benchmarks.',
    'temporal': 'Evolução temporal com identificação de tendências e previsões.',
    'alerts': 'Sistema inteligente de alertas com priorização automática.',
    'statistics': 'Análises estatísticas avançadas com correlações e distribuições.',
    'ml': 'Insights de Machine Learning com detecção de padrões e anomalias.',
    'reports': 'Geração e exportação de relatórios personalizados.'
}

# ============================================================================
# CONFIGURAÇÕES DE ML
# ============================================================================

ML_CONFIG = {
    'random_state': 42,
    'test_size': 0.2,
    'n_clusters': 5,
    'outlier_contamination': 0.1,
    'min_samples_prediction': 6
}

# ============================================================================
# EXPORTAÇÃO
# ============================================================================

EXPORT_CONFIG = {
    'excel_engine': 'openpyxl',
    'pdf_orientation': 'landscape',
    'csv_encoding': 'utf-8-sig',
    'csv_sep': ';'
}

# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

AUTH_CONFIG = {
    'password': 'tsevero258',  # TODO: Mover para secrets
    'session_timeout': 3600,  # 1 hora
    'max_attempts': 3
}
