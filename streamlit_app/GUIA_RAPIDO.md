# 🚀 ARGOS v2.0 - Guia Rápido de Instalação

## 📋 Pré-requisitos

- Python 3.10+
- Acesso ao banco Impala
- Git configurado

## ⚡ Instalação Rápida

### 1. Instalar Dependências

```bash
cd Argos/streamlit_app
pip install -r requirements.txt
```

### 2. Configurar Credenciais

Crie o arquivo `.streamlit/secrets.toml`:

```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml << 'EOF'
[impala]
username = "SEU_USUARIO"
password = "SUA_SENHA"
EOF
```

### 3. Executar o Sistema

```bash
streamlit run app.py
```

Acesse: `http://localhost:8501`

## 🔐 Autenticação

**Senha padrão**: `tsevero258`

⚠️ **IMPORTANTE**: Alterar em `config.py` antes de produção!

## 📊 Estrutura do Sistema

### Módulos Principais

| Arquivo | Função |
|---------|--------|
| `app.py` | Aplicação principal e navegação |
| `config.py` | Configurações centralizadas |
| `database.py` | Conexão e cache de dados |
| `analytics.py` | Análises estatísticas e ML |
| `visualizations.py` | Gráficos Plotly |
| `utils.py` | Funções utilitárias |

### Páginas (10 Dashboards)

1. **🏠 Home**: Overview e KPIs
2. **📈 Dashboard Executivo**: Visão consolidada
3. **🏢 Análise de Empresas**: Rankings e drill-down
4. **📦 Análise de Produtos**: Volatilidade
5. **🏭 Análise Setorial**: Comparação NCM
6. **📅 Análise Temporal**: Tendências
7. **🚨 Sistema de Alertas**: Priorização
8. **📊 Análises Estatísticas**: Correlações
9. **🤖 ML Insights**: Clustering e anomalias
10. **📄 Relatórios**: Exportação

## ⚙️ Configurações Importantes

### Cache (config.py)

```python
CACHE_CONFIG = {
    'dados_agregados_ttl': 3600,  # 1 hora
    'detalhes_empresa_ttl': 1800, # 30 min
}
```

### Performance (config.py)

```python
PERFORMANCE_CONFIG = {
    'max_records_query': 50000,   # Limite de registros
}
```

### Alertas (config.py)

```python
ALERT_WEIGHTS = {
    'mudancas_extremas': 40,  # 40%
    'taxa_afastamento': 30,   # 30%
    'base_calculo': 20,       # 20%
    'volatilidade': 10        # 10%
}
```

## 🎯 Funcionalidades Principais

### ✨ Visualizações
- 20+ tipos de gráficos Plotly interativos
- Dashboards responsivos
- Temas customizáveis
- Exportação de imagens

### 📊 Análises
- Estatísticas descritivas completas
- Correlações e distribuições
- Detecção de outliers (3 métodos)
- Testes de normalidade
- Regressão linear

### 🤖 Machine Learning
- Clustering (K-Means)
- Detecção de anomalias (Isolation Forest)
- Visualizações 3D
- Score de anomalia

### 🚨 Sistema de Alertas
- Score de risco 0-100
- 5 níveis de alerta
- Priorização automática
- Pesos configuráveis

### 📥 Exportação
- Excel (formatado)
- CSV (separado por ;)
- Relatórios consolidados
- Downloads personalizados

## 🔧 Manutenção

### Limpar Cache
Use o botão "🔄 Limpar Cache" na sidebar

### Atualizar Dados
Os dados são atualizados automaticamente conforme TTL do cache

### Logs
Logs são salvos automaticamente em `logs/`

## 🐛 Problemas Comuns

### Erro de Conexão
```
Verificar credenciais em .streamlit/secrets.toml
```

### Performance Lenta
```python
# Reduzir em config.py:
PERFORMANCE_CONFIG = {
    'max_records_query': 10000  # Reduzir de 50000
}
```

### Módulo não encontrado
```bash
pip install -r requirements.txt
```

## 📈 Métricas do Sistema

### Estatísticas do Código
- **Linhas de Código**: ~5.000
- **Arquivos**: 20
- **Módulos**: 6
- **Páginas**: 10
- **Funções**: 150+

### Recursos
- **Visualizações**: 20+ tipos
- **Análises Estatísticas**: 15+
- **Algoritmos ML**: 3
- **KPIs**: 30+

## 📚 Documentação Completa

Consulte `README.md` para documentação completa incluindo:
- Arquitetura detalhada
- API de cada módulo
- Exemplos de uso
- Configurações avançadas
- Troubleshooting completo

## 🎓 Primeiros Passos

1. Execute o sistema
2. Login com senha padrão
3. Explore a página **Home** para overview
4. Use **Dashboard Executivo** para análise geral
5. Acesse **Sistema de Alertas** para priorização
6. Explore páginas específicas conforme necessidade

## 💡 Dicas

- Use filtros globais na sidebar
- Explore gráficos interativos (zoom, pan, hover)
- Exporte dados para análises externas
- Configure alertas conforme prioridades
- Personalize cores e temas em config.py

## 🔗 Links Úteis

- Streamlit Docs: https://docs.streamlit.io
- Plotly Docs: https://plotly.com/python
- Scikit-learn Docs: https://scikit-learn.org

---

**ARGOS v2.0** - Sistema Completo de Análise Tributária
Desenvolvido por NIAT - Receita Estadual de Santa Catarina
