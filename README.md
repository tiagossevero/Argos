# ARGOS - Sistema de Análise de Mudança de Comportamento Tributário

## Visão Geral

**ARGOS** (Análise de Mudança de Comportamento Tributário) é um sistema inteligente de monitoramento e análise de comportamento tributário desenvolvido para a Receita Estadual de Santa Catarina. O sistema detecta variações anormais nas alíquotas de ICMS praticadas por empresas, comparando-as com históricos e valores de referência, para identificar potenciais irregularidades fiscais.

### Objetivo Principal

Monitorar comportamentos tributários suspeitos através de análise estatística de dados de NFC-e (Nota Fiscal de Consumidor Eletrônica), comparando alíquotas praticadas com valores esperados/históricos e identificando empresas e produtos com maiores riscos para priorização de ações de fiscalização.

## Características Principais

### 1. **Dashboard Executivo** 📊
- Visualização de KPIs principais (total de registros, empresas monitoradas, taxa de correção)
- Distribuição por classificação de mudança (extrema, significativa, normal)
- Análise de movimento vs alíquota correta
- Evolução temporal de casos e empresas
- Métricas de base de cálculo total (ICMS)

### 2. **Ranking de Empresas** 🏆
- Top empresas por múltiplas métricas (taxa de correção, mudanças extremas, base de cálculo)
- Ordenação configurável (crescente/decrescente)
- Filtros dinâmicos por período
- Visualização de taxonomia de dados

### 3. **Análise de Produtos** 📦
- Identificação de produtos com maior volatilidade de alíquotas
- Análise de desvio padrão de alíquotas praticadas
- Comparação entre empresas para mesmo produto
- Identificação de produtos problemáticos com múltiplas variações

### 4. **Análise Setorial** 🏭
- Análise por NCM (Nomenclatura Comum do Mercosul) - 2 dígitos
- Identificação de setores críticos
- Taxa de correção por setor
- Evolução temporal por setor

### 5. **Drill-Down por Empresa** 🔬
- Análise detalhada de empresa específica
- Evolução temporal de comportamento
- Top produtos por empresa
- Distribuição de classificações e movimentos
- Carregamento sob demanda de dados completos

### 6. **Análise Comparativa Temporal** ⏱️
- Comparação entre períodos (primeiros vs últimos 6 meses)
- Variação percentual de métricas-chave
- Tendências de melhoria ou piora
- Interpretação automática de resultados

### 7. **Sistema de Alertas** 🚨
- Scoring automático de empresas por risco
- Níveis de alerta (BAIXO, MÉDIO, ALTO, CRÍTICO, EMERGENCIAL)
- Matriz de priorização (Score vs Impacto Financeiro)
- Weights configuráveis para componentes do score

## Arquitetura e Tecnologias

### Stack Tecnológico

| Componente | Tecnologia | Uso |
|-----------|-----------|-----|
| **ETL & Processamento** | PySpark 3.x | Processamento distribuído de dados grandes |
| **Dados** | Impala (HDFS) | Data warehouse SQL em Hadoop |
| **Dashboard Web** | Streamlit | Interface web interativa |
| **Visualizações** | Plotly | Gráficos interativos |
| **Análise de Dados** | Pandas, NumPy | Manipulação e cálculos de dados |
| **Autenticação** | Session State (Streamlit) | Proteção com senha |
| **Linguagem** | Python 3.10+ | Desenvolvimento |

### Arquitetura de Dados

```
NFC-e (nfce.nfce)
    ↓
Extração e Flattening
    ↓
argos_nfce_base_extraida (tabela base de produtos)
    ↓
Cálculo de Alíquotas Ponderadas
    ↓
argos_nfce_periodo_base (alíquotas por período)
    ↓
Cálculo de Médias Históricas
    ↓
argos_medias_historicas_produto (média histórica por empresa-produto)
    ↓
Análise de Mudanças de Comportamento
    ↓
argos_mudanca_comportamento (tabela final com classificações)
    ↓
argos_vw_evolucao_nfce (view para consultas)
```

## Estrutura do Projeto

```
/home/user/Argos/
├── README.md                          # Este arquivo
├── ARGOSCA.py                         # Aplicação Streamlit (Dashboard)
├── ARGOSC.ipynb                       # Notebook principal de análise (PySpark)
├── ARGOSC-Exemplo.ipynb              # Notebook exemplo/demonstração
└── ARGOS INDIVIDUAL.json             # Metadados de configuração (Hue)
```

### Descrição dos Arquivos

