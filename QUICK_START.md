# ARGOS - Quick Start Guide

## What is ARGOS?

ARGOS is a **tax behavior monitoring system** that detects suspicious changes in ICMS tax rates applied by companies in electronic invoices (NFC-e). It helps tax authorities identify companies that may be committing tax fraud or irregularities.

## Quick Facts

| What | Details |
|------|---------|
| **Purpose** | Detect abnormal tax rate variations by companies |
| **Data Source** | Electronic invoices (NFC-e) 2023-2025 |
| **Technology** | Python, Streamlit, PySpark, Impala |
| **Dashboard Pages** | 7 interactive pages |
| **Main User** | Tax auditors at Santa Catarina State Tax Authority |
| **Password** | tsevero258 |

## 60-Second Setup

```bash
# 1. Install dependencies
pip install streamlit pandas numpy plotly sqlalchemy impyla

# 2. Configure credentials
# Create ~/.streamlit/secrets.toml with:
# [impala_credentials]
# user = "your_username"
# password = "your_password"

# 3. Run dashboard
streamlit run ARGOSCA.py

# 4. Open browser
# http://localhost:8501
# Enter password: tsevero258
```

## What Each Dashboard Page Does

### 1. Executive Dashboard (📊)
Shows overview of all monitored companies. Key numbers:
- Total cases analyzed
- Companies being monitored
- % of cases corrected (moved toward correct tariff)
- Extreme tariff changes detected

### 2. Company Rankings (🏆)
Lists top problematic companies. Can sort by:
- **Correction Rate**: % that fixed their tariffs
- **Extreme Changes**: Cases where tariff jumped >2 standard deviations
- **Calculation Base**: Total ICMS amount involved
- **Number of Cases**: Total suspicious instances

### 3. Product Analysis (📦)
Identifies products with inconsistent tariffs across companies:
- Shows which products have high variation
- Lists companies using different rates for same product
- Highlights suspicious pricing patterns

### 4. Sectoral Analysis (🏭)
Groups by product category (NCM - 2 digits):
- Shows which sectors have most problems
- Displays correction rates by sector
- Identifies high-risk industry groups

### 5. Company Drill-Down (🔬)
Deep dive into one specific company:
- Monthly behavior over time
- Top products by that company
- How their tariffs changed
- Comparison to expected rates

### 6. Temporal Comparison (⏱️)
Compares first 6 months vs last 6 months:
- Is behavior improving or getting worse?
- Are extreme changes increasing/decreasing?
- Automatic trend interpretation

### 7. Alert System (🚨)
Risk scoring and prioritization for audits:
- Automatic risk score (0-100+)
- Alert level: LOW, MEDIUM, HIGH, CRITICAL, EMERGENCY
- Prioritization matrix for audit targeting
- Configurable risk weights

## Understanding the Data Model

### 3 Core Concepts

**1. Tariff (Alíquota)**
- Tax rate applied by company (e.g., 7% ICMS)
- What company ACTUALLY charged
- What company SHOULD charge (IA/expected value)

**2. Base (Base de Cálculo)**
- Total value of goods sold
- Used to calculate ICMS owed
- In the system: monthly totals per company-product

**3. Change Classification**
```
PRODUCT_STABLE          → No variation in history
BEHAVIOR_NORMAL         → Normal variation (≤1 std dev)
SIGNIFICANT_CHANGE      → Notable change (1-2 std dev)
EXTREME_CHANGE          → Very suspicious (>2 std dev)
```

### How It Works

```
Company sells Product X for 100 months:
  Months 1-95:  Always charge 10% ICMS
  Month 96:     Suddenly charges 4% ICMS
  
Analysis Result:
  Classification: EXTREME_CHANGE (moved >2 std dev)
  Movement: AFASTOU_DA_CORRETA (wrong direction)
  Risk: HIGH (moved away from correct 7%)
```

## Common Queries

### "How do I find the most suspicious companies?"
1. Go to **Alert System** (🚨)
2. Look at "EMERGENCIAL" and "CRÍTICO" levels
3. Companies at top of list are highest priority for audit

### "Which products are most problematic?"
1. Go to **Product Analysis** (📦)
2. Products with highest standard deviation = most variation
3. Check which companies use different rates for same product

