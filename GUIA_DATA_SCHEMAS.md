# 📊 Guia Rápido - Geração de Data Schemas

Este guia explica como gerar automaticamente os schemas de todas as tabelas do projeto ARGOS.

---

## 🎯 Objetivo

Gerar arquivos de documentação contendo:
- `DESCRIBE FORMATTED` - estrutura completa de cada tabela
- `SELECT * FROM ... LIMIT 10` - amostra de dados reais

---

## 📋 Tabelas que serão documentadas

### Tabelas Originais (4)
- `nfce.nfce` - Dados brutos de NFC-e
- `niat.argos_cnpj` - Lista de CNPJs monitorados
- `niat.tabela_niat` - Alíquotas esperadas (IA)
- `usr_sat_ods.vw_ods_contrib` - View de contribuintes

### Tabelas Intermediárias (4)
- `niat.argos_nfce_base_extraida` - Base extraída e flattenida
- `niat.argos_nfce_periodo_base` - Alíquotas ponderadas por período
- `niat.argos_medias_historicas_produto` - Médias históricas
- `niat.argos_mudanca_comportamento` - Análise de mudanças

### Views (1)
- `niat.argos_vw_evolucao_nfce` ⭐ **MAIS IMPORTANTE** - usada em todo o Streamlit

**Total: 9 tabelas/views**

---

## 🚀 Como Usar

### Opção 1: Notebook Jupyter (RECOMENDADO)

1. Abra o notebook:
   ```bash
   jupyter notebook Gerar_Data_Schemas.ipynb
   ```

2. Execute as células na ordem:
   - Células 1-5: Configuração e funções auxiliares
   - Célula 6: **EXECUTAR TUDO DE UMA VEZ** (recomendado)
   - OU Células 7-8: Executar por categoria (opcional)

3. Os schemas serão salvos em `./data-schemas/`

### Opção 2: Script Python

```python
# Em um notebook PySpark ou PySpark shell:
from gerar_data_schemas import gerar_todos_schemas

# Executar
gerar_todos_schemas(spark)
```

### Opção 3: Comandos Manuais

Se preferir executar manualmente, use o padrão:

```python
# DESCRIBE FORMATTED
describe_df = spark.sql("DESCRIBE FORMATTED niat.argos_vw_evolucao_nfce")
describe_df.show(1000, truncate=False)

# SELECT LIMIT 10
sample_df = spark.sql("SELECT * FROM niat.argos_vw_evolucao_nfce LIMIT 10")
sample_df.show(10, truncate=False)
```

---

## 📁 Estrutura de Saída

Após a execução, será criado o diretório `data-schemas/` com:

```
data-schemas/
├── README.md                                    # Índice de todos os schemas
│
├── nfce_schema.txt                             # Schema: nfce.nfce
├── argos_cnpj_schema.txt                       # Schema: niat.argos_cnpj
├── tabela_niat_schema.txt                      # Schema: niat.tabela_niat
├── vw_ods_contrib_schema.txt                   # Schema: usr_sat_ods.vw_ods_contrib
│
├── argos_nfce_base_extraida_schema.txt         # Schema: niat.argos_nfce_base_extraida
├── argos_nfce_periodo_base_schema.txt          # Schema: niat.argos_nfce_periodo_base
├── argos_medias_historicas_produto_schema.txt  # Schema: niat.argos_medias_historicas_produto
├── argos_mudanca_comportamento_schema.txt      # Schema: niat.argos_mudanca_comportamento
│
└── argos_vw_evolucao_nfce_schema.txt          # Schema: niat.argos_vw_evolucao_nfce ⭐
```

---

## 📄 Formato dos Arquivos Gerados

Cada arquivo `*_schema.txt` contém:

```
================================================================================
                        DATA SCHEMA - niat.argos_vw_evolucao_nfce
================================================================================

Categoria: VIEWS
Gerado em: 2025-11-17 10:30:00
Tabela: niat.argos_vw_evolucao_nfce

--------------------------------------------------------------------------------
                            DESCRIBE FORMATTED
--------------------------------------------------------------------------------

```sql
DESCRIBE FORMATTED niat.argos_vw_evolucao_nfce;
```

col_name        data_type       comment
cnpj            string          NULL
periodo         string          NULL
gtin            string          NULL
...

--------------------------------------------------------------------------------
                          SELECT * FROM ... LIMIT 10
--------------------------------------------------------------------------------

```sql
SELECT * FROM niat.argos_vw_evolucao_nfce LIMIT 10;
```

cnpj              periodo    gtin          ncm       produto         ...
00000000000001    202401     7891000000001 12345678  Produto X      ...
00000000000002    202401     7891000000002 87654321  Produto Y      ...
...

================================================================================
                              FIM DO SCHEMA
================================================================================
```