#### 1. **ARGOSCA.py** (Dashboard Streamlit)
- **Tamanho**: ~62 KB
- **Linhas**: 1.672 linhas
- **Tipo**: Aplicação Web Streamlit
- **Funcionalidades**:
  - Interface web interativa
  - 7 páginas de análise diferentes
  - Cache de dados agregados (TTL 3600s)
  - Carregamento sob demanda de dados detalhados
  - Autenticação por senha
  - Estilos CSS customizados
  - Integração com banco Impala
  - Cálculos de KPIs e métricas

**Dependências principais**:
```python
- streamlit
- pandas
- numpy
- plotly (express, graph_objects, subplots)
- sqlalchemy
- impala (pyodbc/ImpalaDB driver)
```

#### 2. **ARGOSC.ipynb** (Análise PySpark)
- **Tamanho**: ~2.2 MB
- **Células**: 18 código/análise
- **Tipo**: Jupyter Notebook
- **Funcionalidades**:
  - Carregamento e verificação de dados
  - Análise de distribuição por classificação
  - Análise de movimento vs alíquota correta
  - Evolução temporal
  - Ranking de empresas
  - Análise setorial
  - Análise de produtos
  - Casos críticos e alertas
  - Visualizações com Matplotlib/Seaborn

**Dependências principais**:
```python
- pyspark
- pandas
- numpy
- matplotlib
- seaborn
- sqlalchemy
```

#### 3. **ARGOSC-Exemplo.ipynb** (Notebook Exemplo)
- **Tamanho**: ~69 KB
- **Células**: 18 código/análise
- **Tipo**: Jupyter Notebook (versão exemplo/demo)
- **Conteúdo**: Mesma estrutura do ARGOSC.ipynb mas com dados de exemplo

#### 4. **ARGOS INDIVIDUAL.json** (Metadados)
- **Tamanho**: ~179 KB
- **Tipo**: JSON (Metadados de Hue)
- **Conteúdo**: Configurações de query, documentos, metadados de ambiente

## Configuração e Execução

### Pré-requisitos

1. **Python 3.10+**
   ```bash
   python --version  # Verificar versão
   ```

2. **Dependências Python**
   ```bash
   pip install -r requirements.txt
   ```

   Principais dependências:
   - `streamlit>=1.0.0`
   - `pandas>=1.3.0`
   - `numpy>=1.20.0`
   - `plotly>=5.0.0`
   - `sqlalchemy>=1.4.0`
   - `impala-connector` ou equivalente

3. **Acesso ao Banco Impala**
   - Host: `bdaworkernode02.sef.sc.gov.br`
   - Port: `21050`
   - Database: `niat`
   - Credenciais: Configuradas em `~/.streamlit/secrets.toml`

4. **Jupyter Kernel (para notebooks)**
   - PySpark disponível
   - Conda environment com `conda_data_pipeline`

### Instalação

```bash
# Clonar repositório (se aplicável)
git clone <repository-url>
cd Argos

# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install streamlit pandas numpy plotly sqlalchemy

# Para Impala (verificar versão específica da sua instalação)
pip install impyla
```

### Configuração de Credenciais

Crie arquivo `~/.streamlit/secrets.toml`:

```toml
[impala_credentials]
user = "seu_usuario"
password = "sua_senha"
```

### Execução do Dashboard

```bash
streamlit run ARGOSCA.py
```

O dashboard estará disponível em: `http://localhost:8501`

### Execução dos Notebooks

```bash
jupyter notebook ARGOSC.ipynb
```

## Modelos e Algoritmos

### Classificação de Mudança de Comportamento

Classificação baseada em desvio padrão histórico:

```
- PRODUTO_ESTÁVEL: Sem variação histórica
- COMPORTAMENTO_NORMAL: Variação <= 1σ (desvio padrão)
- MUDANÇA_SIGNIFICATIVA: Variação entre 1σ e 2σ
- MUDANÇA_EXTREMA: Variação > 2σ
```

### Movimento vs Alíquota Correta (IA)

Comparação com valores esperados:

```
- APROXIMOU_DA_CORRETA: Alíquota se aproximou do valor esperado
- AFASTOU_DA_CORRETA: Alíquota se distanciou do valor esperado
- MANTEVE_DISTANCIA: Distância mantida
- SEM_REFERÊNCIA_IA: Sem valor de referência disponível
```

### Scoring de Risco (Sistema de Alertas)

