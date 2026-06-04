"""
East Africa Economic Lens — Streamlit BI Dashboard
Kenya vs EAC: GDP growth, inflation, FDI, trade, living standards 2000-2024
"""

import io
import warnings
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

warnings.filterwarnings("ignore")

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="East Africa Economic Lens",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── THEME & CSS ───────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] { display: none !important; }
span.material-symbols-rounded,
span.material-symbols-outlined,
span.material-icons { visibility: hidden !important; font-size: 0 !important; }

.stApp { background-color: #060b17; }

[data-testid="stSidebar"] {
    background: #0a0f1e !important;
    border-right: 1px solid rgba(0,210,106,0.12);
}

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0f1729 0%, #141f38 100%);
    border: 1px solid rgba(0,210,106,0.18);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    border-left: 3px solid #00d26a;
}

[data-testid="stMetricValue"] { color: #00d26a !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-size: 0.85rem !important; }
[data-testid="stMetricLabel"] { color: #718096 !important; font-size: 0.8rem !important; }

.stTabs [data-baseweb="tab-list"] {
    background: #0f1729;
    border-radius: 10px;
    padding: 4px 6px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #718096;
    border-radius: 7px;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 8px 18px;
}
.stTabs [aria-selected="true"] {
    background: #00d26a !important;
    color: #060b17 !important;
    font-weight: 700 !important;
}

h1 { color: #e2e8f0 !important; font-weight: 700 !important; letter-spacing: -0.5px; }
h2, h3 { color: #a0aec0 !important; font-weight: 600 !important; }
p, li { color: #cbd5e0; }

.insight-box {
    background: linear-gradient(135deg, #0f1729 0%, #161f36 100%);
    border-left: 4px solid #f5a623;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.5rem;
    margin: 1rem 0;
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.6;
}

.section-header {
    color: #a0aec0;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    padding-top: 0.5rem;
}

hr { border-color: rgba(0,210,106,0.1) !important; }

.stSelectbox > div, .stMultiSelect > div {
    background: #0f1729 !important;
    border-color: rgba(0,210,106,0.2) !important;
}

[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #00d26a, #00a855) !important;
    color: #060b17 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
COUNTRY_COLORS = {
    "Kenya":    "#00d26a",
    "Uganda":   "#f5a623",
    "Tanzania": "#4299e1",
    "Ethiopia": "#9f7aea",
    "Rwanda":   "#ed64a6",
}

def hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
COUNTRY_MAP = {
    "Kenya": "KE",
    "Uganda": "UG",
    "Tanzania": "TZ",
    "Ethiopia": "ET",
    "Rwanda": "RW",
}
COUNTRY_NAMES = {v: k for k, v in COUNTRY_MAP.items()}  # code → name


# ── HELPERS ───────────────────────────────────────────────────────────────────
def chart_layout(title="", height=420, legend_orient="h", legend_y=-0.15):
    return dict(
        title=dict(
            text=title,
            font=dict(color="#e2e8f0", size=15, family="Inter"),
            x=0,
            xanchor="left",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", family="Inter", size=12),
        height=height,
        margin=dict(l=10, r=10, t=50, b=60),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.08)",
            zeroline=False,
            tickfont=dict(size=11, color="#718096"),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.08)",
            zeroline=False,
            tickfont=dict(size=11, color="#718096"),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#a0aec0", size=11),
            orientation=legend_orient,
            yanchor="top" if legend_orient == "h" else "middle",
            y=legend_y if legend_orient == "h" else 0.5,
            x=0 if legend_orient == "h" else 1.02,
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0f1729",
            bordercolor="rgba(0,210,106,0.3)",
            font=dict(color="#e2e8f0", size=12),
        ),
    )


def _safe_nth(series: pd.Series, n: int) -> float | None:
    valid = series.dropna()
    try:
        return float(valid.iloc[n])
    except IndexError:
        return None

def safe_latest(series: pd.Series) -> float | None:
    return _safe_nth(series, -1)

def safe_prev(series: pd.Series) -> float | None:
    return _safe_nth(series, -2)


def insight(text: str):
    st.markdown(f'<div class="insight-box">&#128161; {text}</div>', unsafe_allow_html=True)


# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_parquet("data/processed/eac_economy.parquet")
    df["country"] = df["country"].astype(str)
    return df


df_all = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 EAC Economic Lens")
    st.markdown('<div class="section-header">Filters</div>', unsafe_allow_html=True)

    year_range = st.slider(
        "Year Range",
        min_value=2000,
        max_value=2024,
        value=(2005, 2024),
        step=1,
    )

    st.markdown("---")
    show_countries = st.multiselect(
        "Countries",
        options=list(COUNTRY_MAP.keys()),
        default=list(COUNTRY_MAP.keys()),
    )
    if not show_countries:
        show_countries = list(COUNTRY_MAP.keys())

    selected_codes = [COUNTRY_MAP[c] for c in show_countries]

    st.markdown("---")
    st.markdown('<div class="section-header">About</div>', unsafe_allow_html=True)
    st.caption("Data: World Bank WDI (2000–2024)")
    st.caption("Countries: Kenya · Uganda · Tanzania · Ethiopia · Rwanda")
    st.caption("Indicators: 15 macroeconomic series")

# ── FILTER DATA ───────────────────────────────────────────────────────────────
df = df_all[
    (df_all["economy"].isin(selected_codes))
    & (df_all["year"].between(year_range[0], year_range[1]))
].copy()

ke_all = df_all[df_all["economy"] == "KE"].sort_values("year")  # Kenya, all years
ke = df[df["economy"] == "KE"].sort_values("year")              # Kenya, filtered

# ── HERO HEADER ───────────────────────────────────────────────────────────────
st.markdown("# 🌍 East Africa Economic Lens")
st.markdown(
    "**Kenya vs East Africa** — GDP growth, inflation, FDI, trade, and living "
    "standards in regional context · 2000–2024 · World Bank WDI"
)
st.markdown("---")

# ── KPI CARDS (Kenya, latest available) ──────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

gdp_growth_now  = safe_latest(ke_all["GDP Growth (%)"])
gdp_growth_prev = safe_prev(ke_all["GDP Growth (%)"])
gdp_pc_now      = safe_latest(ke_all["GDP per Capita (2015 USD)"])
gdp_pc_prev     = safe_prev(ke_all["GDP per Capita (2015 USD)"])
inflation_now   = safe_latest(ke_all["Inflation (%)"])
inflation_prev  = safe_prev(ke_all["Inflation (%)"])
fdi_now         = safe_latest(ke_all["FDI % GDP"])
fdi_prev        = safe_prev(ke_all["FDI % GDP"])

with col1:
    if gdp_growth_now is not None:
        delta = round(gdp_growth_now - gdp_growth_prev, 2) if gdp_growth_prev else None
        st.metric("Kenya GDP Growth", f"{gdp_growth_now:.1f}%",
                  delta=f"{delta:+.1f}pp" if delta else None)
with col2:
    if gdp_pc_now is not None:
        delta = round(gdp_pc_now - gdp_pc_prev, 0) if gdp_pc_prev else None
        st.metric("Kenya GDP per Capita", f"${gdp_pc_now:,.0f}",
                  delta=f"${delta:+,.0f}" if delta else None)
with col3:
    if inflation_now is not None:
        delta = round(inflation_now - inflation_prev, 2) if inflation_prev else None
        st.metric("Kenya Inflation", f"{inflation_now:.1f}%",
                  delta=f"{delta:+.1f}pp" if delta else None,
                  delta_color="inverse")
with col4:
    if fdi_now is not None:
        delta = round(fdi_now - fdi_prev, 2) if fdi_prev else None
        st.metric("Kenya FDI (% GDP)", f"{fdi_now:.2f}%",
                  delta=f"{delta:+.2f}pp" if delta else None)

st.markdown("---")

# ── EXECUTIVE SUMMARY BANNER ──────────────────────────────────────────────────
ke_gdp_latest_row = ke_all[ke_all["GDP Growth (%)"].notna()].sort_values("year").iloc[-1]
ke_gdp_avg        = ke_all[ke_all["GDP Growth (%)"].notna()]["GDP Growth (%)"].mean()
ke_infl_latest    = ke_all[ke_all["Inflation (%)"].notna()].sort_values("year").iloc[-1]
ke_fdi_latest_row = ke_all[ke_all["FDI % GDP"].notna()].sort_values("year").iloc[-1]
ke_rem_latest_row = ke_all[ke_all["Remittances % GDP"].notna()].sort_values("year").iloc[-1]

fastest_code    = df_all[df_all["GDP Growth (%)"].notna()].groupby("economy")["GDP Growth (%)"].mean().idxmax()
fastest_country = COUNTRY_NAMES.get(fastest_code, fastest_code)

_cbk_target   = 5.0
_infl_status  = "above" if ke_infl_latest["Inflation (%)"] > _cbk_target else "within"
_fdi_val      = ke_fdi_latest_row["FDI % GDP"]
_rem_val      = ke_rem_latest_row["Remittances % GDP"]
_rem_vs_fdi   = "outpace" if _rem_val > _fdi_val else "trail"

exec_text = f"""
<div style="background:linear-gradient(135deg,#0f1729,#1a2744);border-radius:12px;padding:1.2rem 1.5rem;border:1px solid rgba(0,210,106,0.2);margin-bottom:1.5rem">
<div style="color:#00d26a;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:0.6rem">&#128203; KEY FINDINGS</div>
<ul style="color:#cbd5e0;margin:0;padding-left:1.2rem;line-height:1.8">
<li>Kenya's average GDP growth rate: <strong style="color:#00d26a">{ke_gdp_avg:.1f}%/yr</strong> since 2000, with latest reading of <strong>{ke_gdp_latest_row['GDP Growth (%)']:.1f}%</strong> in {int(ke_gdp_latest_row['year'])}.</li>
<li>Inflation in {int(ke_infl_latest['year'])}: <strong style="color:#f5a623">{ke_infl_latest['Inflation (%)']:.1f}%</strong> — <strong>{_infl_status}</strong> Kenya's CBK target of ~{_cbk_target:.0f}%.</li>
<li>Remittances at <strong style="color:#00d26a">{_rem_val:.1f}%</strong> of GDP {_rem_vs_fdi} FDI at <strong>{_fdi_val:.2f}%</strong> — diaspora inflows are Kenya's dominant external capital source.</li>
<li><strong style="color:#f5a623">{fastest_country}</strong> leads EAC in average annual GDP growth rate over the full 2000–2024 analysis period.</li>
</ul>
</div>
"""
st.markdown(exec_text, unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈  Growth & Wealth",
    "⚖️  Macro Stability",
    "🌐  Trade & Investment",
    "📥  Export Data",
])


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — GROWTH & WEALTH
# ────────────────────────────────────────────────────────────────────────────
with tab1:

    # ── Chart 1: Multi-country GDP growth line chart ─────────────────────────
    st.markdown("### GDP Growth Rate — Annual (%)")
    fig1 = go.Figure()

    # Zero line
    fig1.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)",
                   annotation_text="0% (recession)", annotation_font_color="#718096",
                   annotation_position="bottom right")

    for country in show_countries:
        cdf = df[df["country"] == country].sort_values("year")
        lw = 3 if country == "Kenya" else 1.5
        mode = "lines+markers" if country == "Kenya" else "lines"
        fig1.add_trace(go.Scatter(
            x=cdf["year"], y=cdf["GDP Growth (%)"],
            name=country, mode=mode,
            line=dict(color=COUNTRY_COLORS[country], width=lw),
            marker=dict(size=5) if country == "Kenya" else dict(size=3),
            hovertemplate=f"<b>{country}</b>: %{{y:.1f}}%<extra></extra>",
        ))

    # Annotations — GFC and COVID-19 reference lines
    if year_range[0] <= 2009 <= year_range[1]:
        fig1.add_vline(x=2009, line_dash="dot",
                       line_color="rgba(245,166,35,0.4)", line_width=1)
        fig1.add_annotation(x=2009, y=2, text="GFC",
                             font=dict(color="#f5a623", size=11),
                             showarrow=False, bgcolor="rgba(0,0,0,0)")
    if year_range[0] <= 2020 <= year_range[1]:
        fig1.add_vline(x=2020, line_dash="dash",
                       line_color="rgba(206,17,38,0.6)", line_width=1.5,
                       annotation_text="COVID-19",
                       annotation_font_color="#ff6b6b",
                       annotation_position="top")

    layout1 = chart_layout("GDP Growth (% Annual)", height=420)
    layout1["yaxis"]["ticksuffix"] = "%"
    fig1.update_layout(**layout1)
    st.plotly_chart(fig1, use_container_width=True)

    # ── Chart 2: GDP per Capita grouped bar — last 5 available years ─────────
    st.markdown("### GDP per Capita — Wealth Gap (USD, constant 2015)")
    latest_5 = sorted(df["year"].unique())[-5:]
    df_bar = df[df["year"].isin(latest_5)].dropna(subset=["GDP per Capita (2015 USD)"])

    fig2 = go.Figure()
    for country in show_countries:
        cdf = df_bar[df_bar["country"] == country].sort_values("year")
        fig2.add_trace(go.Bar(
            x=cdf["year"], y=cdf["GDP per Capita (2015 USD)"],
            name=country,
            marker_color=COUNTRY_COLORS[country],
            hovertemplate=f"<b>{country}</b> %{{x}}: $%{{y:,.0f}}<extra></extra>",
        ))

    layout2 = chart_layout("GDP per Capita — Last 5 Years (Constant 2015 USD)", height=400)
    layout2["yaxis"]["tickprefix"] = "$"
    layout2["barmode"] = "group"
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True)

    # ── Chart 3: Box plot — GDP growth distribution ───────────────────────────
    st.markdown("### Growth Volatility — Distribution of Annual GDP Growth Rates")
    df_box = df_all[df_all["economy"].isin(selected_codes)].dropna(subset=["GDP Growth (%)"])
    fig3 = go.Figure()
    for country in show_countries:
        cdf = df_box[df_box["country"] == country]["GDP Growth (%)"]
        fig3.add_trace(go.Box(
            y=cdf, name=country,
            marker_color=COUNTRY_COLORS[country],
            line_color=COUNTRY_COLORS[country],
            fillcolor=hex_to_rgba(COUNTRY_COLORS[country], 0.15),
            boxmean="sd",
            hovertemplate=f"<b>{country}</b><br>%{{y:.1f}}%<extra></extra>",
        ))

    layout3 = chart_layout("GDP Growth Distribution 2000–2024 (Full Period)", height=400)
    layout3["yaxis"]["ticksuffix"] = "%"
    layout3["hovermode"] = "closest"
    fig3.update_layout(**layout3)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Insight ───────────────────────────────────────────────────────────────
    ke_latest_growth = safe_latest(ke_all["GDP Growth (%)"])
    ke_latest_yr     = int(ke_all.dropna(subset=["GDP Growth (%)"]).iloc[-1]["year"])

    # EAC average for same year
    eac_yr = df_all[df_all["year"] == ke_latest_yr]["GDP Growth (%)"].mean()

    ke_pc       = safe_latest(ke_all["GDP per Capita (2015 USD)"])
    all_latest  = df_all[df_all["year"] == ke_latest_yr][["country","GDP per Capita (2015 USD)"]].dropna()
    ke_rank     = int(all_latest["GDP per Capita (2015 USD)"].rank(ascending=False)[
        all_latest["country"] == "Kenya"
    ].values[0]) if not all_latest.empty else "N/A"

    insight(
        f"Kenya's GDP grew at <b>{ke_latest_growth:.1f}%</b> in {ke_latest_yr} "
        f"vs EAC average of <b>{eac_yr:.1f}%</b>. "
        f"Kenya ranks <b>{ke_rank}</b> in EAC for GDP per capita at "
        f"<b>${ke_pc:,.0f}</b> (constant 2015 USD). "
        f"Ethiopia leads in raw growth rates but Kenya leads in per-capita wealth."
    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — MACROECONOMIC STABILITY
# ────────────────────────────────────────────────────────────────────────────
with tab2:

    # ── Chart 4: Inflation multi-line ─────────────────────────────────────────
    st.markdown("### Inflation Rates — Consumer Prices (Annual %)")
    fig4 = go.Figure()

    # Reference bands
    fig4.add_hrect(y0=0, y1=5, fillcolor="rgba(0,210,106,0.05)",
                   line_width=0, annotation_text="Target zone (<5%)",
                   annotation_font_color="#00d26a", annotation_font_size=11)
    fig4.add_hline(y=10, line_dash="dot", line_color="rgba(245,166,35,0.5)",
                   annotation_text="High inflation (10%)",
                   annotation_font_color="#f5a623",
                   annotation_position="top right")

    for country in show_countries:
        cdf = df[df["country"] == country].sort_values("year")
        lw = 3 if country == "Kenya" else 1.5
        fig4.add_trace(go.Scatter(
            x=cdf["year"], y=cdf["Inflation (%)"],
            name=country, mode="lines",
            line=dict(color=COUNTRY_COLORS[country], width=lw),
            hovertemplate=f"<b>{country}</b>: %{{y:.1f}}%<extra></extra>",
        ))

    layout4 = chart_layout("Inflation (CPI, Annual %)", height=420)
    layout4["yaxis"]["ticksuffix"] = "%"
    fig4.update_layout(**layout4)
    st.plotly_chart(fig4, use_container_width=True)

    # ── Chart 5: GDP growth vs Inflation scatter ──────────────────────────────
    st.markdown("### Growth–Stability Trade-off")
    df_scatter = df_all[
        df_all["economy"].isin(selected_codes)
    ].dropna(subset=["GDP Growth (%)", "Inflation (%)", "GDP (current USD)"])

    fig5 = px.scatter(
        df_scatter,
        x="GDP Growth (%)",
        y="Inflation (%)",
        color="country",
        size="GDP (current USD)",
        hover_data={"year": True, "country": True,
                    "GDP Growth (%)": ":.1f", "Inflation (%)": ":.1f"},
        color_discrete_map=COUNTRY_COLORS,
        opacity=0.75,
    )
    fig5.update_traces(marker=dict(line=dict(width=0)))

    # Quadrant lines
    fig5.add_vline(x=0, line_dash="dash", line_color="rgba(255,255,255,0.15)")
    fig5.add_hline(y=5, line_dash="dash", line_color="rgba(0,210,106,0.3)")

    layout5 = chart_layout(
        "GDP Growth vs Inflation — All Years (bubble = GDP size)", height=450
    )
    layout5["xaxis"]["ticksuffix"] = "%"
    layout5["yaxis"]["ticksuffix"] = "%"
    layout5["hovermode"] = "closest"
    fig5.update_layout(**layout5)
    st.plotly_chart(fig5, use_container_width=True)

    # ── Chart 6: Kenya Remittances vs FDI % GDP ───────────────────────────────
    st.markdown("### Kenya — Foreign Capital Sources: Remittances vs FDI (% GDP)")
    ke_cap = ke_all.sort_values("year")
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=ke_cap["year"], y=ke_cap["Remittances % GDP"],
        name="Remittances % GDP",
        mode="lines+markers",
        line=dict(color="#f5a623", width=2.5),
        fill="tozeroy", fillcolor="rgba(245,166,35,0.08)",
        marker=dict(size=5),
        hovertemplate="Remittances: %{y:.2f}%<extra></extra>",
    ))
    fig6.add_trace(go.Scatter(
        x=ke_cap["year"], y=ke_cap["FDI % GDP"],
        name="FDI % GDP",
        mode="lines+markers",
        line=dict(color="#00d26a", width=2.5),
        fill="tozeroy", fillcolor="rgba(0,210,106,0.06)",
        marker=dict(size=5),
        hovertemplate="FDI: %{y:.2f}%<extra></extra>",
    ))
    layout6 = chart_layout("Kenya: Remittances vs FDI (% of GDP)", height=380)
    layout6["yaxis"]["ticksuffix"] = "%"
    fig6.update_layout(**layout6)
    st.plotly_chart(fig6, use_container_width=True)

    # ── Insight ───────────────────────────────────────────────────────────────
    ke_infl_avg  = ke_all["Inflation (%)"].dropna().mean()
    eac_infl_avg = df_all[df_all["economy"].isin(list(COUNTRY_MAP.values()))]["Inflation (%)"].dropna().mean()
    ke_rem_latest = safe_latest(ke_all["Remittances % GDP"])
    ke_fdi_latest = safe_latest(ke_all["FDI % GDP"])
    rem_vs_fdi = "higher than" if (ke_rem_latest or 0) > (ke_fdi_latest or 0) else "lower than"

    insight(
        f"Kenya's inflation averaged <b>{ke_infl_avg:.1f}%</b> over the full period "
        f"vs the EAC average of <b>{eac_infl_avg:.1f}%</b>. "
        f"Remittances represent <b>{ke_rem_latest:.1f}%</b> of GDP — "
        f"<b>{rem_vs_fdi}</b> FDI at <b>{ke_fdi_latest:.2f}%</b> of GDP. "
        f"This signals Kenya's diaspora is a larger financing source than foreign direct investment."
    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — TRADE & INVESTMENT
# ────────────────────────────────────────────────────────────────────────────
with tab3:

    # ── Chart 7: Kenya Trade — stacked area ───────────────────────────────────
    st.markdown("### Kenya — Trade Balance: Exports vs Imports (% GDP)")
    ke_trade = ke_all.dropna(subset=["Exports % GDP", "Imports % GDP"])
    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=ke_trade["year"], y=ke_trade["Exports % GDP"],
        name="Exports % GDP",
        mode="lines", stackgroup="trade",
        fillcolor="rgba(0,210,106,0.25)",
        line=dict(color="#00d26a", width=2),
        hovertemplate="Exports: %{y:.1f}%<extra></extra>",
    ))
    fig7.add_trace(go.Scatter(
        x=ke_trade["year"], y=ke_trade["Imports % GDP"],
        name="Imports % GDP",
        mode="lines", stackgroup="trade",
        fillcolor="rgba(206,17,38,0.2)",
        line=dict(color="#ce1126", width=2),
        hovertemplate="Imports: %{y:.1f}%<extra></extra>",
    ))
    layout7 = chart_layout("Kenya: Exports vs Imports as % of GDP (stacked area)", height=400)
    layout7["yaxis"]["ticksuffix"] = "%"
    fig7.update_layout(**layout7)
    st.plotly_chart(fig7, use_container_width=True)

    # ── Chart 8: FDI % GDP horizontal bar ────────────────────────────────────
    st.markdown("### FDI Net Inflows (% GDP) — Latest Year, Country Comparison")
    latest_yr = df_all.dropna(subset=["FDI % GDP"])["year"].max()
    df_fdi = (
        df_all[df_all["year"] == latest_yr]
        .dropna(subset=["FDI % GDP"])
        .sort_values("FDI % GDP", ascending=True)
    )

    fig8 = go.Figure()
    fig8.add_trace(go.Bar(
        x=df_fdi["FDI % GDP"],
        y=df_fdi["country"],
        orientation="h",
        marker=dict(
            color=[COUNTRY_COLORS.get(c, "#718096") for c in df_fdi["country"]],
            line=dict(width=0),
        ),
        text=[f"{v:.2f}%" for v in df_fdi["FDI % GDP"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b>: %{x:.2f}%<extra></extra>",
    ))
    layout8 = chart_layout(f"FDI Net Inflows (% GDP) — {latest_yr}", height=350)
    layout8["xaxis"]["ticksuffix"] = "%"
    layout8["margin"]["r"] = 80
    layout8["hovermode"] = "closest"
    fig8.update_layout(**layout8)
    st.plotly_chart(fig8, use_container_width=True)

    # ── Chart 9: Radar chart — Kenya vs Rwanda vs Ethiopia ────────────────────
    st.markdown("### Country Scorecard — Multi-Dimensional Competitiveness Radar")

    radar_countries = [c for c in ["Kenya", "Rwanda", "Ethiopia"] if c in show_countries]
    if len(radar_countries) < 2:
        radar_countries = ["Kenya", "Rwanda", "Ethiopia"]

    # Radar uses only high-coverage indicators (>15 data points per country).
    # Poverty Rate and Gini Index are excluded — survey-based, only 4–6 points each.
    radar_dims = {
        "GDP Growth (%)":   ("GDP Growth",     True),
        "Inflation (%)":    ("Low Inflation",  False),
        "FDI % GDP":        ("FDI Attraction", True),
        "Trade % GDP":      ("Trade Openness", True),
        "Remittances % GDP": ("Remittances",   True),
    }

    # Use 5-year averages for robustness
    radar_window = df_all[df_all["year"] >= 2019]

    def radar_score(country_name: str):
        cdf = radar_window[radar_window["country"] == country_name]
        scores = {}
        for col, (label, higher_is_better) in radar_dims.items():
            val = cdf[col].dropna().mean() if col in cdf.columns else np.nan
            scores[label] = val
        return scores

    raw_scores = {c: radar_score(c) for c in radar_countries}
    dim_labels = [v[0] for v in radar_dims.values()]

    # Normalize 0–100 per dimension across the 3 countries
    def normalize_dim(dim_label: str, higher_is_better: bool):
        vals = [raw_scores[c].get(dim_label, np.nan) for c in radar_countries]
        clean = [v for v in vals if not np.isnan(v)]
        if not clean:
            return {c: 50 for c in radar_countries}
        mn, mx = min(clean), max(clean)
        normed = {}
        for c, v in zip(radar_countries, vals):
            if np.isnan(v):
                normed[c] = 50
            elif mx == mn:
                normed[c] = 50
            else:
                score = (v - mn) / (mx - mn) * 100
                normed[c] = score if higher_is_better else 100 - score
        return normed

    norm = {}
    for col, (label, hib) in radar_dims.items():
        norm[label] = normalize_dim(label, hib)

    fig9 = go.Figure()
    for country in radar_countries:
        r_vals = [norm[label][country] for label in dim_labels]
        r_vals_closed = r_vals + [r_vals[0]]
        labels_closed = dim_labels + [dim_labels[0]]
        fig9.add_trace(go.Scatterpolar(
            r=r_vals_closed,
            theta=labels_closed,
            fill="toself",
            fillcolor=hex_to_rgba(COUNTRY_COLORS[country], 0.20),
            line=dict(color=COUNTRY_COLORS[country], width=2),
            name=country,
            hovertemplate=f"<b>{country}</b><br>%{{theta}}: %{{r:.0f}}/100<extra></extra>",
        ))

    fig9.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=9, color="#718096"),
                gridcolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.1)",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#a0aec0"),
                gridcolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.1)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(
            text="Country Competitiveness Radar (2019–2024 avg, normalized 0–100 — full-coverage indicators only)",
            font=dict(color="#e2e8f0", size=15),
            x=0,
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a0aec0")),
        height=480,
        font=dict(color="#e2e8f0", family="Inter"),
        hoverlabel=dict(bgcolor="#0f1729", bordercolor="rgba(0,210,106,0.3)",
                        font=dict(color="#e2e8f0", size=12)),
    )
    st.plotly_chart(fig9, use_container_width=True)

    # ── Insight ───────────────────────────────────────────────────────────────
    ke_trade_latest  = safe_latest(ke_all["Trade % GDP"])
    eac_trade_latest = df_all[
        (df_all["economy"].isin(list(COUNTRY_MAP.values()))) &
        (df_all["year"] == df_all.dropna(subset=["Trade % GDP"])["year"].max())
    ]["Trade % GDP"].mean()

    trade_dir = "higher" if (ke_trade_latest or 0) > (eac_trade_latest or 0) else "lower"
    ke_fdi_yr = int(df_all.dropna(subset=["FDI % GDP"]).iloc[-1]["year"])
    fdi_change_dir = "increased" if (fdi_now or 0) > (fdi_prev or 0) else "decreased"

    insight(
        f"Kenya's trade-to-GDP ratio is <b>{ke_trade_latest:.1f}%</b> — "
        f"<b>{trade_dir}</b> than the EAC average of <b>{eac_trade_latest:.1f}%</b>. "
        f"FDI net inflows <b>{fdi_change_dir}</b> to <b>{fdi_now:.2f}%</b> of GDP in "
        f"{ke_fdi_yr}. The radar shows Rwanda punching above its weight on FDI attraction "
        f"relative to its economic size — a key lesson for Kenya's investment climate."
    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — EXPORT DATA
# ────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### Filtered Dataset")
    st.markdown(
        f"Showing data for **{', '.join(show_countries)}** "
        f"from **{year_range[0]}** to **{year_range[1]}**"
    )

    display_df = df.copy()
    display_df = display_df.rename(columns={"economy": "ISO2"})
    display_df = display_df.sort_values(["country", "year"])

    # Round numeric columns for display
    num_cols = display_df.select_dtypes(include="number").columns
    display_df[num_cols] = display_df[num_cols].round(3)

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
        hide_index=True,
    )

    # Summary stats
    st.markdown("#### Summary Statistics")
    summary_cols = [
        "GDP Growth (%)", "GDP per Capita (2015 USD)", "Inflation (%)",
        "FDI % GDP", "Trade % GDP", "Remittances % GDP",
    ]
    available_summary = [c for c in summary_cols if c in display_df.columns]
    st.dataframe(
        display_df[available_summary].describe().round(2),
        use_container_width=True,
    )

    # Excel download
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        display_df.to_excel(writer, sheet_name="EAC_Data", index=False)
        if available_summary:
            display_df[available_summary].describe().round(2).to_excel(
                writer, sheet_name="Summary_Stats"
            )

    st.download_button(
        label="Download as Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name=f"eac_economic_lens_{year_range[0]}_{year_range[1]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
