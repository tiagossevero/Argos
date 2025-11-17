# ARGOS v2.0 - Sistema de Análise de Comportamento Tributário

## 🎯 Visão Geral

Sistema completamente refatorado e otimizado para análise de mudanças de comportamento tributário da Receita Estadual de Santa Catarina. O ARGOS v2.0 oferece dashboards interativos, análises estatísticas avançadas, machine learning e sistema inteligente de alertas.

## ✨ Novidades da v2.0

### Arquitetura Modular
- Código totalmente refatorado em módulos independentes
- Separação clara de responsabilidades (MVC pattern)
- Fácil manutenção e extensibilidade

### Visualizações Avançadas
- Gráficos interativos com Plotly
- 20+ tipos de visualizações diferentes
- Dashboards responsivos e modernos
- Temas customizáveis

### Análises Estatísticas
- Correlações e distribuições
- Testes de normalidade
- Detecção de outliers (IQR, Z-score, Isolation Forest)
- Análises de tendência e regressão

### Machine Learning
- Clustering (K-Means) para segmentação
- Detecção de anomalias (Isolation Forest)
- Análise de padrões automática
- Visualizações 3D interativas

### Sistema de Alertas Inteligente
- Score de risco multi-critério
- Priorização automática
- 5 níveis de alerta (LOW → EMERGENCY)
- Pesos configuráveis

### Performance Otimizada
- Cache inteligente em múltiplos níveis
- Queries otimizadas
- Carregamento assíncrono
- Suporte a grandes volumes de dados

## 📁 Estrutura do Projeto

```
streamlit_app/
├── app.py                      # Aplicação principal
├── config.py                   # Configurações e constantes
├── database.py                 # Conexão e cache de dados
├── analytics.py                # Análises estatísticas
├── visualizations.py           # Visualizações Plotly
├── utils.py                    # Funções utilitárias
├── requirements.txt            # Dependências
├── README.md                   # Esta documentação
└── pages/                      # Páginas do dashboard
    ├── __init__.py
    ├── home.py                 # Página inicial
    ├── dashboard_executivo.py  # Dashboard executivo
    ├── analise_empresas.py     # Análise de empresas
    ├── analise_produtos.py     # Análise de produtos
    ├── analise_setorial.py     # Análise setorial
    ├── analise_temporal.py     # Análise temporal
    ├── sistema_alertas.py      # Sistema de alertas
    ├── analises_estatisticas.py # Análises estatísticas
    ├── ml_insights.py          # ML insights
    └── relatorios.py           # Geração de relatórios
```

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.10 ou superior
- Acesso ao banco Impala
- Credenciais configuradas

### Instalação

```bash
# Clone o repositório
cd Argos/streamlit_app

# Instale as dependências
pip install -r requirements.txt
```

### Configuração

Crie o arquivo `.streamlit/secrets.toml`:

```toml
[impala]
username = "seu_usuario"
password = "sua_senha"
```

### Execução

```bash
streamlit run app.py
```

O sistema estará disponível em `http://localhost:8501`

## 📊 Funcionalidades por Página

### 🏠 Home
- Overview geral do sistema
- KPIs principais consolidados
- Evolução temporal resumida
- Guia rápido de navegação

### 📈 Dashboard Executivo
- **Visão Geral**: KPIs, distribuições, top setores
- **Tendências**: Evolução temporal com previsões
- **Rankings**: Top empresas por múltiplos critérios
- **Impacto Financeiro**: Análise de base de cálculo

### 🏢 Análise de Empresas
- **Ranking**: Lista priorizada com scores
- **Drill-Down**: Análise detalhada por CNPJ
- Evolução temporal da empresa
- Top produtos por empresa
- Download de dados

### 📦 Análise de Produtos
- Identificação de produtos voláteis
- Scatter plots interativos
- Análise de desvio padrão
- Coeficiente de variação
- Top produtos problemáticos

### 🏭 Análise Setorial
- Comparação entre setores (NCM 2 dígitos)
- Taxa de correção por setor
- Treemap de distribuição
- Benchmarking setorial

### 📅 Análise Temporal
- Evolução de todas as métricas
- Médias móveis
- Análise de tendência (regressão linear)
- Identificação de sazonalidade
- Gráficos empilhados

### 🚨 Sistema de Alertas
- Score de risco multi-critério
- Priorização automática
- Filtros por nível de alerta
- Lista exportável
- Visualização de distribuição

### 📊 Análises Estatísticas
- **Descritivas**: Média, mediana, desvio, quartis
- **Correlações**: Matriz de correlação com heatmap
- **Distribuições**: Histogramas com teste de normalidade
- **Outliers**: Detecção por IQR e Z-score