Score total = (Taxa Mudanças Extremas × Peso_Classificação) + (Taxa Afastamento × Peso_Movimento) + (|Diferença vs IA| × Peso_Magnitude)

**Weights padrão** (configuráveis):
- Classificação: 40%
- Movimento: 30%
- Magnitude: 20%

**Níveis de Alerta**:
- BAIXO: Score 0-35
- MÉDIO: Score 35-50
- ALTO: Score 50-65
- CRÍTICO: Score 65-80
- EMERGENCIAL: Score 80+

## Fonte de Dados

### Tabelas Principais

1. **nfce.nfce**: Dados brutos de NFC-e (Nota Fiscal de Consumidor Eletrônica)
   - Estrutura aninhada (JSON)
   - Contém detalhes de produtos, impostos, valores

2. **niat.argos_cnpj**: Lista de CNPJs fiscalizados/monitorados

3. **niat.tabela_niat**: Tabela de alíquotas esperadas (IA) por GTIN/NCM

4. **usr_sat_ods.vw_ods_contrib**: View de contribuintes (razão social)

### Tabelas Intermediárias (criadas pelo ETL)

1. **niat.argos_nfce_base_extraida**: Base extraída e flattenida
   - ~1.7M+ registros
   - Campos: cnpj, periodo, gtin, ncm, descrição, bc_fisco, alíquota_emitente

2. **niat.argos_nfce_periodo_base**: Alíquotas ponderadas por período
   - Agregação mensal por empresa-produto
   - Alíquota ponderada = Σ(alíquota × bc) / Σ(bc)

3. **niat.argos_medias_historicas_produto**: Médias históricas
   - Calculadas a partir de 3+ períodos
   - Média e desvio padrão históricos

4. **niat.argos_mudanca_comportamento**: Tabela final com classificações
   - Base para todas as análises
   - Contém todos os cálculos e classificações

### View para Consultas

**niat.argos_vw_evolucao_nfce**: View final para análises
- Dados prontos para consumo
- Alíquotas em percentual (×100)
- Ordenado por empresa, produto, período

## Exemplos de Uso

### Consulta: Top 10 Empresas com Mudanças Extremas

```sql
SELECT 
    nm_razao_social,
    cnpj_emitente,
    COUNT(*) as total_mudancas_extremas,
    COUNT(DISTINCT CONCAT(gtin, '-', ncm)) as produtos_afetados,
    SUM(bc_total_periodo) as base_calculo_total
FROM niat.argos_vw_evolucao_nfce
WHERE classificacao_mudanca = 'MUDANCA_EXTREMA'
  AND LEFT(periodo, 4) = '2024'
GROUP BY nm_razao_social, cnpj_emitente
ORDER BY total_mudancas_extremas DESC
LIMIT 10;
```

### Consulta: Tendência por Período

```sql
SELECT 
    periodo,
    COUNT(*) as total_casos,
    SUM(CASE WHEN classificacao_mudanca = 'MUDANCA_EXTREMA' THEN 1 ELSE 0 END) as mudancas_extremas,
    SUM(CASE WHEN movimento_vs_ia = 'AFASTOU_DA_CORRETA' THEN 1 ELSE 0 END) as afastou_da_correta,
    SUM(bc_total_periodo) as base_calculo_total
FROM niat.argos_vw_evolucao_nfce
WHERE periodo >= '202409'
GROUP BY periodo
ORDER BY periodo DESC;
```

## KPIs e Métricas

### KPIs Principais

| KPI | Descrição | Fórmula |
|-----|-----------|---------|
| **Total de Registros** | Quantidade de casos analisados | COUNT(*) |
| **Empresas Monitoradas** | Quantidade de empresas únicas | COUNT(DISTINCT cnpj) |
| **Taxa de Correção** | % de casos que aproximaram da alíquota correta | APROXIMOU / TOTAL × 100 |
| **Base de Cálculo Total** | ICMS em R$ de todos os registros | SUM(bc_total) |
| **Mudanças Extremas** | Quantidade de casos com mudança > 2σ | COUNT WHERE extrema |
| **Taxa de Extremas** | % de casos com mudança extrema | EXTREMAS / TOTAL × 100 |
| **Diferença Média vs IA** | Distância média da alíquota correta | AVG(\|praticada - ia\|) |

## Fluxo de Dados