### "Is the situation improving?"
1. Go to **Temporal Comparison** (⏱️)
2. Compare "Correction Rate" between periods
3. Positive trend = companies fixing behavior
4. Negative trend = more extreme changes

### "Tell me about one company"
1. Go to **Drill-Down** (🔬)
2. Select company from dropdown
3. See monthly evolution and top problematic products

## Key Metrics Explained

| Metric | Meaning | Good/Bad |
|--------|---------|----------|
| Correction Rate | % of cases that improved toward correct tariff | Higher = GOOD |
| Extreme Changes | # of cases with massive tariff jumps | Lower = GOOD |
| Difference vs IA | How far from expected rate | Lower = GOOD |
| Base of Calculation | Total ICMS amount involved | For impact assessment |

## File Structure

```
ARGOSCA.py              ← Main dashboard (run this!)
ARGOSC.ipynb            ← PySpark analysis notebook (for data scientists)
ARGOSC-Exemplo.ipynb    ← Example/demo notebook
ARGOS INDIVIDUAL.json   ← Database configuration
README.md               ← Full documentation
PROJECT_SUMMARY.txt     ← This comprehensive summary
QUICK_START.md          ← This quick start guide
```

## Database Connection

**Server**: bdaworkernode02.sef.sc.gov.br:21050
**Database**: niat
**Tables Used**:
- `niat.argos_mudanca_comportamento` (main analysis table)
- `niat.argos_vw_evolucao_nfce` (query view)

**Credentials**: Stored in `~/.streamlit/secrets.toml`

## Troubleshooting

### Dashboard Won't Start
```
Error: "Connection to Impala failed"
Fix: Check credentials and network access to bdaworkernode02
```

### No Data Shows Up
```
Error: "No data found for selected filters"
Fix: Check date range (2023-2025 only) or expand filters
```

### Very Slow
```
Problem: Dashboard responding slowly
Fix: Increase cache time or reduce analysis period
```

## Advanced Usage

### Adding Custom Analysis
Edit ARGOSCA.py to add new page:
```python
def minha_analise(dados, filtros):
    st.title("My Custom Analysis")
    # Your code here
```

### Exporting Data
From any page, use `st.dataframe()` and Streamlit's download button.

### Using Notebooks
1. Open ARGOSC.ipynb
2. Connect PySpark session
3. Run SQL queries directly on Impala
4. Create custom visualizations

## Important Notes

1. **Password**: Default password (tsevero258) should be changed before production
2. **Data Sensitivity**: All data is confidential tax information
3. **Compliance**: Ensure LGPD/privacy law compliance when sharing
4. **Performance**: First load takes 30-60s as it caches data (then <5s)
5. **Cache**: Data refreshes every hour (configurable in code)

## Glossary

| Term | Definition |
|------|-----------|
| **NFC-e** | Nota Fiscal de Consumidor Eletrônica (electronic consumer invoice) |
| **ICMS** | Imposto sobre Circulação de Mercadorias e Serviços (state tax) |
| **CNPJ** | Cadastro Nacional da Pessoa Jurídica (company tax ID) |
| **NCM** | Nomenclatura Comum do Mercosul (product category code) |
| **GTIN** | Global Trade Item Number (product barcode) |
| **IA** | Inteligência Artificial (expected/reference tariff value) |
| **Alíquota** | Tax rate percentage |
| **Desvio** | Standard deviation (measure of variation) |

## Getting Help

1. **Technical Issues**: Check PROJECT_SUMMARY.txt troubleshooting section
2. **Understanding Data**: Read README.md "Understanding the Data" section
3. **Dashboard Features**: Click help icons (?) in each page
4. **Code Details**: Review ARGOSCA.py comments and docstrings

## Performance Tips

- **Faster Load**: Check "Configurações Visuais" to clear cache
- **Smooth Scrolling**: Use period filters to reduce data
- **Better Export**: Use drill-down for specific company data
- **Bulk Analysis**: Use notebooks (ARGOSC.ipynb) for large extracts

## Next Steps

1. Start the dashboard with `streamlit run ARGOSCA.py`
2. Explore each of the 7 pages
3. Use filters to narrow down to companies of interest
4. Click on companies in ranking to drill down
5. Use Alert System to prioritize audit targets
6. Export data for further analysis or reports

---

**Document Version**: 1.0
**Created**: November 2025
**Status**: Production Ready

For detailed information, see README.md and PROJECT_SUMMARY.txt