### 🤖 ML Insights
- **Clustering**: K-Means com visualização 3D
- **Anomalias**: Isolation Forest
- Score de anomalia
- Top casos anômalos

### 📄 Relatórios
- Exportação em Excel e CSV
- Relatório consolidado
- Downloads personalizados
- Formatação automática

## ⚙️ Configuração Avançada

### Configurações de Cache (config.py)

```python
CACHE_CONFIG = {
    'dados_agregados_ttl': 3600,  # 1 hora
    'detalhes_empresa_ttl': 1800,  # 30 minutos
    'kpis_ttl': 600,  # 10 minutos
    'max_entries': 100
}
```

### Sistema de Alertas (config.py)

```python
ALERT_WEIGHTS = {
    'mudancas_extremas': 40,  # Peso 40%
    'taxa_afastamento': 30,   # Peso 30%
    'base_calculo': 20,       # Peso 20%
    'volatilidade': 10        # Peso 10%
}
```

### Performance (config.py)

```python
PERFORMANCE_CONFIG = {
    'max_records_query': 50000,  # Máximo de registros por query
    'batch_size': 10000,         # Tamanho do batch
    'min_periods_analysis': 3,   # Mínimo de períodos para análise
    'parallel_queries': True     # Queries paralelas
}
```

## 🎨 Customização

### Temas

O sistema oferece dois temas pré-configurados:
- **Light**: Tema claro (padrão)
- **Dark**: Tema escuro

Para alternar, modifique em `config.py`:

```python
CHART_TEMPLATES = {
    'default': 'plotly_white',  # ou 'plotly_dark'
}
```

### Cores

Personalize as cores em `config.py`:

```python
CHART_COLORS = {
    'primary': '#1f77b4',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    # ...
}
```

## 📈 Métricas e KPIs

### KPIs Principais
- **Total de Registros**: Casos analisados
- **Empresas Monitoradas**: CNPJs distintos
- **Taxa de Correção**: % que aproximou da tarifa IA
- **Base de Cálculo**: Valor total em R$
- **Mudanças Extremas**: Casos críticos
- **Taxa de Extremas**: % de casos extremos

### Score de Risco

Calculado com 4 componentes:
1. **Mudanças Extremas (40%)**: Quantidade de casos extremos
2. **Taxa de Afastamento (30%)**: % de afastamentos da tarifa correta
3. **Base de Cálculo (20%)**: Impacto financeiro
4. **Volatilidade (10%)**: Desvio padrão das tarifas

**Fórmula**: Score = Σ(componente_i × peso_i), normalizado 0-100

### Níveis de Alerta

| Nível | Score | Prioridade |
|-------|-------|------------|
| EMERGENCY | ≥80 | 1 (Máxima) |
| CRITICAL | 60-79 | 2 |
| HIGH | 40-59 | 3 |
| MEDIUM | 20-39 | 4 |
| LOW | 0-19 | 5 (Mínima) |

## 🔐 Segurança

### Autenticação
- Senha padrão: `tsevero258`
- **IMPORTANTE**: Alterar antes de produção
- Credenciais Impala em secrets

### Boas Práticas
1. Nunca commitar credenciais
2. Usar `.streamlit/secrets.toml` para senhas
3. Configurar timeout de sessão
4. Revisar logs regularmente

## 🐛 Troubleshooting

### Erro de Conexão
```
Erro ao conectar ao banco de dados
```
**Solução**: Verificar credenciais em secrets.toml

### Cache Desatualizado
**Solução**: Usar botão "Limpar Cache" na sidebar

### Performance Lenta
**Solução**:
- Reduzir período de análise
- Diminuir `max_records_query` em config.py
- Verificar conexão de rede

### Erro de Import
```
ModuleNotFoundError: No module named 'X'
```
**Solução**: `pip install -r requirements.txt`

## 📝 Changelog

### v2.0.0 (2025-01-XX)
- ✨ Refatoração completa da arquitetura
- ✨ 10 páginas de análise interativa
- ✨ Sistema de ML e anomalias
- ✨ Cache inteligente multi-nível
- ✨ Exportação de relatórios
- ✨ Temas e customização
- 🎨 UI/UX completamente redesenhada
- ⚡ Performance otimizada
- 📊 20+ tipos de visualizações
- 🤖 Machine Learning integrado

### v1.0.0
- Versão inicial com dashboard básico

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFuncionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Email: niat@sef.sc.gov.br
- Issues: GitHub Issues

## 📄 Licença

Propriedade da Receita Estadual de Santa Catarina - NIAT

---

**ARGOS v2.0** - Sistema de Análise de Comportamento Tributário
Desenvolvido por NIAT - Receita Estadual de Santa Catarina
