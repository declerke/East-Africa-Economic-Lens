# 🌍 East Africa Economic Lens: GDP Growth, Inflation, FDI & Trade Intelligence Dashboard for EAC-5

**East Africa Economic Lens is a production-grade Streamlit BI dashboard that ingests 15 World Bank WDI macroeconomic indicators for Kenya, Uganda, Tanzania, Ethiopia, and Rwanda across 25 years (2000–2024) via the World Bank REST API v2, stores the results as a typed Parquet file, and renders 9 interactive Plotly charts across 4 analysis tabs — covering GDP growth trajectories, per-capita wealth gaps, inflation dynamics, remittances vs FDI capital flows, trade balance composition, multi-country FDI comparisons, and a normalized 5-dimension competitiveness radar — all within a custom dark-theme Streamlit interface with real-time sidebar filters, auto-generated insight callouts, and a one-click Excel export; the entire pipeline and dashboard run at zero cost, sourcing exclusively from the World Bank's open API with no paid data subscriptions, no synthetic values, and no placeholder charts.**

| Metric | Value |
|---|---|
| Countries | Kenya, Uganda, Tanzania, Ethiopia, Rwanda (EAC-5 core) |
| Year Range | 2000–2024 (25 years) |
| Total Rows | 125 (5 countries × 25 years) |
| Indicators | 15 World Bank WDI series |
| Charts | 9 interactive Plotly charts |
| Dashboard Tabs | Growth & Wealth · Macroeconomic Stability · Trade & Investment · Export Data |
| Lines of Code | 782 |
| Data Source | World Bank REST API v2 (open, free, no API key) |
| Tech Stack | Python 3.11 · Streamlit 1.45 · Plotly 6.x · Pandas · PyArrow |
| Cost to Run | $0 |

---

## 🎯 Project Goal

East Africa is one of the fastest-growing economic regions on earth, yet per-country comparisons are typically scattered across PDF reports, spreadsheet downloads, and static World Bank portals that do not enable side-by-side interactive analysis. This project answers a single practical question: **how do Kenya and its four EAC peers compare across the macroeconomic indicators that development economists, investors, and policy analysts actually care about?** The answer is delivered as a live, filterable dashboard that pulls directly from authoritative World Bank data, computes real statistics at render time, and surfaces non-obvious insights — including Ethiopia's growth leadership, Kenya's remittances-over-FDI anomaly, and Rwanda's outsized FDI attraction — that are invisible in single-country summaries.

---

## 🧬 System Architecture

**1. Ingestion Layer** — A Python ingestion module calls the World Bank REST API v2 (no authentication required) for 15 WDI indicator codes across the EAC-5 country set and the full 2000–2024 date range. Responses arrive as JSON, are parsed into a flat Pandas DataFrame with consistent column naming, and are persisted as a typed Parquet file via PyArrow. The Parquet format provides columnar compression and schema enforcement, allowing subsequent loads to be an order of magnitude faster than re-querying the API on every dashboard start.

**2. Storage Layer** — A single Parquet file (`data/eac_economic_data.parquet`) holds 125 rows and 17 columns (country, year, and 15 indicator values). The file is committed to the repository so the dashboard can be cloned and run offline without an internet connection, while a refresh function in the sidebar re-fetches live data on demand.

**3. Presentation Layer** — A 782-line `app.py` implements the full Streamlit dashboard. The file is structured into four logical sections: global page config and CSS injection for the dark theme, sidebar controls (country multi-select, year range slider, tab selector), a computed statistics engine that derives per-tab KPI callouts from the filtered DataFrame at render time, and a chart rendering engine that builds all 9 Plotly figures with consistent country colors, shared axis formatting, and a custom `hex_to_rgba()` helper required by Plotly 6.x.

**4. Export Layer** — A one-click Excel export button in the sidebar converts the filtered DataFrame to an in-memory `BytesIO` buffer using `pandas.ExcelWriter` with the `openpyxl` engine and serves it as a `.xlsx` download without writing any temporary files to disk.

---

## 🛠️ Technical Stack

| Component | Technology | Purpose |
|---|---|---|
| Language | Python 3.11 | Core runtime |
| Dashboard Framework | Streamlit 1.45 | UI, sidebar controls, layout |
| Charting | Plotly 6.x | All 9 interactive charts |
| Data Manipulation | Pandas | DataFrame transforms, aggregations |
| Parquet I/O | PyArrow | Typed columnar storage |
| Excel Export | openpyxl | In-memory .xlsx generation |
| Data Source | World Bank REST API v2 | Live macroeconomic data |
| Storage Format | Parquet | Schema-enforced columnar file |
| Deployment | Streamlit Community Cloud | Zero-cost hosting |

---

## 📊 Performance & Results

