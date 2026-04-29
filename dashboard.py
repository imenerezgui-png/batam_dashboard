"""
Batam Meta Ads Dashboard
Interactive Streamlit dashboard for Facebook/Instagram campaign analytics.
"""
from pathlib import Path
import base64

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ---------------------------------------------------------------------------
# Plotly default dark template matching the dashboard theme
# ---------------------------------------------------------------------------
pio.templates["batam"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, sans-serif", color="#e2e8f0", size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=["#a855f7", "#6366f1", "#3b82f6", "#22d3ee",
                  "#f472b6", "#facc15", "#34d399", "#fb7185"],
        title=dict(font=dict(size=16, color="#f1f5f9", family="Inter")),
        legend=dict(bgcolor="rgba(20,26,43,0.6)",
                    bordercolor="rgba(148,163,184,0.15)", borderwidth=1),
        xaxis=dict(gridcolor="rgba(148,163,184,0.10)", zerolinecolor="rgba(148,163,184,0.15)",
                   linecolor="rgba(148,163,184,0.20)", tickfont=dict(color="#94a3b8")),
        yaxis=dict(gridcolor="rgba(148,163,184,0.10)", zerolinecolor="rgba(148,163,184,0.15)",
                   linecolor="rgba(148,163,184,0.20)", tickfont=dict(color="#94a3b8")),
        hoverlabel=dict(bgcolor="#141a2b", bordercolor="#a855f7",
                        font=dict(color="#f1f5f9", family="Inter")),
    ),
    data=dict(
        bar=[go.Bar(marker=dict(cornerradius=8, line=dict(width=0)))],
    ),
)
pio.templates.default = "batam"

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Batam Meta Ads Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — modern dark theme inspired by analytics dashboards
# ---------------------------------------------------------------------------
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
    /* ===== Global ===== */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    .stApp {
        background:
            radial-gradient(ellipse at top left, rgba(168, 85, 247, 0.10), transparent 50%),
            radial-gradient(ellipse at bottom right, rgba(59, 130, 246, 0.10), transparent 50%),
            linear-gradient(180deg, #0b0f1a 0%, #0f1424 100%);
        color: #e2e8f0;
    }
    /* Hide default header */
    header[data-testid="stHeader"] { background: transparent; }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1220 0%, #141a2b 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.12);
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label { color: #cbd5e1; }

    /* ===== Title h1 ===== */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #f8fafc 0%, #c4b5fd 60%, #a78bfa 100%);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    h2, h3, h4 { color: #f1f5f9 !important; font-weight: 700 !important; letter-spacing: -0.01em; }

    /* ===== KPI cards ===== */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 22px 24px;
        box-shadow:
            0 4px 12px rgba(0, 0, 0, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #a855f7, #6366f1, #3b82f6);
        opacity: 0.85;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(168, 85, 247, 0.45);
        box-shadow:
            0 12px 28px rgba(168, 85, 247, 0.18),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }
    div[data-testid="stMetric"] label {
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: #f8fafc !important;
        margin-top: 4px;
    }

    /* ===== Tabs ===== */
    div[data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(20, 26, 43, 0.55);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(148, 163, 184, 0.10);
    }
    button[data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }
    button[data-baseweb="tab"]:hover { color: #f1f5f9 !important; background: rgba(168, 85, 247, 0.08) !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(168, 85, 247, 0.35);
    }
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display: none !important; }

    /* ===== Buttons / radios / multiselect chips ===== */
    .stButton > button {
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%);
        color: white; border: none; border-radius: 10px;
        font-weight: 600; padding: 8px 16px;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.25);
        transition: transform 0.15s ease;
    }
    .stButton > button:hover { transform: translateY(-1px); }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background: rgba(20, 26, 43, 0.7) !important;
        border-color: rgba(148, 163, 184, 0.22) !important;
        border-radius: 10px !important;
    }

    /* ===== Containers / dividers ===== */
    hr { border-color: rgba(148, 163, 184, 0.15) !important; }
    div[data-testid="stExpander"] {
        background: rgba(20, 26, 43, 0.55);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 14px;
    }

    /* ===== Plotly chart container ===== */
    div[data-testid="stPlotlyChart"] {
        background: transparent !important;
        border: none;
        border-radius: 16px;
        padding: 8px;
        filter: drop-shadow(0 12px 28px rgba(0, 0, 0, 0.45))
                drop-shadow(0 4px 10px rgba(168, 85, 247, 0.15));
        transition: filter 0.25s ease, transform 0.25s ease;
    }
    div[data-testid="stPlotlyChart"]:hover {
        filter: drop-shadow(0 18px 36px rgba(0, 0, 0, 0.55))
                drop-shadow(0 6px 14px rgba(168, 85, 247, 0.25));
        transform: translateY(-2px);
    }
    div[data-testid="stPlotlyChart"] .js-plotly-plot,
    div[data-testid="stPlotlyChart"] .plot-container,
    div[data-testid="stPlotlyChart"] .svg-container,
    div[data-testid="stPlotlyChart"] .main-svg {
        background: transparent !important;
    }

    /* ===== Info / warning blocks ===== */
    div[data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid rgba(168, 85, 247, 0.25);
        background: rgba(168, 85, 247, 0.08) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_FILE = Path(__file__).parent / "mg_batam.xlsx"
PLATFORM_FILE = Path(__file__).parent / "mg_batam_plateform.csv"

# Column name constants (French headers from the source file)
COL_START = "Début des rapports"
COL_END = "Fin des rapports"
COL_CAMPAIGN = "Nom de la campagne"
COL_AGE = "Âge"
COL_PLATFORM = "Plateforme"
COL_MONTH = "mois"
COL_YEAR = "annee"
COL_RESULT = "Résultats"
COL_OBJECTIVE = "Indicateur de résultats"
COL_REACH = "Couverture"
COL_IMPRESSIONS = "Impressions"
COL_FREQ = "Répétition"
COL_CPM = "CPM (Coût pour 1\u00a0000\u00a0impressions) (USD)"
COL_CLICKS = "Clics (tous)"
COL_CTR = "CTR (tous)"
COL_CPC_ALL = "CPC (tous) (USD)"
COL_POST_ENG = "Interactions avec la publication"
COL_COMMENTS = "Commentaires sur la publication"
COL_REACTIONS = "Réactions à une publication"
COL_SHARES = "Partages de publications"
COL_LIKES = "J\u2019aime sur Facebook"
COL_LINK_CLICKS = "Clics sur un lien"
COL_LINK_CPC = "CPC (coût par clic sur un lien) (USD)"
COL_THRUPLAYS = "ThruPlays"
COL_3SEC_VIEWS = "Lectures de vidéo de 3 secondes"
COL_IG_FOLLOWERS = "Followers sur Instagram"
COL_MSG = "Conversations par messages démarrées"
COL_PURCHASES = "Achats"
COL_ADD_CART = "Ajouts au panier"
COL_PAY_INFO = "Ajouts d\u2019informations de paiement"
COL_CHECKOUT = "Paiements initiés"
COL_LEADS = "Prospects"
COL_CONTENT_VIEWS = "Vues de contenu"
COL_ROAS = "ROAS (retour sur les dépenses publicitaires) des achats"
COL_CONV_RATE = "Conversion rate"
COL_COST_PER_RESULT = "Coût par résultat"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading data…")
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
    for c in (COL_START, COL_END):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    # Estimated spend = clicks * CPC (proxy when no spend column exists)
    df["Spend (est.)"] = (df[COL_CLICKS].fillna(0) * df[COL_CPC_ALL].fillna(0)).round(2)
    return df


@st.cache_data
def load_uploaded(file) -> pd.DataFrame:
    df = pd.read_excel(file)
    for c in (COL_START, COL_END):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    df["Spend (est.)"] = (df[COL_CLICKS].fillna(0) * df[COL_CPC_ALL].fillna(0)).round(2)
    return df


@st.cache_data(show_spinner="Loading platform data…")
def load_platform_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for c in (COL_START, COL_END):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    df["Spend (est.)"] = (df[COL_CLICKS].fillna(0) * df[COL_CPC_ALL].fillna(0)).round(2)
    return df


pdf = load_platform_data(PLATFORM_FILE) if PLATFORM_FILE.exists() else None


# ---------------------------------------------------------------------------
# Sidebar — data source + filters
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Controls")

uploaded = st.sidebar.file_uploader("Upload Meta Ads export (.xlsx)", type=["xlsx"])
if uploaded is not None:
    df = load_uploaded(uploaded)
elif DATA_FILE.exists():
    df = load_data(DATA_FILE)
else:
    st.error(
        f"No data file found. Place `mg_batam.xlsx` next to `dashboard.py` "
        f"or upload an export in the sidebar."
    )
    st.stop()

st.sidebar.markdown("### Filters")

campaigns = sorted(df[COL_CAMPAIGN].dropna().unique().tolist())
sel_campaigns = st.sidebar.multiselect("Campaign", campaigns, default=campaigns)

ages = sorted(df[COL_AGE].dropna().unique().tolist())
sel_ages = st.sidebar.multiselect("Age group", ages, default=ages)

objectives = sorted(df[COL_OBJECTIVE].dropna().unique().tolist())
sel_obj = st.sidebar.multiselect("Objective", objectives, default=objectives)

# Platform-view filters (only used inside the Platform tab)
if pdf is not None and not pdf.empty:
    with st.sidebar.expander("🔀 Platform view filters", expanded=False):
        st.caption("Used only on the **Platform (FB vs IG)** tab.")
        plat_campaigns_all = sorted(pdf[COL_CAMPAIGN].dropna().unique().tolist())
        sel_pcamp = st.multiselect(
            "Campaigns", plat_campaigns_all,
            default=plat_campaigns_all, key="plat_camp_filter",
        )
else:
    sel_pcamp = []

mask = (
    df[COL_CAMPAIGN].isin(sel_campaigns)
    & df[COL_AGE].isin(sel_ages)
    & df[COL_OBJECTIVE].isin(sel_obj)
)

# ---------------------------------------------------------------------------
# Cross-filter state (set by clicking on charts)
# ---------------------------------------------------------------------------
st.session_state.setdefault("xf_campaigns", [])
st.session_state.setdefault("xf_age", [])
st.session_state.setdefault("xf_objective", [])

xf_camp = st.session_state["xf_campaigns"]
xf_age = st.session_state["xf_age"]
xf_obj = st.session_state["xf_objective"]

if xf_camp:
    mask &= df[COL_CAMPAIGN].isin(xf_camp)
if xf_age:
    mask &= df[COL_AGE].isin(xf_age)
if xf_obj:
    mask &= df[COL_OBJECTIVE].isin(xf_obj)

fdf = df.loc[mask].copy()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
@st.cache_data
def _img_b64(path_str: str) -> str:
    return base64.b64encode(Path(path_str).read_bytes()).decode()


_logo_path = Path(__file__).parent / "ykone_logo.jpg"
if _logo_path.exists():
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:22px; margin: 6px 0 14px 0;">
            <img src="data:image/jpeg;base64,{_img_b64(str(_logo_path))}"
                 style="height:78px; width:78px; object-fit:cover;
                        border-radius:18px; background:#000; padding:4px;
                        box-shadow:
                            0 0 14px rgba(255,255,255,0.85),
                            0 0 32px rgba(180,200,255,0.55),
                            0 0 60px rgba(120,150,255,0.35),
                            0 8px 22px rgba(0,0,0,0.45);
                        animation: ykoneGlow 3.2s ease-in-out infinite;" />
            <div>
                <h1 style="margin:0; padding:0; font-size:2.1rem;">
                    Batam — Meta Ads Performance Dashboard
                </h1>
            </div>
        </div>
        <style>
        @keyframes ykoneGlow {{
            0%, 100% {{
                box-shadow:
                    0 0 14px rgba(255,255,255,0.85),
                    0 0 32px rgba(180,200,255,0.55),
                    0 0 60px rgba(120,150,255,0.35),
                    0 8px 22px rgba(0,0,0,0.45);
            }}
            50% {{
                box-shadow:
                    0 0 22px rgba(255,255,255,1),
                    0 0 48px rgba(200,215,255,0.75),
                    0 0 80px rgba(150,180,255,0.55),
                    0 8px 22px rgba(0,0,0,0.45);
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.title("📊 Batam — Meta Ads Performance Dashboard")

st.caption(
    f"{len(fdf):,} rows · {fdf[COL_CAMPAIGN].nunique()} campaigns · "
    f"{fdf[COL_AGE].nunique()} age groups"
)

# Active cross-filter chips + reset
active = []
if xf_camp:
    active.append(f"Campaign: {', '.join(map(str, xf_camp))}")
if xf_age:
    active.append(f"Age: {', '.join(map(str, xf_age))}")
if xf_obj:
    active.append(f"Objective: {', '.join(map(str, xf_obj))}")
if active:
    chip_col, btn_col = st.columns([5, 1])
    with chip_col:
        st.info("🔍 **Active chart filters** — " + " · ".join(active))
    with btn_col:
        if st.button("✖ Clear", use_container_width=True):
            st.session_state["xf_campaigns"] = []
            st.session_state["xf_age"] = []
            st.session_state["xf_objective"] = []
            st.rerun()

if fdf.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ---------------------------------------------------------------------------
# Formatting helpers (used across tabs)
# ---------------------------------------------------------------------------
def fmt_int(x):
    return f"{int(x):,}" if pd.notna(x) else "—"


def fmt_money(x):
    return f"${x:,.2f}" if pd.notna(x) else "—"


def fmt_pct(x):
    return f"{x:.2f}%" if pd.notna(x) else "—"


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_plat, tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🌐 Global Overview Meta", "📈 Reach & Impressions", "💰 Cost & Efficiency",
     "❤️ Engagement", "🎯 Audience & Funnel", "🗂️ Raw Data"]
)

# ---- Tab 1: Reach & Impressions ----
with tab1:
    st.caption("💡 **Tip:** click bars / slices below to filter the whole dashboard.")

    by_camp = (
        fdf.groupby(COL_CAMPAIGN, as_index=False)[[COL_IMPRESSIONS, COL_REACH]]
        .sum()
        .sort_values(COL_IMPRESSIONS, ascending=False)
        .head(20)
    )
    fig = go.Figure()
    fig.add_bar(name="Impressions", x=by_camp[COL_CAMPAIGN], y=by_camp[COL_IMPRESSIONS])
    fig.add_bar(name="Reach", x=by_camp[COL_CAMPAIGN], y=by_camp[COL_REACH])
    fig.update_layout(
        barmode="group", title="Top 20 Campaigns — Impressions vs Reach (click a bar to filter)",
        xaxis_tickangle=-40, height=520, legend_orientation="h",
    )
    sel = st.plotly_chart(
        fig, use_container_width=True, key="chart_camp",
        on_select="rerun", selection_mode=("points",),
    )
    picks = [p["x"] for p in (sel.selection.get("points") or [])]
    if picks and set(picks) != set(st.session_state["xf_campaigns"]):
        st.session_state["xf_campaigns"] = picks
        st.rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        by_obj = fdf.groupby(COL_OBJECTIVE, as_index=False)[COL_IMPRESSIONS].sum()
        fig = px.pie(by_obj, names=COL_OBJECTIVE, values=COL_IMPRESSIONS,
                     title="Impressions share by objective (click a slice)", hole=0.4)
        sel = st.plotly_chart(
            fig, use_container_width=True, key="chart_obj",
            on_select="rerun", selection_mode=("points",),
        )
        picks = [p["label"] for p in (sel.selection.get("points") or [])]
        if picks and set(picks) != set(st.session_state["xf_objective"]):
            st.session_state["xf_objective"] = picks
            st.rerun()
    with col_b:
        by_age = fdf.groupby(COL_AGE, as_index=False)[[COL_IMPRESSIONS, COL_REACH]].sum()
        fig = px.bar(by_age, x=COL_AGE, y=[COL_IMPRESSIONS, COL_REACH],
                     barmode="group", title="Impressions & Reach by age group (click a bar)")
        sel = st.plotly_chart(
            fig, use_container_width=True, key="chart_age",
            on_select="rerun", selection_mode=("points",),
        )
        picks = [p["x"] for p in (sel.selection.get("points") or [])]
        if picks and set(picks) != set(st.session_state["xf_age"]):
            st.session_state["xf_age"] = picks
            st.rerun()

# ---- Tab 2: Cost & Efficiency ----
with tab2:
    cost_df = (
        fdf.groupby(COL_CAMPAIGN, as_index=False)
        .agg({COL_CTR: "mean", COL_CPC_ALL: "mean", COL_CPM: "mean",
              "Spend (est.)": "sum"})
        .sort_values("Spend (est.)", ascending=False)
        .head(20)
    )

    CHART_HEIGHT = 500

    fig = px.bar(cost_df, x=COL_CAMPAIGN, y="Spend (est.)",
                 title="Estimated spend by campaign (top 20)",
                 color="Spend (est.)", color_continuous_scale="Blues")
    fig.update_layout(xaxis_tickangle=-40, height=CHART_HEIGHT)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(cost_df.melt(id_vars=COL_CAMPAIGN,
                              value_vars=[COL_CTR, COL_CPC_ALL, COL_CPM]),
                 x=COL_CAMPAIGN, y="value", color="variable", barmode="group",
                 title="CTR / CPC / CPM by campaign (top 20 by spend)")
    fig.update_layout(xaxis_tickangle=-40, height=CHART_HEIGHT)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.scatter(
        fdf, x=COL_CPC_ALL, y=COL_CTR, size=COL_IMPRESSIONS,
        color=COL_OBJECTIVE, hover_name=COL_CAMPAIGN,
        title="CTR vs CPC (bubble = Impressions)",
    )
    fig.update_layout(height=CHART_HEIGHT)
    st.plotly_chart(fig, use_container_width=True)

# ---- Tab 3: Engagement ----
with tab3:
    eng_cols = [COL_LIKES, COL_REACTIONS, COL_COMMENTS, COL_SHARES]
    eng = (
        fdf.groupby(COL_CAMPAIGN, as_index=False)[eng_cols]
        .sum()
        .assign(total=lambda d: d[eng_cols].sum(axis=1))
        .sort_values("total", ascending=False)
        .head(15)
        .drop(columns="total")
    )
    fig = px.bar(
        eng.melt(id_vars=COL_CAMPAIGN, var_name="metric", value_name="count"),
        x=COL_CAMPAIGN, y="count", color="metric", barmode="stack",
        title="Engagement breakdown — Top 15 campaigns",
    )
    fig.update_layout(xaxis_tickangle=-40, height=520)
    st.plotly_chart(fig, use_container_width=True)

    video = fdf[[COL_CAMPAIGN, COL_3SEC_VIEWS, COL_THRUPLAYS]].dropna(
        subset=[COL_3SEC_VIEWS, COL_THRUPLAYS], how="all"
    )
    if not video.empty:
        video = video.groupby(COL_CAMPAIGN, as_index=False).sum().sort_values(
            COL_3SEC_VIEWS, ascending=False
        ).head(15)
        fig = px.bar(video, x=COL_CAMPAIGN, y=[COL_3SEC_VIEWS, COL_THRUPLAYS],
                     barmode="group", title="Video performance")
        fig.update_layout(xaxis_tickangle=-40, height=520)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No video metrics in current selection.")

    ig = fdf.groupby(COL_CAMPAIGN, as_index=False)[COL_IG_FOLLOWERS].sum()
    ig = ig[ig[COL_IG_FOLLOWERS] > 0].sort_values(COL_IG_FOLLOWERS, ascending=False).head(15)
    if not ig.empty:
        fig = px.bar(ig, x=COL_CAMPAIGN, y=COL_IG_FOLLOWERS,
                     title="Instagram followers gained", color=COL_IG_FOLLOWERS,
                     color_continuous_scale="Magenta")
        fig.update_layout(xaxis_tickangle=-40, height=520)
        st.plotly_chart(fig, use_container_width=True)

# ---- Tab 4: Audience & Funnel ----
with tab4:
    col_a, col_b = st.columns(2)
    with col_a:
        age_perf = fdf.groupby(COL_AGE, as_index=False).agg(
            Impressions=(COL_IMPRESSIONS, "sum"),
            Clicks=(COL_CLICKS, "sum"),
            CTR=(COL_CTR, "mean"),
            CPC=(COL_CPC_ALL, "mean"),
        )
        fig = px.bar(age_perf, x=COL_AGE, y="Clicks", color="CTR",
                     title="Clicks per age group (color = avg CTR)",
                     color_continuous_scale="Viridis")
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        funnel_vals = {
            "Content views": fdf[COL_CONTENT_VIEWS].sum(),
            "Link clicks": fdf[COL_LINK_CLICKS].sum(),
            "Add to cart": fdf[COL_ADD_CART].sum(),
            "Checkout": fdf[COL_CHECKOUT].sum(),
            "Payment info": fdf[COL_PAY_INFO].sum(),
            "Purchases": fdf[COL_PURCHASES].sum(),
        }
        funnel_vals = {k: v for k, v in funnel_vals.items() if pd.notna(v) and v > 0}
        if funnel_vals:
            fig = go.Figure(go.Funnel(
                y=list(funnel_vals.keys()),
                x=list(funnel_vals.values()),
                textinfo="value+percent initial",
            ))
            fig.update_layout(title="Conversion funnel", height=420)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No conversion events in current selection.")

    # ROAS / leads / messages summary
    col_c, col_d, col_e = st.columns(3)
    col_c.metric("Total Leads", fmt_int(fdf[COL_LEADS].sum()))
    col_d.metric("Messages started", fmt_int(fdf[COL_MSG].sum()))
    roas = fdf[COL_ROAS].dropna()
    col_e.metric("Avg ROAS", f"{roas.mean():.2f}" if not roas.empty else "—")

# ---- Tab Platform: Facebook vs Instagram comparison ----
with tab_plat:
    if pdf is None or pdf.empty:
        st.warning(
            "Platform-level dataset not found. Place `mg_batam_plateform.csv` next "
            "to `dashboard.py`."
        )
    else:
        st.caption(
            "Comparison of all KPIs and their costs **by platform** "
            "(Facebook vs Instagram). Use the **🔀 Platform view filters** "
            "section in the sidebar to narrow campaigns."
        )

        ppdf = pdf[pdf[COL_CAMPAIGN].isin(sel_pcamp)].copy()

        if ppdf.empty:
            st.info("No campaigns selected.")
            st.stop()

        # ---- Top KPI cards per platform ----
        st.subheader("KPIs per platform")

        plat_options = ["All"] + sorted(ppdf[COL_PLATFORM].dropna().unique().tolist())
        plat_view = st.radio(
            "View", plat_options, horizontal=True, key="plat_kpi_view",
        )

        agg = ppdf.groupby(COL_PLATFORM, as_index=False).agg(
            Impressions=(COL_IMPRESSIONS, "sum"),
            Reach=(COL_REACH, "sum"),
            Clicks=(COL_CLICKS, "sum"),
            Spend=("Spend (est.)", "sum"),
            Purchases=(COL_PURCHASES, "sum"),
            CTR=(COL_CTR, "mean"),
            CPC=(COL_CPC_ALL, "mean"),
            CPM=(COL_CPM, "mean"),
            Frequency=(COL_FREQ, "mean"),
        )

        if plat_view == "All":
            # Aggregated across both platforms
            sub = ppdf
            row = {
                "Impressions": sub[COL_IMPRESSIONS].sum(),
                "Reach": sub[COL_REACH].sum(),
                "Clicks": sub[COL_CLICKS].sum(),
                "Spend": sub["Spend (est.)"].sum(),
                "Purchases": sub[COL_PURCHASES].sum(),
                "CTR": sub[COL_CTR].mean(),
                "CPC": sub[COL_CPC_ALL].mean(),
                "CPM": sub[COL_CPM].mean(),
                "Frequency": sub[COL_FREQ].mean(),
            }
            label = "All platforms"
        else:
            row = agg[agg[COL_PLATFORM] == plat_view].iloc[0].to_dict()
            label = plat_view

        st.markdown(f"#### {label}")
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Impressions", fmt_int(row["Impressions"]))
        k2.metric("Reach", fmt_int(row["Reach"]))
        k3.metric("Clicks", fmt_int(row["Clicks"]))
        k4.metric("Spend (est.)", fmt_money(row["Spend"]))
        k5.metric("Purchases", fmt_int(row["Purchases"]))

        k6, k7, k8, k9 = st.columns(4)
        k6.metric("Avg CTR", fmt_pct(row["CTR"]))
        k7.metric("Avg CPC", fmt_money(row["CPC"]))
        k8.metric("Avg CPM", fmt_money(row["CPM"]))
        k9.metric("Avg frequency", f"{row['Frequency']:.2f}" if pd.notna(row["Frequency"]) else "—")

        st.divider()

        # ---- Volume KPI bar chart ----
        vol_long = agg.melt(
            id_vars=COL_PLATFORM,
            value_vars=["Impressions", "Reach", "Clicks", "Purchases"],
            var_name="KPI", value_name="value",
        )
        fig = px.bar(
            vol_long, x="KPI", y="value", color=COL_PLATFORM,
            barmode="group", text_auto=".2s",
            title="Volume KPIs — Facebook vs Instagram",
            color_discrete_map={"Facebook": "#1877F2", "Instagram": "#E4405F"},
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

        # ---- Cost / efficiency comparison ----
        col_a, col_b = st.columns(2)
        with col_a:
            cost_long = agg.melt(
                id_vars=COL_PLATFORM,
                value_vars=["CTR", "CPC", "CPM", "Frequency"],
                var_name="Metric", value_name="value",
            )
            fig = px.bar(
                cost_long, x="Metric", y="value", color=COL_PLATFORM,
                barmode="group", text_auto=".3f",
                title="Avg cost & efficiency metrics",
                color_discrete_map={"Facebook": "#1877F2", "Instagram": "#E4405F"},
            )
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            spend_share = agg[[COL_PLATFORM, "Spend"]].copy()
            fig = px.pie(
                spend_share, names=COL_PLATFORM, values="Spend", hole=0.4,
                title="Estimated spend share",
                color=COL_PLATFORM,
                color_discrete_map={"Facebook": "#1877F2", "Instagram": "#E4405F"},
            )
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

        # ---- Engagement comparison ----
        eng_cols = [COL_LIKES, COL_REACTIONS, COL_COMMENTS, COL_SHARES,
                    COL_POST_ENG]
        eng = ppdf.groupby(COL_PLATFORM, as_index=False)[eng_cols].sum()
        eng_long = eng.melt(id_vars=COL_PLATFORM, var_name="Metric",
                            value_name="value")
        fig = px.bar(
            eng_long, x="Metric", y="value", color=COL_PLATFORM,
            barmode="group", text_auto=".2s",
            title="Engagement metrics by platform",
            color_discrete_map={"Facebook": "#1877F2", "Instagram": "#E4405F"},
        )
        fig.update_layout(height=420, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

        # ---- Conversion funnel side-by-side ----
        funnel_metrics = {
            "Content views": COL_CONTENT_VIEWS,
            "Link clicks": COL_LINK_CLICKS,
            "Add to cart": COL_ADD_CART,
            "Checkout": COL_CHECKOUT,
            "Payment info": COL_PAY_INFO,
            "Purchases": COL_PURCHASES,
        }
        platforms = sorted(ppdf[COL_PLATFORM].dropna().unique().tolist())
        funnel_cols = st.columns(len(platforms))
        for col, plat in zip(funnel_cols, platforms):
            sub = ppdf[ppdf[COL_PLATFORM] == plat]
            vals = {label: sub[c].sum() for label, c in funnel_metrics.items()}
            vals = {k: v for k, v in vals.items() if pd.notna(v) and v > 0}
            with col:
                if vals:
                    color = "#1877F2" if plat == "Facebook" else "#E4405F"
                    fig = go.Figure(go.Funnel(
                        y=list(vals.keys()), x=list(vals.values()),
                        textinfo="value+percent initial",
                        marker={"color": color},
                    ))
                    fig.update_layout(title=f"{plat} funnel", height=380)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No conversion events for {plat}.")

        # ---- Per-campaign platform comparison ----
        st.subheader("Per-campaign comparison")
        kpi_choice = st.selectbox(
            "Metric to compare per campaign",
            ["Impressions", "Reach", "Clicks", "Spend (est.)", "Purchases",
             COL_CTR, COL_CPC_ALL, COL_CPM],
            index=0,
        )
        agg_func = "mean" if kpi_choice in (COL_CTR, COL_CPC_ALL, COL_CPM) else "sum"
        col_map = {
            "Impressions": COL_IMPRESSIONS, "Reach": COL_REACH,
            "Clicks": COL_CLICKS, "Spend (est.)": "Spend (est.)",
            "Purchases": COL_PURCHASES,
        }
        col_to_use = col_map.get(kpi_choice, kpi_choice)
        per_camp = (
            ppdf.groupby([COL_CAMPAIGN, COL_PLATFORM], as_index=False)[col_to_use]
            .agg(agg_func)
        )
        fig = px.bar(
            per_camp, x=COL_CAMPAIGN, y=col_to_use, color=COL_PLATFORM,
            barmode="group", title=f"{kpi_choice} by campaign & platform",
            color_discrete_map={"Facebook": "#1877F2", "Instagram": "#E4405F"},
        )
        fig.update_layout(xaxis_tickangle=-40, height=560)
        st.plotly_chart(fig, use_container_width=True)

        # ---- Trend by month if available ----
        if COL_MONTH in ppdf.columns and COL_YEAR in ppdf.columns:
            month_order = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                           "Juillet", "Août", "Septembre", "Octobre",
                           "Novembre", "Décembre"]
            tdf = ppdf.dropna(subset=[COL_MONTH, COL_YEAR]).copy()
            if not tdf.empty:
                tdf["Période"] = (
                    tdf[COL_MONTH].astype(str) + " " + tdf[COL_YEAR].astype(int).astype(str)
                )
                trend = tdf.groupby(["Période", COL_MONTH, COL_YEAR, COL_PLATFORM],
                                    as_index=False)[
                    [COL_IMPRESSIONS, COL_CLICKS, "Spend (est.)"]
                ].sum()
                trend["_m"] = trend[COL_MONTH].apply(
                    lambda m: month_order.index(m) if m in month_order else 99
                )
                trend = trend.sort_values([COL_YEAR, "_m"])
                fig = px.line(
                    trend, x="Période", y="Spend (est.)", color=COL_PLATFORM,
                    markers=True, title="Spend trend by month & platform",
                    color_discrete_map={"Facebook": "#1877F2", "Instagram": "#E4405F"},
                )
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Platform raw data"):
            st.dataframe(ppdf, use_container_width=True, height=400)

# ---- Tab 5: Raw Data ----
with tab5:
    st.dataframe(fdf, use_container_width=True, height=600)
    csv = fdf.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered data (CSV)", csv,
                       file_name="batam_filtered.csv", mime="text/csv")
