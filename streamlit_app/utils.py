"""
ARGOS - Sistema de Análise de Mudança de Comportamento Tributário
Módulo de Funções Utilitárias
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime
from typing import Any, Dict, List, Optional
import base64

from config import (
    FORMAT_CONFIG, CLASSIFICACOES, MOVIMENTOS, ALERT_LEVELS,
    MESSAGES, AUTH_CONFIG
)


# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

def check_password() -> bool:
    """
    Verifica senha de acesso

    Returns:
        True se autenticado, False caso contrário
    """
    def password_entered():
        """Callback para verificar senha"""
        if st.session_state["password"] == AUTH_CONFIG['password']:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # Primeira execução ou não autenticado
    if "password_correct" not in st.session_state:
        st.text_input(
            "Digite a senha:",
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False

    # Senha incorreta
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Digite a senha:",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😕 Senha incorreta")
        return False

    # Senha correta
    else:
        return True


# ============================================================================
# FORMATAÇÃO
# ============================================================================

def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ para exibição"""
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


def formatar_percentual(valor: float, decimais: int = 2) -> str:
    """Formata valor como percentual"""
    if pd.isna(valor):
        return f'0,{"0" * decimais}%'
    return f"{valor:.{decimais}f}%".replace('.', ',')


def formatar_numero(valor: float, decimais: int = 0) -> str:
    """Formata número com separadores"""
    if pd.isna(valor):
        return '0'
    if decimais == 0:
        return f"{valor:,.0f}".replace(',', '.')
    else:
        return f"{valor:,.{decimais}f}".replace(',', '_').replace('.', ',').replace('_', '.')


# ============================================================================
# MÉTRICAS E KPIs
# ============================================================================

def exibir_metrica_customizada(
    label: str,
    valor: Any,
    delta: Optional[float] = None,
    formato: str = 'numero',
    cor_fundo: str = '#f0f2f6',
    cor_texto: str = '#262730'
):
    """
    Exibe métrica customizada com estilo

    Args:
        label: Label da métrica
        valor: Valor da métrica
        delta: Variação (opcional)
        formato: Tipo de formatação
        cor_fundo: Cor de fundo
        cor_texto: Cor do texto
    """
    # Formatar valor
    if formato == 'moeda':
        valor_fmt = formatar_moeda(valor)
    elif formato == 'percentual':
        valor_fmt = formatar_percentual(valor)
    else:
        valor_fmt = formatar_numero(valor)

    # Formatar delta
    delta_html = ''
    if delta is not None:
        delta_cor = '#28a745' if delta >= 0 else '#dc3545'
        delta_sinal = '+' if delta >= 0 else ''
        delta_html = f'<div style="color: {delta_cor}; font-size: 0.9em;">{delta_sinal}{formatar_percentual(delta)}</div>'

    # HTML customizado
    html = f"""
    <div style="
        background-color: {cor_fundo};
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid {cor_texto};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <div style="color: {cor_texto}; font-size: 0.9em; margin-bottom: 5px;">{label}</div>
        <div style="color: {cor_texto}; font-size: 2em; font-weight: bold;">{valor_fmt}</div>
        {delta_html}
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def criar_card_info(titulo: str, conteudo: str, cor: str = '#1f77b4'):
    """
    Cria card informativo

    Args:
        titulo: Título do card
        conteudo: Conteúdo do card
        cor: Cor de destaque
    """
    html = f"""
    <div style="
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid {cor};
        margin: 10px 0;
    ">
        <h4 style="margin: 0 0 10px 0; color: {cor};">{titulo}</h4>
        <p style="margin: 0; color: #262730;">{conteudo}</p>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


# ============================================================================
# BADGES E LABELS
# ============================================================================

def criar_badge(texto: str, cor: str = '#6c757d') -> str:
    """
    Cria badge HTML

    Args:
        texto: Texto do badge
        cor: Cor do badge

    Returns:
        HTML do badge
    """
    return f"""
    <span style="
        background-color: {cor};
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 500;
        display: inline-block;
        margin: 2px;
    ">{texto}</span>
    """


def obter_badge_classificacao(classificacao: str) -> str:
    """Retorna badge HTML para classificação"""
    config = CLASSIFICACOES.get(classificacao, {})
    label = config.get('label', classificacao)
    cor = config.get('color', '#6c757d')
    icon = config.get('icon', '')

    return criar_badge(f"{icon} {label}", cor)