- **Kenya** averaged **4.3% GDP growth per year** over the 2000–2024 period, placing it in the middle of the EAC-5 field.
- **Ethiopia** is the **fastest-growing EAC economy** at a **8.4% average annual GDP growth rate**, driven by sustained infrastructure investment cycles.
- **Kenya remittances consistently exceed FDI** — a structural anomaly within the EAC-5 that distinguishes Kenya's external capital model from every other member state.
- Rwanda sustains the highest FDI-to-GDP ratio among EAC-5 nations relative to its economic size, reflecting deliberate ease-of-doing-business reform dividends.
- Tanzania shows the most stable inflation trajectory, while Ethiopia and Uganda exhibit the highest volatility across the 25-year series.
- The 5-dimension competitiveness radar (Tab 4: Export Data) normalises GDP per capita, GDP growth, FDI inflows, trade openness, and remittances onto a common 0–1 scale, making relative national strengths immediately readable.

---

## 🌐 Live Dashboard

**Run locally:**

```bash
git clone https://github.com/declerke/East-Africa-Economic-Lens
cd east-africa-economic-lens
uv venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`. On first run the ingestion module fetches data from the World Bank API and writes `data/eac_economic_data.parquet`. Subsequent runs load from disk.

**Deploy to Streamlit Community Cloud:**

1. Fork the repository to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select your fork, set the branch to `main`, and the main file path to `app.py`.
4. Click **Deploy** — no secrets or environment variables are required.

---

## 📑 Data Sources

| Source | Access Method | Coverage | Cost |
|---|---|---|---|
| World Bank WDI REST API v2 | HTTP GET, no API key | 217 countries, 1960–present | Free |
| Parquet cache (`data/eac_economic_data.parquet`) | PyArrow local read | EAC-5, 2000–2024, 15 indicators | Free |

All data originates from the World Bank's World Development Indicators database, the authoritative source for macroeconomic time-series comparisons. No scraping, no paid subscriptions, no synthetic values.

---

## 🧠 Key Design Decisions

**1. Parquet over CSV for the data cache.** The ingestion module persists results as Parquet rather than CSV because Parquet encodes column data types in the file schema, eliminating the need for post-load dtype coercion. Float columns with sparse World Bank coverage (poverty rate, Gini index) remain typed correctly rather than silently converting to `object` when missing values are present. The columnar format also compresses the 125-row file to under 20 KB.

**2. hex_to_rgba() helper for Plotly 6.x compatibility.** Plotly 6.0 removed support for 8-digit hex color strings (RRGGBBAA format) that were previously accepted in some fill and marker color arguments. Rather than downgrading Plotly, the project implements a lightweight `hex_to_rgba(hex_color, alpha)` helper that converts the 6-digit country hex codes into `rgba()` CSS strings at render time. This keeps the color palette declaration clean (`#00d26a`, `#f5a623`, `#4299e1`, `#9f7aea`, `#ed64a6`) while producing Plotly 6.x-compatible RGBA strings for filled area charts and scatter markers.

**3. Poverty and Gini as scatter dots, not line charts.** World Bank poverty headcount ratio and Gini coefficient data for EAC-5 countries are drawn from national household surveys that occur at irregular intervals — typically 3–7 years apart — rather than annually. Rendering these series as connected line charts would imply annual measurement continuity that does not exist in the underlying data. The dashboard uses scatter dot markers with no connecting lines, explicitly communicating the survey-based, sparse nature of the data to avoid misinterpretation.

**4. Competitiveness radar on normalized 0–1 scale.** The 5-dimension radar chart in the Export Data tab compares countries across indicators with vastly different units and magnitudes: GDP per capita (USD thousands), GDP growth (%), FDI inflows (% of GDP), trade openness (% of GDP), and remittances (% of GDP). Rendering raw values would make the radar meaningless — Ethiopia's high growth rate would dominate while Kenya's GDP per capita advantage would be invisible. Each dimension is normalized to the 0–1 range across the EAC-5 values for the selected year, making relative national strengths directly comparable on a single chart.

**5. Zero-cost architecture with no paid API tier.** Every component in the pipeline — data source, compute, storage, and hosting — operates at zero cost. The World Bank REST API v2 is fully open with no rate limits for the query volumes this project generates. Streamlit Community Cloud hosts the dashboard for free. PyArrow Parquet eliminates the need for a database. This was a deliberate constraint: the project must be fully reproducible by any data engineer with only a GitHub account and a Python environment.

---

## 📂 Project Structure

```
east-africa-economic-lens/
├── app.py                         # Main Streamlit dashboard (782 lines)
├── ingest.py                      # World Bank API ingestion module
├── requirements.txt               # Python dependencies
├── data/
│   └── eac_economic_data.parquet  # Cached WDI data (EAC-5, 2000–2024)
├── assets/
│   └── dashboard_preview.png      # README screenshot
└── README.md
```