```
1. EXTRAÇÃO (nfce.nfce)
   ├─ Filtra NFCs válidas (2023-2025)
   ├─ Filtra empresas fiscalizadas
   └─ Desaninha arrays de produtos

2. TRANSFORMAÇÃO
   ├─ Calcula alíquotas ponderadas
   ├─ Agrega por período
   └─ Enriquece com dados de IA

3. ANÁLISE
   ├─ Calcula médias históricas
   ├─ Identifica mudanças
   └─ Classifica comportamentos

4. APRESENTAÇÃO
   ├─ Dashboard Streamlit
   ├─ Filtros por período/critério
   └─ Exportação de relatórios
```

## Performance e Otimizações

### Cache Estratégico

- **Dados Agregados**: TTL 3600s (1 hora)
  - Carregamento inicial rápido
  - Reduz carga no Impala

- **Detalhes por Empresa**: TTL 1800s (30 minutos)
  - Carregamento sob demanda
  - Consultas otimizadas com LIMIT

### Índices Recomendados (Impala)

```sql
-- Performance de consultas principais
CREATE INDEX idx_periodo ON niat.argos_mudanca_comportamento(periodo);
CREATE INDEX idx_cnpj ON niat.argos_mudanca_comportamento(cnpj_emitente);
CREATE INDEX idx_classificacao ON niat.argos_mudanca_comportamento(classificacao_mudanca);
CREATE INDEX idx_movimento ON niat.argos_mudanca_comportamento(movimento_vs_ia);
```

## Limitações e Considerações

1. **Limitações de Dados**
   - Apenas dados de NFC-e (não cobre outros documentos)
   - Período: 2023-2025
   - Apenas empresas em lista de fiscalização (niat.argos_cnpj)

2. **Performance**
   - Limite de 10.000 registros em consultas de período
   - Agregação em cache para velocidade
   - Carregamento sob demanda para detalhes

3. **Precisão**
   - Requer 3+ períodos para cálculos de média histórica
   - Sensível a mudanças estruturais de alíquotas
   - Dependente da qualidade dos dados de IA

## Desenvolvimento e Manutenção

### Estructura do Código

- **ARGOSCA.py**: Código estruturado em funções por página
  - check_password(): Autenticação
  - get_impala_engine(): Conexão ao banco
  - carregar_dados_*(): Carregamento de dados
  - dashboard_executivo(): Página principal
  - ranking_empresas(): Rankings
  - ... (outras páginas)

### Como Adicionar Nova Página

1. Criar função `minha_nova_pagina(dados, filtros_globais)`
2. Implementar interface Streamlit
3. Adicionar ao dicionário `paginas_funcoes`
4. Adicionar ao list `paginas` de navegação

Exemplo:
```python
def minha_nova_pagina(dados, filtros_globais):
    st.title("Minha Nova Página")
    # ... código da página
    
# No main():
paginas_funcoes = {
    # ... outras páginas
    "📊 Minha Nova Página": minha_nova_pagina
}
```

## Troubleshooting

### Erro: "Conexão com Impala falha"
- Verificar credenciais em `~/.streamlit/secrets.toml`
- Verificar conectividade com `bdaworkernode02.sef.sc.gov.br:21050`
- Verificar VPN/acesso à rede

### Erro: "Dados não carregados"
- Verificar se tabelas existem no banco: `SHOW TABLES IN niat`
- Verificar permissões de acesso
- Verificar logs: `st.sidebar.text(traceback.format_exc())`

### Performance lenta
- Aumentar TTL de cache
- Reduzir período de análise
- Verificar índices no Impala
- Usar agregados ao invés de dados completos

## Contribuindo

Para contribuir:

1. Criar branch com nome descritivo
2. Fazer alterações
3. Testar localmente
4. Criar pull request com descrição

## Licença

Propriedade da Receita Estadual de Santa Catarina

## Contato e Suporte

Para questões, bugs ou sugestões:
- Proprietário: tsevero
- Banco de Dados: niat (Impala)
- Versão: 1.0

## Histórico de Versões

### v1.0 (Atual)
- Dashboard Executivo com 7 páginas
- Integração com Impala
- Sistema de alertas
- Cache estratégico
- Autenticação por senha

## Referências Técnicas

- [Streamlit Documentation](https://docs.streamlit.io)
- [PySpark SQL Guide](https://spark.apache.org/docs/latest/sql-getting-started.html)
- [Impala Queries](https://impala.apache.org/)
- [Plotly Python](https://plotly.com/python/)

---

**Nota**: Este projeto foi desenvolvido para análise de comportamento tributário e monitoramento de conformidade fiscal. Todos os dados são sensíveis e devem ser tratados com confidencialidade apropriada.

*Última atualização: Novembro 2025*