def obter_badge_movimento(movimento: str) -> str:
    """Retorna badge HTML para movimento"""
    config = MOVIMENTOS.get(movimento, {})
    label = config.get('label', movimento)
    cor = config.get('color', '#6c757d')
    icon = config.get('icon', '')

    return criar_badge(f"{icon} {label}", cor)


def obter_badge_alerta(nivel: str) -> str:
    """Retorna badge HTML para nível de alerta"""
    config = ALERT_LEVELS.get(nivel, {})
    label = config.get('label', nivel)
    cor = config.get('color', '#6c757d')
    icon = config.get('icon', '')

    return criar_badge(f"{icon} {label}", cor)


# ============================================================================
# EXPORTAÇÃO
# ============================================================================

def exportar_dataframe_excel(df: pd.DataFrame, nome_arquivo: str = 'relatorio.xlsx') -> bytes:
    """
    Exporta DataFrame para Excel

    Args:
        df: DataFrame para exportar
        nome_arquivo: Nome do arquivo

    Returns:
        Bytes do arquivo Excel
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')

        # Auto-ajustar largura das colunas
        worksheet = writer.sheets['Dados']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(str(col))
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)

    return output.getvalue()


def exportar_dataframe_csv(df: pd.DataFrame) -> bytes:
    """
    Exporta DataFrame para CSV

    Args:
        df: DataFrame para exportar

    Returns:
        Bytes do arquivo CSV
    """
    return df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')


def criar_link_download(data: bytes, filename: str, label: str = 'Download'):
    """
    Cria botão de download

    Args:
        data: Dados para download
        filename: Nome do arquivo
        label: Label do botão
    """
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" style="text-decoration: none;"><button style="background-color: #1f77b4; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">{label}</button></a>'
    st.markdown(href, unsafe_allow_html=True)


# ============================================================================
# FILTROS E SELEÇÕES
# ============================================================================

def criar_filtro_periodo(key: str = 'filtro_periodo') -> tuple:
    """
    Cria seletor de período

    Args:
        key: Key para o widget

    Returns:
        Tupla (periodo_inicio, periodo_fim)
    """
    col1, col2 = st.columns(2)

    with col1:
        periodo_inicio = st.date_input(
            'Período Inicial',
            value=datetime(2023, 1, 1),
            key=f'{key}_inicio'
        )

    with col2:
        periodo_fim = st.date_input(
            'Período Final',
            value=datetime.now(),
            key=f'{key}_fim'
        )

    # Converter para formato YYYY-MM
    periodo_inicio_str = periodo_inicio.strftime('%Y-%m')
    periodo_fim_str = periodo_fim.strftime('%Y-%m')

    return periodo_inicio_str, periodo_fim_str


def criar_filtro_multiplo(
    df: pd.DataFrame,
    coluna: str,
    label: str,
    key: str,
    default: Optional[List] = None
) -> List:
    """
    Cria filtro de seleção múltipla

    Args:
        df: DataFrame
        coluna: Nome da coluna
        label: Label do filtro
        key: Key única do widget
        default: Valores padrão

    Returns:
        Lista de valores selecionados
    """
    opcoes = sorted(df[coluna].unique().tolist())

    if default is None:
        default = opcoes

    selecionados = st.multiselect(
        label,
        options=opcoes,
        default=default,
        key=key
    )

    return selecionados


# ============================================================================
# TABELAS
# ============================================================================

def estilizar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica estilos ao DataFrame para exibição

    Args:
        df: DataFrame para estilizar

    Returns:
        DataFrame estilizado
    """
    # Formatar colunas específicas
    df_styled = df.copy()

    for col in df_styled.columns:
        col_lower = col.lower()

        if 'cnpj' in col_lower:
            df_styled[col] = df_styled[col].apply(lambda x: formatar_cnpj(x) if pd.notna(x) else '')

        elif any(word in col_lower for word in ['bc_', 'valor', 'base']):
            df_styled[col] = df_styled[col].apply(lambda x: formatar_moeda(x) if pd.notna(x) else '')

        elif any(word in col_lower for word in ['taxa', 'percentual', 'correcao']):
            df_styled[col] = df_styled[col].apply(lambda x: formatar_percentual(x) if pd.notna(x) else '')

        elif any(word in col_lower for word in ['tarifa', 'media', 'desvio']):
            df_styled[col] = df_styled[col].apply(lambda x: formatar_numero(x, 2) if pd.notna(x) else '')

    return df_styled


