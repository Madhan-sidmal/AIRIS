"""
AIRIS — Pilot Dashboard
========================
Streamlit dashboard showing the AI Equity Index for pilot districts.
Run with: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="AIRIS — AI Rural Impact Surveillance System",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130 0%, #252a3d 100%);
        border: 1px solid #2d3250;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #e2e8f0; }
    .metric-label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
    .severely-excluded { color: #ef4444; }
    .excluded          { color: #f97316; }
    .transitional      { color: #eab308; }
    .included          { color: #22c55e; }
    .header-gradient {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_airis_data():
    feat_dir = Path("data/features")
    files = list(feat_dir.glob("ai_equity_index_*.parquet"))
    if files:
        df = pd.read_parquet(sorted(files)[-1])
        return df
    # Generate live if not cached
    from analysis.indices.ai_equity_index import AIEquityIndexCalculator
    calc = AIEquityIndexCalculator()
    df, _ = calc.run()
    return df

@st.cache_data
def load_gdp_data():
    from analysis.indices.ai_equity_index import AIEquityIndexCalculator
    feat_dir = Path("data/features")
    files = list(feat_dir.glob("ai_equity_index_*.parquet"))
    if files:
        df = pd.read_parquet(sorted(files)[-1])
        calc = AIEquityIndexCalculator()
        gdp = calc.estimate_gdp_loss(df)
        return gdp
    return {}


# ── Header ────────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 8])
with col_title:
    st.markdown('<p class="header-gradient">AIRIS</p>', unsafe_allow_html=True)
    st.markdown("**AI Rural Impact Surveillance System** — India's AI Equity Intelligence Platform")
    st.caption("Measuring how AI advancement is widening the rural-urban development gap, district by district.")

st.markdown("---")

# ── Load ──────────────────────────────────────────────────────────────────────
try:
    df  = load_airis_data()
    gdp = load_gdp_data()
except Exception as e:
    st.error(f"Data not ready. Run: `python run_pipeline.py` first.\n\nError: {e}")
    st.stop()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filters")
    states   = ["All States"] + sorted(df["state_name"].dropna().unique().tolist())
    sel_state = st.selectbox("State", states)
    classes  = ["All"] + df["ai_equity_class"].dropna().unique().tolist()
    sel_class = st.selectbox("AI Equity Class", classes)
    show_top = st.slider("Show top N districts", 5, len(df), min(10, len(df)))

    st.markdown("---")
    st.markdown("**Data Sources**")
    st.caption("TRAI Q3 2024 | PLFS 2023-24")
    st.caption("Benchmarks: OECD 2024, TRAI 2024, FAO")

# ── Filter ────────────────────────────────────────────────────────────────────
filtered = df.copy()
if sel_state != "All States":
    filtered = filtered[filtered["state_name"] == sel_state]
if sel_class != "All":
    filtered = filtered[filtered["ai_equity_class"] == sel_class]
filtered = filtered.sort_values("ai_equity_index", ascending=False).head(show_top)

# ── KPI row ───────────────────────────────────────────────────────────────────
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

excluded_pct = (df["ai_equity_index"] > 50).mean() * 100
mean_infra   = df["infrastructure_gap_index"].mean()
mean_job     = df["job_impact_index"].mean()
gdp_loss     = gdp.get("total_annual_gdp_loss_cr", 0)

with kpi1:
    st.metric("Districts AI-Excluded (>50)", f"{excluded_pct:.0f}%",
              delta="Pilot sample", delta_color="off")
with kpi2:
    st.metric("Avg Infrastructure Gap", f"{mean_infra:.1f}/100",
              delta="63.7pp broadband gap", delta_color="off")
with kpi3:
    st.metric("Avg Job Displacement Risk", f"{mean_job:.1f}/100",
              delta="Rural vs urban workers", delta_color="off")
with kpi4:
    st.metric("Est. Annual GDP Loss", f"₹{gdp_loss:,.0f} Cr",
              delta="From AI exclusion", delta_color="off")

st.markdown("---")

# ── Main charts ───────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 AI Equity Rankings",
    "🔗 Gap Decomposition",
    "💼 Job Risk vs Infrastructure",
    "📈 The Gap Story"
])

with tab1:
    st.subheader("AI Equity Index by District (0 = No exclusion, 100 = Fully excluded)")

    color_map = {
        "Severely Excluded": "#ef4444",
        "Excluded":          "#f97316",
        "Transitional":      "#eab308",
        "Included":          "#22c55e",
    }

    fig = px.bar(
        filtered.sort_values("ai_equity_index"),
        x="ai_equity_index",
        y="district_name",
        color="ai_equity_class",
        color_discrete_map=color_map,
        orientation="h",
        text="ai_equity_index",
        hover_data=["state_name", "infrastructure_gap_index",
                    "adoption_gap_index", "job_impact_index"],
        labels={"ai_equity_index": "AI Equity Index", "district_name": "District"}
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        plot_bgcolor="#0f1117",
        paper_bgcolor="#0f1117",
        font_color="#e2e8f0",
        showlegend=True,
        height=max(400, len(filtered) * 45),
        xaxis=dict(range=[0, 105], gridcolor="#2d3250"),
        yaxis=dict(gridcolor="#2d3250"),
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("What is driving the exclusion? Sub-Index Breakdown")
    melt = filtered.melt(
        id_vars="district_name",
        value_vars=["infrastructure_gap_index", "adoption_gap_index", "job_impact_index"],
        var_name="Sub-Index",
        value_name="Score"
    )
    melt["Sub-Index"] = melt["Sub-Index"].map({
        "infrastructure_gap_index": "Infrastructure Gap",
        "adoption_gap_index":       "AI Adoption Gap",
        "job_impact_index":         "Job Displacement Risk",
    })
    fig2 = px.bar(
        melt,
        x="district_name", y="Score", color="Sub-Index",
        barmode="group",
        color_discrete_sequence=["#6366f1", "#f59e0b", "#ef4444"],
        labels={"district_name": "District", "Score": "Index Score (0–100)"},
    )
    fig2.update_layout(
        plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
        font_color="#e2e8f0",  legend_bgcolor="#1e2130",
        xaxis=dict(gridcolor="#2d3250"), yaxis=dict(gridcolor="#2d3250"),
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Job Displacement Risk vs Infrastructure Gap")
    fig3 = px.scatter(
        filtered,
        x="infrastructure_gap_index",
        y="job_impact_index",
        color="ai_equity_class",
        color_discrete_map=color_map,
        size="ai_equity_index",
        text="district_name",
        hover_data=["state_name", "rural_penetration_pct", "net_displacement_risk"],
        labels={
            "infrastructure_gap_index": "Infrastructure Gap Index →",
            "job_impact_index":         "Job Displacement Risk Index ↑",
        }
    )
    fig3.add_shape(type="line", x0=50, x1=50, y0=0, y1=100,
                   line=dict(color="#6366f1", dash="dot", width=1))
    fig3.add_shape(type="line", x0=0, x1=100, y0=50, y1=50,
                   line=dict(color="#6366f1", dash="dot", width=1))
    fig3.add_annotation(x=75, y=75, text="⚠️ Highest risk zone",
                        showarrow=False, font=dict(color="#ef4444", size=11))
    fig3.update_layout(
        plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
        font_color="#e2e8f0",  legend_bgcolor="#1e2130",
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("The Numbers That Tell the Story")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### India's AI Infrastructure Gap (TRAI 2024)")
        gap_data = pd.DataFrame({
            "Category": ["Urban India", "Rural India", "Urban (pilot avg)", "Rural (pilot avg)"],
            "Broadband Penetration (%)": [93.0, 29.3,
                                           filtered["urban_penetration_pct"].mean(),
                                           filtered["rural_penetration_pct"].mean()],
        })
        fig4 = px.bar(gap_data, x="Category", y="Broadband Penetration (%)",
                      color="Category",
                      color_discrete_sequence=["#6366f1","#ef4444","#818cf8","#f87171"],
                      text="Broadband Penetration (%)")
        fig4.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig4.update_layout(
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e2e8f0", showlegend=False,
            yaxis=dict(range=[0, 110], gridcolor="#2d3250"),
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col_b:
        st.markdown("#### AI Job Exposure Gap (OECD 2024)")
        exposure = pd.DataFrame({
            "Segment": ["Urban workers (avg)", "Rural workers (avg)",
                        "Highest (Stockholm/Prague)", "Lowest (Cauca, Colombia)"],
            "AI Job Exposure (%)": [32, 21, 45, 13],
        })
        fig5 = px.bar(exposure, x="Segment", y="AI Job Exposure (%)",
                      color="Segment",
                      color_discrete_sequence=["#6366f1","#ef4444","#22c55e","#f59e0b"],
                      text="AI Job Exposure (%)")
        fig5.update_traces(texttemplate="%{text}%", textposition="outside")
        fig5.update_layout(
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e2e8f0", showlegend=False,
            yaxis=dict(range=[0, 55], gridcolor="#2d3250"),
        )
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Key Finding")
    st.info("""
    **Urban workers are being upskilled by AI. Rural workers are being displaced without replacement.**
    
    - Cashiers: 65% at automation risk | Manufacturing: 45% | Farm labour: 25%
    - These jobs are not being replaced by AI-augmented equivalents in rural areas
    - Urban AI adoption is growing **2x faster** than rural adoption
    - Under business-as-usual, the gap compounds every year
    
    *Source: OECD 2024, FAO, TRAI 2024, UNDP 2025*
    """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "AIRIS v0.1 — Pilot (10 districts) | "
    "Data: TRAI Q3 2024, PLFS 2023-24, OECD 2024, FAO | "
    "Built for research. Not government data."
)