---

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/declerke/East-Africa-Economic-Lens
   cd east-africa-economic-lens
   ```

2. **Create and activate a virtual environment**
   ```bash
   uv venv
   # macOS/Linux:
   source .venv/bin/activate
   # Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```
   The dashboard opens at `http://localhost:8501`. On first run, the ingestion module automatically fetches data from the World Bank API and caches it locally as `data/eac_economic_data.parquet`.

5. **Refresh data** (optional)
   Click the **Refresh Data** button in the sidebar to re-fetch the latest World Bank figures and overwrite the local cache.

---

## 📈 Indicator Reference

| # | Indicator Name | WDI Code | Notes |
|---|---|---|---|
| 1 | GDP Growth (annual %) | NY.GDP.MKTP.KD.ZG | Annual % change, constant prices |
| 2 | GDP per Capita (current USD) | NY.GDP.PCAP.CD | Nominal, current USD |
| 3 | Inflation, Consumer Prices (annual %) | FP.CPI.TOTL.ZG | CPI-based, annual % |
| 4 | FDI Net Inflows (% of GDP) | BX.KLT.DINV.WD.GD.ZS | Net inflows as % of GDP |
| 5 | Remittances Received (% of GDP) | BX.TRF.PWKR.DT.GD.ZS | Personal remittances received |
| 6 | Exports of Goods & Services (% of GDP) | NE.EXP.GNFS.ZS | Goods and services exports |
| 7 | Imports of Goods & Services (% of GDP) | NE.IMP.GNFS.ZS | Goods and services imports |
| 8 | Trade (% of GDP) | NE.TRD.GNFS.ZS | Exports + imports sum |
| 9 | Current Account Balance (% of GDP) | BN.CAB.XOKA.GD.ZS | External balance position |
| 10 | Gross Capital Formation (% of GDP) | NE.GDI.TOTL.ZS | Investment proxy |
| 11 | Government Expenditure (% of GDP) | NE.CON.GOVT.ZS | General government final consumption |
| 12 | Population, Total | SP.POP.TOTL | Mid-year estimate |
| 13 | Urban Population (% of total) | SP.URB.TOTL.IN.ZS | Urbanization rate |
| 14 | Poverty Headcount Ratio (%) | SI.POV.DDAY | $2.15/day line; sparse survey data |
| 15 | Gini Index | SI.POV.GINI | Income inequality; sparse survey data |

Indicators 14 and 15 (Poverty and Gini) are rendered as scatter dots rather than connected lines due to irregular survey collection intervals. All other indicators have annual coverage for the full 2000–2024 range across all five countries.

---

## 🎓 Skills Demonstrated

| Domain | Skills | Job Requirement Match |
|---|---|---|
| REST API Integration | Direct World Bank v2 API with semicolon-batched country codes, pagination handling, timeout + retry logic, 300ms rate-limit courtesy sleep | "Experience with public APIs, data ingestion from external sources" |
| Data Pipeline Engineering | Cartesian skeleton merge pattern; 15-indicator left-join assembly; sparsity reporting; PyArrow Parquet output; separation of ingestion and presentation | "Build and maintain data pipelines"; "ETL design" |
| BI Dashboard Development | 9 Plotly charts across 4 Streamlit tabs; dark theme via injected CSS; sidebar filters; KPI cards with live deltas; auto-generated insight callouts; one-click Excel export | "Build interactive dashboards"; "data visualization for non-technical stakeholders" |
| Data Quality Handling | Explicit NaN vs dropped rows; graceful `safe_latest()`/`safe_prev()` fallback for sparse series; scatter-not-line treatment for survey indicators; per-chart `dropna()` scoped to required columns only | "Handle missing data"; "data quality validation" |
| Analytical Thinking | Ethiopia growth leadership surfaced over GDP-size default; remittances-vs-FDI as structural Kenya insight; radar exclusion of sparse indicators for methodological correctness | "Derive insights from data"; "communicate findings to stakeholders" |
| Python Best Practices | `uv venv` isolation; type hints (`pd.Series`, `float \| None`); `@st.cache_data` for performance; modular `chart_layout()` helper; `hex_to_rgba()` for library-version compatibility | "Clean, maintainable Python code"; "production-grade implementation" |
| Dependency Management | `uv` + `requirements.txt` with minimum pinned versions; `.venv` excluded from git; no global pip installs | "Reproducible environments"; "dependency management" |
| World Bank / Economic Data Literacy | Correct interpretation of WDI sparsity (surveys vs annual series); CBK inflation target framing; GDP growth vs GDP size distinction; remittances vs FDI as distinct balance-of-payments flows | "Domain knowledge in economic / development data"; "financial data analysis" |

---

**GitHub:** [https://github.com/declerke/East-Africa-Economic-Lens](https://github.com/declerke/East-Africa-Economic-Lens)

**Country Colors:** Kenya `#00d26a` · Uganda `#f5a623` · Tanzania `#4299e1` · Ethiopia `#9f7aea` · Rwanda `#ed64a6`
