"""
ARGOS - Sistema de Análise de Mudança de Comportamento Tributário
Módulo de Visualizações Avançadas com Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

from config import CHART_COLORS, CLASSIFICACOES, MOVIMENTOS, ALERT_LEVELS


# ============================================================================
# GRÁFICOS DE KPIs E MÉTRICAS
# ============================================================================

def criar_grafico_kpi(
    valor: float,
    titulo: str,
    referencia: Optional[float] = None,
    formato: str = 'numero',
    cor: str = None
) -> go.Figure:
    """
    Cria gráfico de KPI com indicador visual

    Args:
        valor: Valor do KPI
        titulo: Título do KPI
        referencia: Valor de referência (opcional)
        formato: 'numero', 'moeda' ou 'percentual'
        cor: Cor customizada

    Returns:
        Figure Plotly
    """
    if formato == 'moeda':
        valor_formatado = f"R$ {valor:,.2f}"
    elif formato == 'percentual':
        valor_formatado = f"{valor:.2f}%"
    else:
        valor_formatado = f"{valor:,.0f}"

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number+delta" if referencia is not None else "number",
        value=valor,
        title={'text': titulo, 'font': {'size': 16}},
        number={'font': {'size': 40, 'color': cor or CHART_COLORS['primary']}},
        delta={'reference': referencia} if referencia else None,
        domain={'x': [0, 1], 'y': [0, 1]}
    ))

    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def criar_cards_kpis(kpis: Dict[str, Any]) -> go.Figure:
    """
    Cria painel com múltiplos KPIs

    Args:
        kpis: Dicionário com KPIs

    Returns:
        Figure Plotly
    """
    fig = make_subplots(
        rows=2, cols=3,
        specs=[[{'type': 'indicator'}] * 3] * 2,
        subplot_titles=list(kpis.keys())[:6]
    )

    positions = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)]

    for idx, (titulo, valor) in enumerate(list(kpis.items())[:6]):
        row, col = positions[idx]

        fig.add_trace(
            go.Indicator(
                mode="number",
                value=valor,
                title={'text': titulo, 'font': {'size': 14}},
                number={'font': {'size': 24}}
            ),
            row=row, col=col
        )

    fig.update_layout(
        height=400,
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


# ============================================================================
# GRÁFICOS DE DISTRIBUIÇÃO
# ============================================================================

def criar_grafico_pizza(
    df: pd.DataFrame,
    coluna_valores: str,
    coluna_labels: str,
    titulo: str = '',
    mostrar_percentual: bool = True
) -> go.Figure:
    """
    Cria gráfico de pizza interativo

    Args:
        df: DataFrame
        coluna_valores: Coluna com valores
        coluna_labels: Coluna com labels
        titulo: Título do gráfico
        mostrar_percentual: Se True, mostra percentuais

    Returns:
        Figure Plotly
    """
    fig = px.pie(
        df,
        values=coluna_valores,
        names=coluna_labels,
        title=titulo,
        hole=0.4,  # Donut chart
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label' if mostrar_percentual else 'label',
        hovertemplate='<b>%{label}</b><br>Valor: %{value}<br>Percentual: %{percent}<extra></extra>'
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
        margin=dict(l=20, r=150, t=60, b=20),
        height=400
    )

    return fig


def criar_grafico_barras(
    df: pd.DataFrame,
    coluna_x: str,
    coluna_y: str,
    titulo: str = '',
    orientacao: str = 'v',
    cor: Optional[str] = None,
    mostrar_valores: bool = True
) -> go.Figure:
    """
    Cria gráfico de barras

    Args:
        df: DataFrame
        coluna_x: Coluna do eixo X
        coluna_y: Coluna do eixo Y
        titulo: Título
        orientacao: 'v' (vertical) ou 'h' (horizontal)
        cor: Cor das barras
        mostrar_valores: Se True, mostra valores nas barras

    Returns:
        Figure Plotly
    """
    if orientacao == 'h':
        fig = px.bar(df, x=coluna_y, y=coluna_x, orientation='h', title=titulo)
    else:
        fig = px.bar(df, x=coluna_x, y=coluna_y, title=titulo)

    if cor:
        fig.update_traces(marker_color=cor)

    if mostrar_valores:
        fig.update_traces(texttemplate='%{y:,.0f}', textposition='outside')

    fig.update_layout(
        xaxis_title=coluna_x,
        yaxis_title=coluna_y,
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=60, b=60)
    )

    return fig


def criar_histograma(
    df: pd.DataFrame,
    coluna: str,
    bins: int = 30,
    titulo: str = '',
    mostrar_curva_normal: bool = True
) -> go.Figure:
    """
    Cria histograma com opcional curva normal

    Args:
        df: DataFrame
        coluna: Coluna para histograma
        bins: Número de bins
        titulo: Título
        mostrar_curva_normal: Se True, sobrepõe curva normal

    Returns:
        Figure Plotly
    """
    fig = go.Figure()

    dados = df[coluna].dropna()

    # Histograma
    fig.add_trace(go.Histogram(
        x=dados,
        nbinsx=bins,
        name='Frequência',
        marker_color=CHART_COLORS['primary'],
        opacity=0.7
    ))

    # Curva normal (se solicitado)
    if mostrar_curva_normal and len(dados) > 0:
        mu = dados.mean()
        sigma = dados.std()

        x_range = np.linspace(dados.min(), dados.max(), 100)
        y_normal = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
                    np.exp(-0.5 * ((x_range - mu) / sigma) ** 2))

        # Escalar para altura do histograma
        y_normal = y_normal * len(dados) * (dados.max() - dados.min()) / bins

        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_normal,
            mode='lines',
            name='Distribuição Normal',
            line=dict(color=CHART_COLORS['danger'], width=2)
        ))

    fig.update_layout(
        title=titulo,
        xaxis_title=coluna,
        yaxis_title='Frequência',
        height=400,
        showlegend=mostrar_curva_normal,
        barmode='overlay'
    )

    return fig


def criar_boxplot(
    df: pd.DataFrame,
    coluna_y: str,
    coluna_grupo: Optional[str] = None,
    titulo: str = ''
) -> go.Figure:
    """
    Cria boxplot

    Args:
        df: DataFrame
        coluna_y: Coluna com valores
        coluna_grupo: Coluna para agrupar (opcional)
        titulo: Título

    Returns:
        Figure Plotly
    """
    if coluna_grupo:
        fig = px.box(df, x=coluna_grupo, y=coluna_y, title=titulo)
    else:
        fig = px.box(df, y=coluna_y, title=titulo)

    fig.update_layout(
        height=400,
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=60)
    )

    return fig


# ============================================================================
# GRÁFICOS TEMPORAIS
# ============================================================================

def criar_linha_temporal(
    df: pd.DataFrame,
    coluna_x: str,
    colunas_y: List[str],
    titulo: str = '',
    mostrar_markers: bool = True,
    mostrar_tendencia: bool = False
) -> go.Figure:
    """
    Cria gráfico de linhas temporal

    Args:
        df: DataFrame
        coluna_x: Coluna do eixo X (temporal)
        colunas_y: Lista de colunas Y
        titulo: Título
        mostrar_markers: Se True, mostra marcadores
        mostrar_tendencia: Se True, adiciona linha de tendência

    Returns:
        Figure Plotly
    """
    fig = go.Figure()

    cores = [CHART_COLORS['primary'], CHART_COLORS['success'],
             CHART_COLORS['warning'], CHART_COLORS['danger'],
             CHART_COLORS['info']]

    for idx, coluna_y in enumerate(colunas_y):
        fig.add_trace(go.Scatter(
            x=df[coluna_x],
            y=df[coluna_y],
            mode='lines+markers' if mostrar_markers else 'lines',
            name=coluna_y,
            line=dict(color=cores[idx % len(cores)], width=2),
            marker=dict(size=8)
        ))

        # Linha de tendência
        if mostrar_tendencia:
            # Criar índice numérico para x
            x_numeric = np.arange(len(df))
            y_values = df[coluna_y].values

            # Remover NaN
            mask = ~np.isnan(y_values)
            if mask.sum() > 1:
                z = np.polyfit(x_numeric[mask], y_values[mask], 1)
                p = np.poly1d(z)

                fig.add_trace(go.Scatter(
                    x=df[coluna_x],
                    y=p(x_numeric),
                    mode='lines',
                    name=f'Tendência {coluna_y}',
                    line=dict(dash='dash', color=cores[idx % len(cores)], width=1),
                    showlegend=True
                ))

    fig.update_layout(
        title=titulo,
        xaxis_title=coluna_x,
        yaxis_title='Valor',
        hovermode='x unified',
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def criar_area_empilhada(
    df: pd.DataFrame,
    coluna_x: str,
    colunas_y: List[str],
    titulo: str = ''
) -> go.Figure:
    """
    Cria gráfico de área empilhada

    Args:
        df: DataFrame
        coluna_x: Coluna do eixo X
        colunas_y: Lista de colunas Y
        titulo: Título

    Returns:
        Figure Plotly
    """
    fig = go.Figure()

    cores = [CHART_COLORS['success'], CHART_COLORS['warning'],
             CHART_COLORS['danger'], CHART_COLORS['info']]

    for idx, coluna_y in enumerate(colunas_y):
        fig.add_trace(go.Scatter(
            x=df[coluna_x],
            y=df[coluna_y],
            mode='lines',
            name=coluna_y,
            line=dict(width=0.5, color=cores[idx % len(cores)]),
            stackgroup='one',
            fillcolor=cores[idx % len(cores)]
        ))

    fig.update_layout(
        title=titulo,
        xaxis_title=coluna_x,
        yaxis_title='Valor',
        hovermode='x unified',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


# ============================================================================
# GRÁFICOS DE CORRELAÇÃO E DISPERSÃO
# ============================================================================

def criar_scatter_plot(
    df: pd.DataFrame,
    coluna_x: str,
    coluna_y: str,
    coluna_tamanho: Optional[str] = None,
    coluna_cor: Optional[str] = None,
    titulo: str = '',
    mostrar_tendencia: bool = True
) -> go.Figure:
    """
    Cria gráfico de dispersão

    Args:
        df: DataFrame
        coluna_x: Coluna eixo X
        coluna_y: Coluna eixo Y
        coluna_tamanho: Coluna para tamanho dos pontos
        coluna_cor: Coluna para cor dos pontos
        titulo: Título
        mostrar_tendencia: Se True, adiciona linha de tendência

    Returns:
        Figure Plotly
    """
    fig = px.scatter(
        df,
        x=coluna_x,
        y=coluna_y,
        size=coluna_tamanho,
        color=coluna_cor,
        title=titulo,
        trendline='ols' if mostrar_tendencia else None
    )

    fig.update_traces(marker=dict(line=dict(width=0.5, color='white')))

    fig.update_layout(
        height=500,
        hovermode='closest'
    )

    return fig


def criar_heatmap_correlacao(
    corr_matrix: pd.DataFrame,
    titulo: str = 'Matriz de Correlação'
) -> go.Figure:
    """
    Cria heatmap de correlação

    Args:
        corr_matrix: Matriz de correlação
        titulo: Título

    Returns:
        Figure Plotly
    """
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Correlação")
    ))

    fig.update_layout(
        title=titulo,
        height=600,
        xaxis={'side': 'bottom'},
        yaxis={'side': 'left'}
    )

    return fig


# ============================================================================
# GRÁFICOS ESPECIALIZADOS ARGOS
# ============================================================================

def criar_grafico_classificacoes(df: pd.DataFrame) -> go.Figure:
    """
    Cria gráfico de pizza para classificações de mudança

    Args:
        df: DataFrame com coluna 'classificacao_mudanca'

    Returns:
        Figure Plotly
    """
    # Contar classificações
    classificacoes_count = df['classificacao_mudanca'].value_counts()

    # Preparar cores
    cores = [CLASSIFICACOES.get(c, {}).get('color', '#cccccc')
             for c in classificacoes_count.index]

    # Preparar labels
    labels = [CLASSIFICACOES.get(c, {}).get('label', c)
              for c in classificacoes_count.index]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=classificacoes_count.values,
        hole=0.4,
        marker=dict(colors=cores),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Casos: %{value}<br>Percentual: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title='Distribuição por Classificação',
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5)
    )

    return fig


def criar_grafico_movimentos(df: pd.DataFrame) -> go.Figure:
    """
    Cria gráfico de barras para movimentos tarifários

    Args:
        df: DataFrame com coluna 'movimento_tarifario'

    Returns:
        Figure Plotly
    """
    # Contar movimentos
    movimentos_count = df['movimento_tarifario'].value_counts()

    # Preparar cores e labels
    cores = [MOVIMENTOS.get(m, {}).get('color', '#cccccc')
             for m in movimentos_count.index]

    labels = [MOVIMENTOS.get(m, {}).get('label', m)
              for m in movimentos_count.index]

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=movimentos_count.values,
        marker_color=cores,
        text=movimentos_count.values,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Casos: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title='Distribuição por Movimento Tarifário',
        xaxis_title='Movimento',
        yaxis_title='Quantidade de Casos',
        height=400,
        showlegend=False
    )

    return fig


def criar_grafico_alertas(df: pd.DataFrame) -> go.Figure:
    """
    Cria gráfico de barras horizontal para níveis de alerta

    Args:
        df: DataFrame com coluna 'nivel_alerta'

    Returns:
        Figure Plotly
    """
    # Contar alertas
    alertas_count = df['nivel_alerta'].value_counts()

    # Ordenar por prioridade
    ordem = sorted(
        alertas_count.index,
        key=lambda x: ALERT_LEVELS.get(x, {}).get('priority', 999)
    )

    valores = [alertas_count.get(nivel, 0) for nivel in ordem]
    labels = [ALERT_LEVELS.get(nivel, {}).get('label', nivel) for nivel in ordem]
    cores = [ALERT_LEVELS.get(nivel, {}).get('color', '#cccccc') for nivel in ordem]

    fig = go.Figure(data=[go.Bar(
        y=labels,
        x=valores,
        orientation='h',
        marker_color=cores,
        text=valores,
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Casos: %{x}<extra></extra>'
    )])

    fig.update_layout(
        title='Distribuição por Nível de Alerta',
        xaxis_title='Quantidade de Casos',
        yaxis_title='Nível de Alerta',
        height=400,
        showlegend=False
    )

    return fig


def criar_grafico_evolucao_empresa(df: pd.DataFrame, cnpj: str) -> go.Figure:
    """
    Cria gráfico de evolução temporal de uma empresa

    Args:
        df: DataFrame filtrado para a empresa
        cnpj: CNPJ da empresa

    Returns:
        Figure Plotly com múltiplas séries
    """
    # Agrupar por período
    df_periodo = df.groupby('periodo').agg({
        'tarifa_praticada': 'mean',
        'tarifa_ia': 'mean',
        'tarifa_media_historica': 'mean',
        'bc_total': 'sum'
    }).reset_index()

    # Criar subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Evolução das Tarifas', 'Base de Cálculo Total'),
        vertical_spacing=0.15,
        row_heights=[0.6, 0.4]
    )

    # Gráfico 1: Tarifas
    fig.add_trace(
        go.Scatter(
            x=df_periodo['periodo'],
            y=df_periodo['tarifa_praticada'],
            mode='lines+markers',
            name='Tarifa Praticada',
            line=dict(color=CHART_COLORS['primary'], width=2)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df_periodo['periodo'],
            y=df_periodo['tarifa_ia'],
            mode='lines+markers',
            name='Tarifa IA (Referência)',
            line=dict(color=CHART_COLORS['success'], width=2, dash='dash')
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df_periodo['periodo'],
            y=df_periodo['tarifa_media_historica'],
            mode='lines',
            name='Média Histórica',
            line=dict(color=CHART_COLORS['secondary'], width=1, dash='dot')
        ),
        row=1, col=1
    )

    # Gráfico 2: Base de Cálculo
    fig.add_trace(
        go.Bar(
            x=df_periodo['periodo'],
            y=df_periodo['bc_total'],
            name='Base de Cálculo',
            marker_color=CHART_COLORS['info']
        ),
        row=2, col=1
    )

    fig.update_xaxes(title_text="Período", row=2, col=1)
    fig.update_yaxes(title_text="Tarifa (%)", row=1, col=1)
    fig.update_yaxes(title_text="Valor (R$)", row=2, col=1)

    fig.update_layout(
        title=f'Evolução Temporal - CNPJ: {cnpj}',
        height=700,
        showlegend=True,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def criar_gauge_chart(valor: float, titulo: str, min_val: float = 0, max_val: float = 100) -> go.Figure:
    """
    Cria gráfico de gauge (velocímetro)

    Args:
        valor: Valor atual
        titulo: Título
        min_val: Valor mínimo
        max_val: Valor máximo

    Returns:
        Figure Plotly
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor,
        title={'text': titulo},
        delta={'reference': (max_val + min_val) / 2},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': CHART_COLORS['primary']},
            'steps': [
                {'range': [min_val, max_val * 0.33], 'color': CHART_COLORS['success']},
                {'range': [max_val * 0.33, max_val * 0.66], 'color': CHART_COLORS['warning']},
                {'range': [max_val * 0.66, max_val], 'color': CHART_COLORS['danger']}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.9
            }
        }
    ))

    fig.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=20))

    return fig


def criar_sunburst(
    df: pd.DataFrame,
    path: List[str],
    values: str,
    titulo: str = ''
) -> go.Figure:
    """
    Cria gráfico sunburst (hierárquico)

    Args:
        df: DataFrame
        path: Lista de colunas para hierarquia
        values: Coluna de valores
        titulo: Título

    Returns:
        Figure Plotly
    """
    fig = px.sunburst(
        df,
        path=path,
        values=values,
        title=titulo
    )

    fig.update_layout(height=600)

    return fig


def criar_treemap(
    df: pd.DataFrame,
    path: List[str],
    values: str,
    titulo: str = ''
) -> go.Figure:
    """
    Cria gráfico treemap

    Args:
        df: DataFrame
        path: Lista de colunas para hierarquia
        values: Coluna de valores
        titulo: Título

    Returns:
        Figure Plotly
    """
    fig = px.treemap(
        df,
        path=path,
        values=values,
        title=titulo
    )

    fig.update_layout(height=600)
    fig.update_traces(textinfo="label+value+percent parent")

    return fig
