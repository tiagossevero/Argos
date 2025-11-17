"""
ARGOS - Gerador Automático de Data Schemas
Script para gerar DESCRIBE FORMATTED e SELECT LIMIT 10 de todas as tabelas do projeto
"""

from pyspark.sql import SparkSession
import pandas as pd
from datetime import datetime
import os

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Lista completa de tabelas a serem documentadas
TABELAS = {
    'ORIGINAIS': [
        'nfce.nfce',
        'niat.argos_cnpj',
        'niat.tabela_niat',
        'usr_sat_ods.vw_ods_contrib'
    ],
    'INTERMEDIARIAS': [
        'niat.argos_nfce_base_extraida',
        'niat.argos_nfce_periodo_base',
        'niat.argos_medias_historicas_produto',
        'niat.argos_mudanca_comportamento'
    ],
    'VIEWS': [
        'niat.argos_vw_evolucao_nfce'
    ]
}

# Diretório de saída para os schemas
OUTPUT_DIR = './data-schemas'

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def criar_diretorio_saida():
    """Cria diretório de saída se não existir"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✅ Diretório criado: {OUTPUT_DIR}")

def obter_nome_arquivo(tabela_completa):
    """Converte nome da tabela em nome de arquivo"""
    # niat.argos_vw_evolucao_nfce -> argos_vw_evolucao_nfce
    nome = tabela_completa.split('.')[-1]
    return f"{nome}_schema.txt"

def formatar_header(titulo, char='='):
    """Formata header para os arquivos"""
    linha = char * 80
    return f"\n{linha}\n{titulo.center(80)}\n{linha}\n"

def salvar_schema(tabela, describe_df, sample_df, categoria):
    """Salva schema completo em arquivo"""
    nome_arquivo = obter_nome_arquivo(tabela)
    caminho_completo = os.path.join(OUTPUT_DIR, nome_arquivo)

    with open(caminho_completo, 'w', encoding='utf-8') as f:
        # Header do arquivo
        f.write(formatar_header(f'DATA SCHEMA - {tabela}'))
        f.write(f"\nCategoria: {categoria}\n")
        f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Tabela: {tabela}\n")

        # DESCRIBE FORMATTED
        f.write(formatar_header('DESCRIBE FORMATTED', '-'))
        f.write("\n```sql\n")
        f.write(f"DESCRIBE FORMATTED {tabela};\n")
        f.write("```\n\n")

        # Converter DataFrame para string formatada
        describe_str = describe_df.toPandas().to_string(index=False, max_rows=None)
        f.write(describe_str)
        f.write("\n")

        # SELECT LIMIT 10
        f.write(formatar_header('SELECT * FROM ... LIMIT 10', '-'))
        f.write("\n```sql\n")
        f.write(f"SELECT * FROM {tabela} LIMIT 10;\n")
        f.write("```\n\n")

        # Converter sample para string formatada
        sample_str = sample_df.toPandas().to_string(index=False, max_rows=None)
        f.write(sample_str)
        f.write("\n")

        # Footer
        f.write(formatar_header('FIM DO SCHEMA', '='))

    print(f"✅ Schema salvo: {caminho_completo}")

# ============================================================================
# FUNÇÃO PRINCIPAL DE EXTRAÇÃO
# ============================================================================

def extrair_schema_tabela(spark, tabela, categoria):
    """
    Extrai schema e dados de exemplo de uma tabela

    Args:
        spark: SparkSession
        tabela: Nome completo da tabela (schema.tabela)
        categoria: Categoria da tabela (ORIGINAIS, INTERMEDIARIAS, VIEWS)
    """
    print(f"\n{'='*80}")
    print(f"Processando: {tabela} ({categoria})")
    print(f"{'='*80}")

    try:
        # 1. DESCRIBE FORMATTED
        print(f"⏳ Executando DESCRIBE FORMATTED {tabela}...")
        describe_query = f"DESCRIBE FORMATTED {tabela}"
        describe_df = spark.sql(describe_query)
        print(f"✅ DESCRIBE obtido - {describe_df.count()} linhas")

        # 2. SELECT LIMIT 10
        print(f"⏳ Executando SELECT * FROM {tabela} LIMIT 10...")
        sample_query = f"SELECT * FROM {tabela} LIMIT 10"
        sample_df = spark.sql(sample_query)

        # Contar colunas
        num_colunas = len(sample_df.columns)
        print(f"✅ Sample obtido - {num_colunas} colunas")

        # 3. Salvar em arquivo
        print(f"💾 Salvando schema em arquivo...")
        salvar_schema(tabela, describe_df, sample_df, categoria)

        return True

    except Exception as e:
        print(f"❌ ERRO ao processar {tabela}: {str(e)}")

        # Salvar erro em arquivo
        nome_arquivo = obter_nome_arquivo(tabela)
        caminho_erro = os.path.join(OUTPUT_DIR, f"ERRO_{nome_arquivo}")

        with open(caminho_erro, 'w', encoding='utf-8') as f:
            f.write(formatar_header(f'ERRO - {tabela}'))
            f.write(f"\nCategoria: {categoria}\n")
            f.write(f"Erro em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\nMensagem de erro:\n{str(e)}\n")

        print(f"⚠️  Erro salvo em: {caminho_erro}")
        return False

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def gerar_todos_schemas(spark):
    """
    Gera schemas para todas as tabelas definidas

    Args:
        spark: SparkSession ativa
    """
    print("\n" + "="*80)
    print("ARGOS - GERADOR AUTOMÁTICO DE DATA SCHEMAS".center(80))
    print("="*80)

    # Criar diretório de saída
    criar_diretorio_saida()

    # Contadores
    total_tabelas = sum(len(tabelas) for tabelas in TABELAS.values())
    processadas = 0
    sucesso = 0
    falhas = 0

    # Processar cada categoria
    for categoria, lista_tabelas in TABELAS.items():
        print(f"\n{'#'*80}")
        print(f"CATEGORIA: {categoria}".center(80))
        print(f"{'#'*80}")

        for tabela in lista_tabelas:
            processadas += 1
            resultado = extrair_schema_tabela(spark, tabela, categoria)

            if resultado:
                sucesso += 1
            else:
                falhas += 1

            print(f"\n📊 Progresso: {processadas}/{total_tabelas} tabelas processadas")

    # Resumo final
    print("\n" + "="*80)
    print("RESUMO FINAL".center(80))
    print("="*80)
    print(f"✅ Total de tabelas: {total_tabelas}")
    print(f"✅ Processadas com sucesso: {sucesso}")
    print(f"❌ Falhas: {falhas}")
    print(f"📁 Arquivos salvos em: {OUTPUT_DIR}")
    print("="*80 + "\n")

    # Gerar índice de schemas
    gerar_indice_schemas()

# ============================================================================
# GERAÇÃO DE ÍNDICE
# ============================================================================

def gerar_indice_schemas():
    """Gera arquivo índice com lista de todos os schemas gerados"""
    indice_path = os.path.join(OUTPUT_DIR, 'README.md')

    with open(indice_path, 'w', encoding='utf-8') as f:
        f.write("# ARGOS - Data Schemas\n\n")
        f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        f.write("## Estrutura de Dados\n\n")
        f.write("Este diretório contém os schemas completos de todas as tabelas utilizadas no projeto ARGOS.\n\n")

        # Listar por categoria
        for categoria, lista_tabelas in TABELAS.items():
            f.write(f"### {categoria}\n\n")

            for tabela in lista_tabelas:
                nome_arquivo = obter_nome_arquivo(tabela)
                nome_exibicao = tabela.split('.')[-1]
                f.write(f"- **{tabela}** → [`{nome_arquivo}`](./{nome_arquivo})\n")

            f.write("\n")

        # Informações adicionais
        f.write("---\n\n")
        f.write("## Formato dos Arquivos\n\n")
        f.write("Cada arquivo contém:\n\n")
        f.write("1. **DESCRIBE FORMATTED** - Estrutura completa da tabela\n")
        f.write("2. **SELECT LIMIT 10** - Amostra de 10 registros\n\n")

        f.write("## Como Usar\n\n")
        f.write("```python\n")
        f.write("# Para regenerar todos os schemas:\n")
        f.write("from gerar_data_schemas import gerar_todos_schemas\n")
        f.write("gerar_todos_schemas(spark)\n")
        f.write("```\n")

    print(f"📝 Índice gerado: {indice_path}")

# ============================================================================
# EXECUÇÃO STANDALONE
# ============================================================================

if __name__ == "__main__":
    print("\n⚠️  INSTRUÇÕES DE USO:\n")
    print("Este script deve ser executado em um ambiente PySpark.")
    print("Certifique-se de ter uma SparkSession ativa.\n")
    print("Exemplo de uso:\n")
    print("  1. Em um notebook Jupyter/Databricks:")
    print("     %run gerar_data_schemas.py")
    print("     gerar_todos_schemas(spark)")
    print("\n  2. Via PySpark shell:")
    print("     execfile('gerar_data_schemas.py')")
    print("     gerar_todos_schemas(spark)")
    print("\n  3. Importando como módulo:")
    print("     from gerar_data_schemas import gerar_todos_schemas")
    print("     gerar_todos_schemas(spark)")
    print("\n" + "="*80 + "\n")