---

## ⚙️ Personalização

### Adicionar/Remover Tabelas

Edite o arquivo `gerar_data_schemas.py` ou o notebook, seção de configuração:

```python
TABELAS = {
    'ORIGINAIS': [
        'nfce.nfce',
        'niat.argos_cnpj',
        # Adicione ou remova aqui
    ],
    'INTERMEDIARIAS': [
        # ...
    ],
    'VIEWS': [
        # ...
    ]
}
```

### Alterar Número de Registros de Amostra

Por padrão, são extraídos 10 registros. Para alterar:

```python
# Altere LIMIT 10 para LIMIT 20 (ou outro valor)
sample_query = f"SELECT * FROM {tabela} LIMIT 20"
```

### Alterar Diretório de Saída

```python
# Altere o caminho do diretório
OUTPUT_DIR = './meu_diretorio_schemas'
```

---

## 🔍 Verificação

Após a execução, verifique:

1. **Total de arquivos gerados**:
   ```bash
   ls -la data-schemas/ | wc -l
   # Deve mostrar 10+ arquivos (9 schemas + README.md + possíveis erros)
   ```

2. **Arquivos de erro**:
   ```bash
   ls data-schemas/ERRO_*
   # Se houver arquivos, verifique permissões ou se a tabela existe
   ```

3. **Tamanho dos arquivos**:
   ```bash
   du -h data-schemas/*_schema.txt
   # Cada arquivo deve ter alguns KB
   ```

---

## ❌ Solução de Problemas

### Erro: "Table not found"

**Causa**: Tabela não existe ou você não tem permissão de acesso.

**Solução**:
- Verifique se a tabela existe: `spark.sql("SHOW TABLES IN niat").show()`
- Verifique permissões com seu administrador de banco de dados

### Erro: "SparkSession not found"

**Causa**: O script está sendo executado fora de um ambiente PySpark.

**Solução**:
- Use o notebook Jupyter conectado ao cluster PySpark
- OU execute via `pyspark` shell
- OU inicie uma SparkSession manualmente

### Arquivos muito pequenos ou vazios

**Causa**: Tabela existe mas está vazia.

**Solução**:
- Verifique se a tabela tem dados: `spark.sql("SELECT COUNT(*) FROM tabela").show()`
- Se estiver vazia, isso é esperado e o arquivo refletirá essa condição

---

## 📊 Exemplo de Uso Completo

```python
# 1. Importar bibliotecas
from pyspark.sql import SparkSession
from gerar_data_schemas import gerar_todos_schemas

# 2. Verificar SparkSession (já deve estar ativa em notebooks)
print(f"Spark version: {spark.version}")

# 3. Executar geração
gerar_todos_schemas(spark)

# 4. Verificar arquivos gerados
import os
arquivos = os.listdir('./data-schemas')
print(f"Total de arquivos gerados: {len(arquivos)}")
for arquivo in sorted(arquivos):
    print(f"  - {arquivo}")
```

---

## 📝 Checklist de Execução

- [ ] Ambiente PySpark ativo
- [ ] Acesso ao banco de dados Impala configurado
- [ ] Permissões de leitura nas tabelas
- [ ] Notebook ou script copiado para o ambiente
- [ ] Execução concluída sem erros
- [ ] Arquivos gerados em `./data-schemas/`
- [ ] README.md criado com índice
- [ ] Todos os schemas revisados

---

## 🎯 Próximos Passos

Após gerar os schemas:

1. **Revisar os arquivos** em `./data-schemas/`
2. **Verificar estruturas** - conferir se os campos estão corretos
3. **Documentar descobertas** - adicionar comentários sobre campos importantes
4. **Compartilhar** - distribuir para equipe de desenvolvimento
5. **Versionamento** - fazer commit dos schemas no repositório Git

---

## 📚 Referências

- **Script Python**: `gerar_data_schemas.py`
- **Notebook Jupyter**: `Gerar_Data_Schemas.ipynb`
- **Documentação PySpark SQL**: https://spark.apache.org/docs/latest/sql-getting-started.html
- **README do projeto**: `README.md`

---

**Última atualização**: 2025-11-17
**Autor**: Sistema ARGOS
**Versão**: 1.0