def exibir_tabela_interativa(
    df: pd.DataFrame,
    altura: int = 400,
    colunas_ocultar: Optional[List[str]] = None
):
    """
    Exibe tabela interativa com Streamlit

    Args:
        df: DataFrame para exibir
        altura: Altura da tabela
        colunas_ocultar: Lista de colunas para ocultar
    """
    df_exibir = df.copy()

    if colunas_ocultar:
        df_exibir = df_exibir.drop(columns=colunas_ocultar, errors='ignore')

    st.dataframe(
        df_exibir,
        use_container_width=True,
        height=altura
    )


# ============================================================================
# MENSAGENS E NOTIFICAÇÕES
# ============================================================================

def exibir_alerta(mensagem: str, tipo: str = 'info'):
    """
    Exibe alerta customizado

    Args:
        mensagem: Mensagem do alerta
        tipo: 'success', 'info', 'warning', 'error'
    """
    if tipo == 'success':
        st.success(mensagem)
    elif tipo == 'warning':
        st.warning(mensagem)
    elif tipo == 'error':
        st.error(mensagem)
    else:
        st.info(mensagem)


def exibir_spinner(mensagem: str = None):
    """
    Context manager para exibir spinner

    Args:
        mensagem: Mensagem do spinner

    Usage:
        with exibir_spinner("Carregando..."):
            # código
    """
    return st.spinner(mensagem or MESSAGES['loading'])


# ============================================================================
# VALIDAÇÃO
# ============================================================================

def validar_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ (apenas formato)

    Args:
        cnpj: CNPJ para validar

    Returns:
        True se válido, False caso contrário
    """
    if not cnpj:
        return False

    # Remover formatação
    cnpj_numeros = ''.join(filter(str.isdigit, cnpj))

    return len(cnpj_numeros) == 14


def validar_periodo(periodo: str) -> bool:
    """
    Valida formato de período (YYYY-MM)

    Args:
        periodo: Período para validar

    Returns:
        True se válido, False caso contrário
    """
    try:
        datetime.strptime(periodo, '%Y-%m')
        return True
    except:
        return False


# ============================================================================
# HELPERS
# ============================================================================

def formatar_tempo_decorrido(segundos: float) -> str:
    """
    Formata tempo decorrido

    Args:
        segundos: Tempo em segundos

    Returns:
        String formatada (ex: "2m 35s")
    """
    if segundos < 60:
        return f"{segundos:.1f}s"
    elif segundos < 3600:
        minutos = int(segundos // 60)
        segs = int(segundos % 60)
        return f"{minutos}m {segs}s"
    else:
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        return f"{horas}h {minutos}m"


def truncar_texto(texto: str, max_length: int = 50) -> str:
    """
    Trunca texto com reticências

    Args:
        texto: Texto para truncar
        max_length: Comprimento máximo

    Returns:
        Texto truncado
    """
    if pd.isna(texto) or texto is None:
        return ''

    texto_str = str(texto)

    if len(texto_str) <= max_length:
        return texto_str

    return texto_str[:max_length - 3] + '...'


def obter_cor_gradiente(valor: float, min_val: float, max_val: float) -> str:
    """
    Retorna cor em gradiente baseada no valor

    Args:
        valor: Valor atual
        min_val: Valor mínimo
        max_val: Valor máximo

    Returns:
        Cor em formato hex
    """
    if max_val == min_val:
        return '#ffff00'

    # Normalizar valor entre 0 e 1
    norm = (valor - min_val) / (max_val - min_val)
    norm = max(0, min(1, norm))

    # Verde -> Amarelo -> Vermelho
    if norm < 0.5:
        # Verde para Amarelo
        r = int(255 * (norm * 2))
        g = 255
    else:
        # Amarelo para Vermelho
        r = 255
        g = int(255 * (2 - norm * 2))

    return f'#{r:02x}{g:02x}00'
