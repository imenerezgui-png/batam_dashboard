"""
Biocyte Meta Ads Dashboard
Interactive Streamlit dashboard for the Biocyte Meta Ads export.
"""
from pathlib import Path
import base64
import re

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
_PAGE_ICON_PATH = Path(__file__).parent / "3sg_logo.png"

st.set_page_config(
    page_title="Biocyte Meta & Google Ads Dashboard",
    page_icon=str(_PAGE_ICON_PATH) if _PAGE_ICON_PATH.exists() else "📊",
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

    /* ===== Total-results inline selectbox ===== */
    div[data-testid="stSelectbox"]:has(div[data-baseweb="select"]) div[data-baseweb="select"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 0.68rem !important;
        color: #94a3b8 !important;
        padding: 0 !important;
        min-height: unset !important;
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

    /* ===== Summary takeaway cards ===== */
    .summary-card {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.18), rgba(99, 102, 241, 0.10) 60%, rgba(20, 26, 43, 0.55));
        border: 1px solid rgba(168, 85, 247, 0.30);
        border-left: 4px solid #a855f7;
        border-radius: 16px;
        padding: 18px 22px 14px 22px;
        margin: 4px 0 22px 0;
        box-shadow: 0 10px 28px rgba(0,0,0,0.35), 0 0 0 1px rgba(168,85,247,0.05);
        backdrop-filter: blur(8px);
    }
    .summary-card-title {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.0rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: #f5d0fe;
        margin-bottom: 8px;
    }
    .summary-card-list {
        margin: 0;
        padding-left: 1.1rem;
        color: #e2e8f0;
        font-size: 0.94rem;
        line-height: 1.55;
    }
    .summary-card-list li { margin-bottom: 4px; }
    .summary-card-list li b, .summary-card-list li strong { color: #f0abfc; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Data source — Biocyte Meta Ads export
# ---------------------------------------------------------------------------
DATA_FILE = Path(__file__).parent / "Biocyte 29-avr-2023-28-mai-2026.xlsx"

# Column name constants (French headers from the Biocyte source file)
COL_START          = "Début des rapports"
COL_END            = "Fin des rapports"
COL_AD             = "Nom de la publicité"
COL_CAMPAIGN       = "Nom de la campagne"
COL_ADSET          = "Nom de l\u2019ensemble de publicités"  # curly apostrophe
COL_RESULT         = "Résultats"
COL_OBJECTIVE      = "Indicateur de résultats"
COL_SPEND          = "Montant dépensé (EUR)"
COL_REACH          = "Couverture"
COL_IMPRESSIONS    = "Impressions"
COL_FREQ           = "Répétition"
COL_3SEC_VIEWS     = "Lectures de vidéo de 3 secondes"
COL_THRUPLAYS      = "ThruPlays"
COL_CLICKS         = "Clics (tous)"
COL_LINK_CLICKS    = "Clics sur un lien"
COL_UNIQUE_LCLICKS = "Clics uniques sur un lien"
COL_CTR            = "CTR (tous)"
COL_LANDING_VIEWS  = "Vues de page de destination"
COL_IG_VISITS      = "Visites du profil\u00a0Instagram"
COL_POST_ENG       = "Interactions avec la publication"
COL_REACTIONS      = "Réactions à une publication"
COL_COMMENTS       = "Commentaires sur la publication"
COL_SHARES         = "Partages de publications"
COL_LIKES          = "J\u2019aime sur Facebook"          # curly apostrophe
COL_IG_FOLLOWERS   = "Followers sur Instagram"
COL_MSG            = "Conversations par messages démarrées"
COL_CONTENT_VIEWS  = "Vues de contenu"
COL_ADD_CART       = "Ajouts au panier"
COL_CHECKOUT       = "Paiements initiés"
COL_PAY_INFO       = "Ajouts d\u2019informations de paiement"  # curly apostrophe
COL_PURCHASES      = "Achats"
COL_CART_VALUE     = "Valeur de conversion des ajouts au panier"
COL_ROAS           = "ROAS (retour sur les dépenses publicitaires) des achats"
COL_LEADS          = "Prospects"
COL_SIGNUPS        = "Inscriptions terminées"
COL_CPR            = "Coût par résultat"
COL_CPM            = "CPM (Coût pour 1\u00a0000\u00a0impressions) (EUR)"
COL_CPC_ALL        = "CPC (tous) (EUR)"
COL_LINK_CPC       = "CPC (coût par clic sur un lien) (EUR)"
COL_CP_THRUPLAY    = "Coût par ThruPlay (EUR)"
COL_CP_POST_ENG    = "Coût par interaction avec une publication (EUR)"
COL_CP_LANDING     = "Coût par vue de page de destination (EUR)"
COL_CP_CONTENT     = "Coût par vue de contenu (EUR)"
COL_CP_CART        = "Coût par ajout au panier (EUR)"
COL_CP_PAY         = "Coût par ajout des informations de paiement (EUR)"
COL_CP_CHECKOUT    = "Coût par paiement initié (EUR)"
COL_CP_PURCHASE    = "Coût par achat (EUR)"
COL_CP_LEAD        = "Coût par prospect (EUR)"
COL_CP_SIGNUP      = "Coût par inscription terminée (EUR)"

NUMERIC_COLS = [
    COL_RESULT, COL_SPEND, COL_REACH, COL_IMPRESSIONS, COL_FREQ,
    COL_3SEC_VIEWS, COL_THRUPLAYS, COL_CLICKS, COL_LINK_CLICKS,
    COL_UNIQUE_LCLICKS, COL_CTR, COL_LANDING_VIEWS, COL_IG_VISITS,
    COL_POST_ENG, COL_REACTIONS, COL_COMMENTS, COL_SHARES, COL_LIKES,
    COL_IG_FOLLOWERS, COL_MSG, COL_CONTENT_VIEWS, COL_ADD_CART,
    COL_CHECKOUT, COL_PAY_INFO, COL_PURCHASES, COL_CART_VALUE, COL_ROAS,
    COL_LEADS, COL_SIGNUPS, COL_CPR, COL_CPM, COL_CPC_ALL, COL_LINK_CPC,
    COL_CP_THRUPLAY, COL_CP_POST_ENG, COL_CP_LANDING, COL_CP_CONTENT,
    COL_CP_CART, COL_CP_PAY, COL_CP_CHECKOUT, COL_CP_PURCHASE,
    COL_CP_LEAD, COL_CP_SIGNUP,
]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
COL_GOAL   = "Goal"             # derived: text between '-' and '(' in campaign name
COL_BUDGET = "Budget (€)"        # derived: number before '€' inside parentheses

# e.g. "MAY- Lead Gen (350€ budget engagement)" → goal="Lead Gen", budget=350
_GOAL_RE   = re.compile(r"-\s*([^()\-]+?)\s*\(")
_BUDGET_RE = re.compile(r"\(\s*(\d+(?:[.,]\d+)?)\s*€")


def _extract_goal(name) -> str | None:
    if not isinstance(name, str):
        return None
    m = _GOAL_RE.search(name)
    return m.group(1).strip() if m else None


def _extract_budget(name) -> float | None:
    if not isinstance(name, str):
        return None
    m = _BUDGET_RE.search(name)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "."))
    except ValueError:
        return None


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    for c in (COL_START, COL_END):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in NUMERIC_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if COL_CAMPAIGN in df.columns:
        df[COL_GOAL]   = df[COL_CAMPAIGN].apply(_extract_goal)
        df[COL_BUDGET] = df[COL_CAMPAIGN].apply(_extract_budget)
    return df


@st.cache_data(show_spinner="Loading data…")
def load_data(path: Path) -> pd.DataFrame:
    return _prepare(pd.read_excel(path))


@st.cache_data
def load_uploaded(file) -> pd.DataFrame:
    return _prepare(pd.read_excel(file))


# ---------------------------------------------------------------------------
# Sidebar — data source + filters
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Controls")

uploaded = st.sidebar.file_uploader(
    "Upload Meta Ads export (.xlsx)", type=["xlsx"]
)
if uploaded is not None:
    df = load_uploaded(uploaded)
elif DATA_FILE.exists():
    df = load_data(DATA_FILE)
else:
    st.error(
        f"No data file found. Place `{DATA_FILE.name}` next to "
        f"`dashboard.py` or upload an export in the sidebar."
    )
    st.stop()

st.sidebar.markdown("### Filters")


def _toggle_all(key: str, options: list) -> None:
    """Mirror the 'Select all' checkbox onto every option."""
    val = st.session_state[f"{key}__all"]
    for opt in options:
        st.session_state[f"{key}__opt__{opt}"] = val


def _toggle_one(key: str, options: list) -> None:
    """Keep the 'Select all' checkbox in sync with the children."""
    st.session_state[f"{key}__all"] = all(
        st.session_state.get(f"{key}__opt__{opt}", False) for opt in options
    )


def dropdown_filter(label: str, options: list, key: str, container=None) -> list:
    """Collapsed dropdown with 'Select all' + per-option checkboxes."""
    container = container if container is not None else st.sidebar
    for opt in options:
        ck = f"{key}__opt__{opt}"
        if ck not in st.session_state:
            st.session_state[ck] = True
    if f"{key}__all" not in st.session_state:
        st.session_state[f"{key}__all"] = True

    n = len(options)
    count = sum(1 for opt in options if st.session_state[f"{key}__opt__{opt}"])
    btn_label = f"{label}  —  {count}/{n} selected"
    with container.expander(btn_label, expanded=False):
        st.checkbox(
            "✅ Select all", key=f"{key}__all",
            on_change=_toggle_all, args=(key, options),
        )
        st.divider()
        for opt in options:
            st.checkbox(
                str(opt), key=f"{key}__opt__{opt}",
                on_change=_toggle_one, args=(key, options),
            )
    return [opt for opt in options if st.session_state[f"{key}__opt__{opt}"]]


campaigns = sorted(df[COL_CAMPAIGN].dropna().unique().tolist())
sel_campaigns = dropdown_filter("Campaign", campaigns, key="flt_campaign")

adsets = sorted(df[COL_ADSET].dropna().unique().tolist()) if COL_ADSET in df.columns else []
sel_adsets = (
    dropdown_filter("Ad set", adsets, key="flt_adset")
    if adsets else []
)

ads = sorted(df[COL_AD].dropna().unique().tolist()) if COL_AD in df.columns else []
sel_ads = (
    dropdown_filter("Ad name", ads, key="flt_ad")
    if ads else []
)

objectives = sorted(df[COL_OBJECTIVE].dropna().unique().tolist())
sel_obj = (
    dropdown_filter("Objective", objectives, key="flt_objective")
    if objectives else []
)

goals = sorted(df[COL_GOAL].dropna().unique().tolist()) if COL_GOAL in df.columns else []
sel_goals = (
    dropdown_filter("Campaign goal", goals, key="flt_goal")
    if goals else []
)

mask = df[COL_CAMPAIGN].isin(sel_campaigns)
if adsets:
    mask &= df[COL_ADSET].isin(sel_adsets)
if ads:
    mask &= df[COL_AD].isin(sel_ads)
if objectives:
    mask &= df[COL_OBJECTIVE].isin(sel_obj) | df[COL_OBJECTIVE].isna()
if goals:
    mask &= df[COL_GOAL].isin(sel_goals) | df[COL_GOAL].isna()

# ---------------------------------------------------------------------------
# Cross-filter state (set by clicking on charts)
# ---------------------------------------------------------------------------
st.session_state.setdefault("xf_campaigns", [])
st.session_state.setdefault("xf_adsets", [])
st.session_state.setdefault("xf_objective", [])

xf_camp = st.session_state["xf_campaigns"]
xf_adset = st.session_state["xf_adsets"]
xf_obj = st.session_state["xf_objective"]

if xf_camp:
    mask &= df[COL_CAMPAIGN].isin(xf_camp)
if xf_adset and COL_ADSET in df.columns:
    mask &= df[COL_ADSET].isin(xf_adset)
if xf_obj:
    mask &= df[COL_OBJECTIVE].isin(xf_obj)

fdf = df.loc[mask].copy()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
@st.cache_data
def _img_b64(path_str: str) -> str:
    return base64.b64encode(Path(path_str).read_bytes()).decode()


_logo_path = Path(__file__).parent / "logo-biocyte.webp"
if _logo_path.exists():
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:22px; margin: 6px 0 14px 0;">
            <img src="data:image/webp;base64,{_img_b64(str(_logo_path))}"
                 style="height:78px; width:78px; object-fit:cover;
                        border-radius:18px; background:#E9D4F2; padding:4px;
                        box-shadow:
                            0 0 14px rgba(255,255,255,0.85),
                            0 0 32px rgba(180,200,255,0.55),
                            0 0 60px rgba(120,150,255,0.35),
                            0 8px 22px rgba(0,0,0,0.45);
                        animation: ykoneGlow 3.2s ease-in-out infinite;" />
            <div>
                <h1 style="margin:0; padding:0; font-size:2.1rem;">
                    Meta &amp; Google Ads Performance Dashboard
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
    st.title("Meta & Google Ads Performance Dashboard")

# Reporting period
period_txt = ""
if COL_START in fdf.columns and COL_END in fdf.columns and not fdf.empty:
    dmin = fdf[COL_START].min()
    dmax = fdf[COL_END].max()
    if pd.notna(dmin) and pd.notna(dmax):
        period_txt = f" · {dmin:%d %b %Y} → {dmax:%d %b %Y}"

st.caption(
    f"{len(fdf):,} rows · {fdf[COL_CAMPAIGN].nunique()} campaigns · "
    f"{fdf[COL_ADSET].nunique() if COL_ADSET in fdf.columns else 0} ad sets · "
    f"{fdf[COL_AD].nunique() if COL_AD in fdf.columns else 0} ads{period_txt}"
)

# Active cross-filter chips + reset
active = []
if xf_camp:
    active.append(f"Campaign: {', '.join(map(str, xf_camp))}")
if xf_adset:
    active.append(f"Ad set: {', '.join(map(str, xf_adset))}")
if xf_obj:
    active.append(f"Objective: {', '.join(map(str, xf_obj))}")
if active:
    chip_col, btn_col = st.columns([5, 1])
    with chip_col:
        st.info("🔍 **Active chart filters** — " + " · ".join(active))
    with btn_col:
        if st.button("✖ Clear", use_container_width=True):
            st.session_state["xf_campaigns"] = []
            st.session_state["xf_adsets"] = []
            st.session_state["xf_objective"] = []
            st.rerun()

if fdf.empty:
    st.warning("No data matches the current filters.")
    st.stop()


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
def fmt_int(x):
    return f"{int(x):,}" if pd.notna(x) else "—"


def fmt_money(x):
    return f"€{x:,.2f}" if pd.notna(x) else "—"


def fmt_pct(x):
    return f"{x:.2f}%" if pd.notna(x) else "—"


def render_summary(title: str, takeaways: list, icon: str = "💡"):
    items = "".join(f"<li>{t}</li>" for t in takeaways if t)
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-card-title">{icon} {title}</div>
            <ul class="summary-card-list">{items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_top(df, group_col, value_col, agg="sum"):
    if df.empty or group_col not in df.columns or value_col not in df.columns:
        return None, None
    g = df.groupby(group_col, as_index=False)[value_col].agg(agg).dropna()
    if g.empty:
        return None, None
    row = g.sort_values(value_col, ascending=False).iloc[0]
    return row[group_col], row[value_col]


def col_sum(df, c):
    return df[c].sum() if c in df.columns else 0


def col_mean(df, c):
    if c not in df.columns:
        return None
    s = df[c].dropna()
    return s.mean() if not s.empty else None


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_over, tab1, tab2, tab3, tab_targets, tab4, tab_google, tab5 = st.tabs(
    ["🌐 Overview", "📈 Reach & Impressions", "💰 Cost & Efficiency",
     "❤️ Engagement", "🧭 Core Targets", "🎯 Funnel & Conversions",
     "🔍 Google Ads", "🗂️ Raw Data"]
)

# ---------------------------------------------------------------------------
# Tab Overview — top KPIs + headline charts
# ---------------------------------------------------------------------------
with tab_over:
    total_spend = col_sum(fdf, COL_SPEND)
    total_imp = col_sum(fdf, COL_IMPRESSIONS)
    total_reach = col_sum(fdf, COL_REACH)
    total_clicks = col_sum(fdf, COL_CLICKS)
    total_results = col_sum(fdf, COL_RESULT)
    total_purchases = col_sum(fdf, COL_PURCHASES)
    total_leads = col_sum(fdf, COL_LEADS)
    avg_ctr = col_mean(fdf, COL_CTR)
    avg_cpc = col_mean(fdf, COL_CPC_ALL)
    avg_cpm = col_mean(fdf, COL_CPM)
    avg_freq = (total_imp / total_reach) if total_reach else None
    avg_roas = col_mean(fdf, COL_ROAS)
    avg_cpl = (total_spend / total_leads) if total_leads else None
    avg_cost_per_purchase = (total_spend / total_purchases) if total_purchases else None

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Spend", fmt_money(total_spend))
    k2.metric("Impressions", fmt_int(total_imp))
    k3.metric("Reach", fmt_int(total_reach))
    _obj_labels = (
        sorted(fdf[COL_OBJECTIVE].dropna().unique().tolist())
        if COL_OBJECTIVE in fdf.columns else []
    )
    with k4:
        _sel_obj_result = st.session_state.get("overview_result_obj", "All")
        if _sel_obj_result == "All" or not _obj_labels:
            _result_count = total_results
        else:
            _result_count = col_sum(
                fdf[fdf[COL_OBJECTIVE] == _sel_obj_result], COL_RESULT
            )
        st.metric("Total results", fmt_int(_result_count))
        st.selectbox(
            "Filter by objective",
            options=["All"] + _obj_labels,
            key="overview_result_obj",
            label_visibility="collapsed",
        )
    k5.metric("Purchases", fmt_int(total_purchases))

    k6, k7, k8, k9, k10 = st.columns(5)
    k6.metric("Prospects", fmt_int(total_leads))
    k7.metric("Avg CPL (cost per prospect)", fmt_money(avg_cpl) if avg_cpl else "—")
    k8.metric("Avg cost per purchase", fmt_money(avg_cost_per_purchase) if avg_cost_per_purchase else "—")
    k9.metric("Avg Frequency", f"{avg_freq:.2f}" if avg_freq else "—")
    k10.metric("Avg ROAS", f"{avg_roas:.2f}" if avg_roas else "—")

    st.divider()

    # ── Budget tracker (from "(350€ ...)" captured in campaign names) ──────
    if COL_BUDGET in fdf.columns and fdf[COL_BUDGET].notna().any():
        # Budget is defined at the campaign level → take ONE budget per campaign
        camp_budget = (
            fdf.dropna(subset=[COL_BUDGET])
            .groupby(COL_CAMPAIGN, as_index=False)[COL_BUDGET].first()
        )
        camp_spend = (
            fdf.groupby(COL_CAMPAIGN, as_index=False)[COL_SPEND].sum()
            .rename(columns={COL_SPEND: "Spent"})
        )
        bud = camp_budget.merge(camp_spend, on=COL_CAMPAIGN, how="left").fillna({"Spent": 0})
        bud["Remaining"] = bud[COL_BUDGET] - bud["Spent"]
        bud["Used (%)"]  = (bud["Spent"] / bud[COL_BUDGET] * 100).where(bud[COL_BUDGET] > 0)

        total_budget    = bud[COL_BUDGET].sum()
        total_spent     = bud["Spent"].sum()
        total_remaining = total_budget - total_spent
        used_pct        = (total_spent / total_budget * 100) if total_budget else None

        st.markdown("### 💼 Budget tracker")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Total budget",     fmt_money(total_budget))
        b2.metric("Spent so far",     fmt_money(total_spent),
                  delta=f"{used_pct:.1f}% used" if used_pct is not None else None)
        b3.metric("💰 Budget remaining", fmt_money(total_remaining),
                  delta=f"{(total_remaining/total_budget*100):.1f}% left" if total_budget else None,
                  delta_color="inverse")
        b4.metric("Campaigns w/ budget", f"{len(bud)}")

        with st.expander("Per-campaign budget breakdown", expanded=False):
            show = bud.copy()
            show[COL_BUDGET]   = show[COL_BUDGET].map(fmt_money)
            show["Spent"]      = show["Spent"].map(fmt_money)
            show["Remaining"]  = show["Remaining"].map(fmt_money)
            show["Used (%)"]   = show["Used (%)"].map(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
            st.dataframe(show, use_container_width=True, hide_index=True)

        st.divider()

    # Spend by campaign
    by_camp = (
        fdf.groupby(COL_CAMPAIGN, as_index=False)
        .agg(Spend=(COL_SPEND, "sum"), Impressions=(COL_IMPRESSIONS, "sum"))
        .sort_values("Spend", ascending=False)
    )
    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig = px.bar(
            by_camp, x=COL_CAMPAIGN, y="Spend",
            color="Spend", color_continuous_scale="Purples",
            title="Estimated spend by campaign (€)",
            text_auto=".2f",
        )
        fig.update_layout(xaxis_tickangle=-30, height=440, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        if COL_OBJECTIVE in fdf.columns:
            by_obj = (
                fdf.dropna(subset=[COL_OBJECTIVE])
                .groupby(COL_OBJECTIVE, as_index=False)[COL_SPEND].sum()
            )
            if not by_obj.empty:
                fig = px.pie(
                    by_obj, names=COL_OBJECTIVE, values=COL_SPEND,
                    hole=0.55, title="Spend share by objective",
                )
                fig.update_layout(height=440)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No objective data in selection.")

    # ── Campaign goal breakdown ──────────────────────────────────────────
    if COL_GOAL in fdf.columns and fdf[COL_GOAL].notna().any():
        st.markdown("### 🎯 Performance by campaign goal")
        goal_df = (
            fdf.dropna(subset=[COL_GOAL])
            .groupby(COL_GOAL, as_index=False)
            .agg(
                Spend=(COL_SPEND, "sum"),
                Impressions=(COL_IMPRESSIONS, "sum"),
                Clicks=(COL_CLICKS, "sum"),
                Purchases=(COL_PURCHASES, "sum"),
                Leads=(COL_LEADS, "sum"),
                CTR=(COL_CTR, "mean"),
            )
            .sort_values("Spend", ascending=False)
        )
        g1, g2 = st.columns(2)
        with g1:
            fig = px.bar(
                goal_df, x=COL_GOAL, y="Spend",
                color=COL_GOAL, title="Spend by campaign goal (€)",
                text_auto=".2f",
            )
            fig.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            metric_options = ["Impressions", "Clicks", "Purchases", "Leads", "CTR"]
            pick = st.selectbox("Metric", metric_options, key="goal_metric")
            fig = px.bar(
                goal_df.sort_values(pick, ascending=False),
                x=COL_GOAL, y=pick, color=COL_GOAL,
                title=f"{pick} by campaign goal",
                text_auto=".2s" if pick != "CTR" else ".3f",
            )
            fig.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    top_camp, top_spend = safe_top(fdf, COL_CAMPAIGN, COL_SPEND)
    top_ad, top_ad_imp = safe_top(fdf, COL_AD, COL_IMPRESSIONS) if COL_AD in fdf.columns else (None, None)
    top_goal, top_goal_spend = (
        safe_top(fdf, COL_GOAL, COL_SPEND)
        if COL_GOAL in fdf.columns and fdf[COL_GOAL].notna().any()
        else (None, None)
    )
    render_summary(
        "Account snapshot",
        [
            f"Total spend: <b>{fmt_money(total_spend)}</b> across <b>{fdf[COL_CAMPAIGN].nunique()}</b> campaigns.",
            f"Delivered <b>{fmt_int(total_imp)}</b> impressions to <b>{fmt_int(total_reach)}</b> unique users (freq ≈ <b>{avg_freq:.2f}</b>)." if avg_freq else "",
            f"Top spender: <b>{top_camp}</b> ({fmt_money(top_spend)})." if top_camp else "",
            f"Top campaign goal by spend: <b>{top_goal}</b> ({fmt_money(top_goal_spend)})." if top_goal else "",
            f"Top ad by impressions: <b>{top_ad}</b> ({fmt_int(top_ad_imp)})." if top_ad else "",
            f"Conversions: <b>{fmt_int(total_purchases)}</b> purchases · <b>{fmt_int(total_leads)}</b> leads · avg ROAS <b>{avg_roas:.2f}</b>." if avg_roas else f"Conversions: <b>{fmt_int(total_purchases)}</b> purchases · <b>{fmt_int(total_leads)}</b> leads.",
        ],
        icon="🌐",
    )

# ---------------------------------------------------------------------------
# Tab 1 — Reach & Impressions
# ---------------------------------------------------------------------------
with tab1:
    st.caption("💡 **Tip:** click bars / slices to filter the whole dashboard.")

    # Per-campaign impressions vs reach
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
        barmode="group", title="Campaigns — Impressions vs Reach (click a bar to filter)",
        xaxis_tickangle=-30, height=480, legend_orientation="h",
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
        if COL_OBJECTIVE in fdf.columns:
            by_obj = (
                fdf.dropna(subset=[COL_OBJECTIVE])
                .groupby(COL_OBJECTIVE, as_index=False)[COL_IMPRESSIONS].sum()
            )
            if not by_obj.empty:
                fig = px.pie(
                    by_obj, names=COL_OBJECTIVE, values=COL_IMPRESSIONS,
                    title="Impressions share by objective (click a slice)",
                    hole=0.4,
                )
                sel = st.plotly_chart(
                    fig, use_container_width=True, key="chart_obj",
                    on_select="rerun", selection_mode=("points",),
                )
                picks = [p["label"] for p in (sel.selection.get("points") or [])]
                if picks and set(picks) != set(st.session_state["xf_objective"]):
                    st.session_state["xf_objective"] = picks
                    st.rerun()
            else:
                st.info("No objective data in selection.")
    with col_b:
        if COL_ADSET in fdf.columns:
            by_adset = (
                fdf.groupby(COL_ADSET, as_index=False)[[COL_IMPRESSIONS, COL_REACH]]
                .sum()
                .sort_values(COL_IMPRESSIONS, ascending=False)
                .head(15)
            )
            fig = px.bar(
                by_adset, x=COL_ADSET, y=[COL_IMPRESSIONS, COL_REACH],
                barmode="group",
                title="Impressions & Reach by ad set (click a bar)",
            )
            fig.update_layout(xaxis_tickangle=-30, height=460)
            sel = st.plotly_chart(
                fig, use_container_width=True, key="chart_adset",
                on_select="rerun", selection_mode=("points",),
            )
            picks = [p["x"] for p in (sel.selection.get("points") or [])]
            if picks and set(picks) != set(st.session_state["xf_adsets"]):
                st.session_state["xf_adsets"] = picks
                st.rerun()

    # Top ads by results
    if COL_AD in fdf.columns and COL_RESULT in fdf.columns:
        by_ad = (
            fdf.groupby(COL_AD, as_index=False)[[COL_RESULT, COL_REACH, COL_FREQ]]
            .agg({COL_RESULT: "sum", COL_REACH: "sum", COL_FREQ: "mean"})
            .sort_values(COL_RESULT, ascending=False)
            .head(15)
        )
        fig = px.bar(
            by_ad, x=COL_AD, y=COL_RESULT,
            color=COL_FREQ, color_continuous_scale="Plasma",
            title="Top ads by results (color = avg frequency)",
            text_auto=".2s",
        )
        fig.update_layout(xaxis_tickangle=-30, height=460)
        st.plotly_chart(fig, use_container_width=True)

    # Summary
    top_camp, top_imp = safe_top(fdf, COL_CAMPAIGN, COL_IMPRESSIONS)
    top_adset, top_adset_imp = (
        safe_top(fdf, COL_ADSET, COL_IMPRESSIONS) if COL_ADSET in fdf.columns else (None, None)
    )
    top_obj, _ = safe_top(fdf, COL_OBJECTIVE, COL_IMPRESSIONS) if COL_OBJECTIVE in fdf.columns else (None, None)
    total_imp = col_sum(fdf, COL_IMPRESSIONS)
    total_reach = col_sum(fdf, COL_REACH)
    freq = (total_imp / total_reach) if total_reach else None
    render_summary(
        "Reach & Impressions — key takeaways",
        [
            f"Total <b>{fmt_int(total_imp)}</b> impressions to <b>{fmt_int(total_reach)}</b> unique users.",
            f"Top campaign: <b>{top_camp}</b> with <b>{fmt_int(top_imp)}</b> impressions." if top_camp else "",
            f"Top ad set: <b>{top_adset}</b> ({fmt_int(top_adset_imp)} impressions)." if top_adset else "",
            f"Leading objective: <b>{top_obj}</b>." if top_obj else "",
            f"Average frequency ≈ <b>{freq:.2f}</b> impressions per user." if freq else "",
        ],
        icon="📈",
    )

# ---------------------------------------------------------------------------
# Tab 2 — Cost & Efficiency
# ---------------------------------------------------------------------------
with tab2:
    CHART_HEIGHT = 480

    cost_df = (
        fdf.groupby(COL_CAMPAIGN, as_index=False)
        .agg({COL_CTR: "mean", COL_CPC_ALL: "mean", COL_CPM: "mean",
              COL_SPEND: "sum"})
        .sort_values(COL_SPEND, ascending=False)
        .head(20)
    )

    fig = px.bar(
        cost_df, x=COL_CAMPAIGN, y=COL_SPEND,
        color=COL_SPEND, color_continuous_scale="Blues",
        title="Spend by campaign (€)", text_auto=".2f",
    )
    fig.update_layout(xaxis_tickangle=-30, height=CHART_HEIGHT, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        cost_df.melt(id_vars=COL_CAMPAIGN, value_vars=[COL_CTR, COL_CPC_ALL, COL_CPM]),
        x=COL_CAMPAIGN, y="value", color="variable", barmode="group",
        title="Avg CTR / CPC / CPM by campaign",
    )
    fig.update_layout(xaxis_tickangle=-30, height=CHART_HEIGHT)
    st.plotly_chart(fig, use_container_width=True)

    # Cost-per-action funnel chart
    _funnel_metrics = {
        "CPC":                   (COL_SPEND, COL_LINK_CLICKS),
        "Cost per landing view": (COL_SPEND, COL_LANDING_VIEWS),
        "Cost per view content": (COL_SPEND, COL_CONTENT_VIEWS),
        "Cost per add to cart":  (COL_SPEND, COL_ADD_CART),
        "Cost per checkout":     (COL_SPEND, COL_CHECKOUT),
        "Cost per purchase":     (COL_SPEND, COL_PURCHASES),
    }
    cpa_rows = []
    for label, (spend_col, vol_col) in _funnel_metrics.items():
        if vol_col in fdf.columns:
            for camp, grp in fdf.groupby(COL_CAMPAIGN):
                vol = col_sum(grp, vol_col)
                spend = col_sum(grp, spend_col)
                if vol and vol > 0:
                    cpa_rows.append({"Campaign": camp, "Metric": label, "Cost (€)": round(spend / vol, 2)})
    if cpa_rows:
        cpa_df = pd.DataFrame(cpa_rows)
        fig = px.bar(
            cpa_df, x="Campaign", y="Cost (€)", color="Metric",
            barmode="group",
            title="Cost per action — funnel breakdown by campaign (€)",
            text_auto=".2f",
        )
        fig.update_layout(xaxis_tickangle=-30, height=CHART_HEIGHT)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough funnel data to compute cost-per-action metrics.")

    # Treemap spend Campaign → Ad set → Ad
    tree_path = [c for c in [COL_CAMPAIGN, COL_ADSET, COL_AD] if c in fdf.columns]
    if len(tree_path) >= 2:
        tree_df = fdf.dropna(subset=tree_path + [COL_SPEND])
        tree_df = tree_df[tree_df[COL_SPEND] > 0]
        if not tree_df.empty:
            fig = px.treemap(
                tree_df, path=tree_path, values=COL_SPEND,
                color=COL_SPEND, color_continuous_scale="Purples",
                title="Spend breakdown — Campaign → Ad set → Ad",
            )
            fig.update_layout(height=520, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # Summary
    total_spend = col_sum(fdf, COL_SPEND)
    avg_ctr = col_mean(fdf, COL_CTR)
    avg_cpc = col_mean(fdf, COL_CPC_ALL)
    avg_cpm = col_mean(fdf, COL_CPM)
    top_spender, top_spend_val = safe_top(fdf, COL_CAMPAIGN, COL_SPEND)
    eff = (
        fdf.groupby(COL_CAMPAIGN, as_index=False)
        .agg(ctr=(COL_CTR, "mean"), cpc=(COL_CPC_ALL, "mean"),
             imp=(COL_IMPRESSIONS, "sum"))
    )
    eff_med = eff[eff["imp"] >= eff["imp"].median()] if not eff.empty else eff
    best_ctr_camp = eff_med.sort_values("ctr", ascending=False).iloc[0] if not eff_med.empty else None
    cheapest = eff_med[eff_med["cpc"] > 0].sort_values("cpc").iloc[0] if not eff_med[eff_med["cpc"] > 0].empty else None
    render_summary(
        "Cost & Efficiency — key takeaways",
        [
            f"Total spend: <b>{fmt_money(total_spend)}</b>.",
            f"Avg CTR <b>{fmt_pct(avg_ctr)}</b> · avg CPC <b>{fmt_money(avg_cpc)}</b> · avg CPM <b>{fmt_money(avg_cpm)}</b>.",
            f"Biggest spender: <b>{top_spender}</b> ({fmt_money(top_spend_val)})." if top_spender else "",
            f"Highest CTR (above-median reach): <b>{best_ctr_camp[COL_CAMPAIGN]}</b> at <b>{fmt_pct(best_ctr_camp['ctr'])}</b>." if best_ctr_camp is not None else "",
            f"Lowest CPC (above-median reach): <b>{cheapest[COL_CAMPAIGN]}</b> at <b>{fmt_money(cheapest['cpc'])}</b>." if cheapest is not None else "",
        ],
        icon="💰",
    )

# ---------------------------------------------------------------------------
# Tab 3 — Engagement
# ---------------------------------------------------------------------------
with tab3:
    eng_cols = [c for c in [COL_LIKES, COL_REACTIONS, COL_COMMENTS, COL_SHARES]
                if c in fdf.columns]

    if eng_cols:
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
            title="Engagement breakdown by campaign",
        )
        fig.update_layout(xaxis_tickangle=-30, height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No engagement metrics in current selection.")

    # Video performance
    video = fdf[[c for c in [COL_AD, COL_3SEC_VIEWS, COL_THRUPLAYS] if c in fdf.columns]]
    if COL_3SEC_VIEWS in video.columns or COL_THRUPLAYS in video.columns:
        video = video.dropna(subset=[c for c in [COL_3SEC_VIEWS, COL_THRUPLAYS] if c in video.columns], how="all")
        if not video.empty and COL_AD in video.columns:
            grp_cols = [c for c in [COL_3SEC_VIEWS, COL_THRUPLAYS] if c in video.columns]
            video = (
                video.groupby(COL_AD, as_index=False)[grp_cols].sum()
                .sort_values(grp_cols[0], ascending=False).head(15)
            )
            fig = px.bar(
                video, x=COL_AD, y=grp_cols, barmode="group",
                title="Video performance — top ads",
            )
            fig.update_layout(xaxis_tickangle=-30, height=500)
            st.plotly_chart(fig, use_container_width=True)

    # IG & messaging
    ig_cols = [c for c in [COL_IG_FOLLOWERS, COL_IG_VISITS, COL_MSG, COL_POST_ENG]
               if c in fdf.columns]
    if ig_cols:
        col_a, col_b = st.columns(2)
        ig_totals = pd.DataFrame({
            "Metric": [
                "IG followers gained" if c == COL_IG_FOLLOWERS else
                "IG profile visits" if c == COL_IG_VISITS else
                "Messages started" if c == COL_MSG else
                "Post interactions"
                for c in ig_cols
            ],
            "Total": [col_sum(fdf, c) for c in ig_cols],
        })
        with col_a:
            fig = px.bar(
                ig_totals[ig_totals["Total"] > 0],
                x="Metric", y="Total", color="Metric",
                title="Messaging & saves totals", text_auto=".2s",
            )
            fig.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            if COL_POST_ENG in fdf.columns and COL_AD in fdf.columns:
                top_eng_ads = (
                    fdf.groupby(COL_AD, as_index=False)[COL_POST_ENG].sum()
                    .sort_values(COL_POST_ENG, ascending=False).head(10)
                )
                fig = px.bar(
                    top_eng_ads, x=COL_AD, y=COL_POST_ENG,
                    title="Top 10 ads by post interactions",
                    color=COL_POST_ENG, color_continuous_scale="Magenta",
                )
                fig.update_layout(xaxis_tickangle=-30, height=420, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

    # Summary
    totals = {c: col_sum(fdf, c) for c in eng_cols}
    total_eng = sum(totals.values())
    eng_per_camp = (
        fdf.groupby(COL_CAMPAIGN, as_index=False)[eng_cols].sum()
        .assign(_t=lambda d: d[eng_cols].sum(axis=1))
        .sort_values("_t", ascending=False)
    ) if eng_cols else pd.DataFrame()
    top_eng = eng_per_camp.iloc[0] if not eng_per_camp.empty else None
    dominant = max(totals, key=totals.get) if totals else None
    v3 = col_sum(fdf, COL_3SEC_VIEWS)
    thru = col_sum(fdf, COL_THRUPLAYS)
    completion = (thru / v3 * 100) if v3 else None
    render_summary(
        "Engagement — key takeaways",
        [
            f"Total engagement actions: <b>{fmt_int(total_eng)}</b>.",
            f"Most engaging campaign: <b>{top_eng[COL_CAMPAIGN]}</b> ({fmt_int(top_eng['_t'])} interactions)." if top_eng is not None else "",
            f"Dominant interaction type: <b>{dominant}</b> ({fmt_int(totals[dominant])})." if dominant else "",
            f"Video: <b>{fmt_int(v3)}</b> 3-sec views · <b>{fmt_int(thru)}</b> ThruPlays" + (f" → completion ≈ <b>{completion:.1f}%</b>." if completion else "."),
        ],
        icon="❤️",
    )

# ---------------------------------------------------------------------------
# Tab — Core Targets (ad sets)
# ---------------------------------------------------------------------------
with tab_targets:
    st.markdown("### 🧭 Core targets — performance by ad set")
    st.caption(
        "Each ad set in `Nom de l'ensemble de publicités` is a targeting bundle. "
        "Compare what each one delivers in impressions, engagement and clicks."
    )

    if COL_ADSET not in fdf.columns or fdf[COL_ADSET].dropna().empty:
        st.info("No ad-set data available in the current selection.")
    else:
        agg_spec = {
            "Spend":        (COL_SPEND, "sum"),
            "Impressions":  (COL_IMPRESSIONS, "sum"),
            "Reach":        (COL_REACH, "sum"),
            "Clicks":       (COL_CLICKS, "sum"),
            "Link clicks":  (COL_LINK_CLICKS, "sum"),
            "Page likes":   (COL_LIKES, "sum"),
            "Reactions":    (COL_REACTIONS, "sum"),
            "Comments":     (COL_COMMENTS, "sum"),
            "Shares":       (COL_SHARES, "sum"),
            "Engagements":  (COL_POST_ENG, "sum"),
            "Avg CTR":      (COL_CTR, "mean"),
            "Avg CPC":      (COL_CPC_ALL, "mean"),
        }
        # Filter spec to only columns that actually exist (and avoid the size-fallback if undesired)
        safe_spec = {}
        for k, (src, fn) in agg_spec.items():
            if src in fdf.columns:
                safe_spec[k] = (src, fn)
        adset_df = (
            fdf.dropna(subset=[COL_ADSET])
            .groupby(COL_ADSET, as_index=False)
            .agg(**safe_spec)
            .sort_values("Spend", ascending=False)
        )

        # KPI strip
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Ad sets", f"{len(adset_df)}")
        k2.metric("Total impressions", fmt_int(adset_df["Impressions"].sum()) if "Impressions" in adset_df else "—")
        k3.metric("Total clicks", fmt_int(adset_df["Clicks"].sum()) if "Clicks" in adset_df else "—")
        k4.metric("Total spend", fmt_money(adset_df["Spend"].sum()) if "Spend" in adset_df else "—")

        st.divider()

        # Chart picker
        chart_metrics = [c for c in
                         ["Impressions", "Reach", "Clicks", "Link clicks",
                          "Page likes", "Reactions", "Comments", "Shares",
                          "Engagements", "Spend"]
                         if c in adset_df.columns]
        c1, c2 = st.columns([1, 3])
        with c1:
            pick = st.selectbox("Metric", chart_metrics, key="adset_metric")
            top_n = st.slider("Show top N ad sets", 3, max(3, len(adset_df)),
                              min(10, len(adset_df)), key="adset_topn")
        with c2:
            plot_df = adset_df.sort_values(pick, ascending=False).head(top_n)
            fig = px.bar(
                plot_df, x=COL_ADSET, y=pick,
                color=pick, color_continuous_scale="Purples",
                text_auto=".2s",
                title=f"{pick} by ad set (top {top_n})",
            )
            fig.update_layout(xaxis_tickangle=-30, height=420, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        # Multi-metric comparison
        st.markdown("#### Multi-metric comparison")
        comp_metrics = st.multiselect(
            "Pick metrics to compare side-by-side",
            chart_metrics,
            default=[m for m in ["Impressions", "Clicks", "Engagements"] if m in chart_metrics],
            key="adset_multi",
        )
        if comp_metrics:
            long_df = adset_df.melt(
                id_vars=[COL_ADSET], value_vars=comp_metrics,
                var_name="Metric", value_name="Value",
            )
            fig = px.bar(
                long_df, x=COL_ADSET, y="Value", color="Metric",
                barmode="group", title="Ad-set comparison",
            )
            fig.update_layout(xaxis_tickangle=-30, height=440)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Ad-set table")
        show = adset_df.copy()
        if "Spend" in show:    show["Spend"]   = show["Spend"].map(fmt_money)
        if "Avg CPC" in show:  show["Avg CPC"] = show["Avg CPC"].map(fmt_money)
        if "Avg CTR" in show:  show["Avg CTR"] = show["Avg CTR"].map(lambda v: f"{v:.3f}%" if pd.notna(v) else "—")
        for c in ["Impressions", "Reach", "Clicks", "Link clicks",
                  "Page likes", "Reactions", "Comments", "Shares", "Engagements"]:
            if c in show:
                show[c] = show[c].map(fmt_int)
        st.dataframe(show, use_container_width=True, hide_index=True)

        # Insight summary
        if not adset_df.empty:
            top_imp_row = adset_df.sort_values("Impressions", ascending=False).iloc[0] if "Impressions" in adset_df else None
            top_clk_row = adset_df.sort_values("Clicks", ascending=False).iloc[0] if "Clicks" in adset_df else None
            top_eng_row = adset_df.sort_values("Engagements", ascending=False).iloc[0] if "Engagements" in adset_df else None
            bullets = []
            if top_imp_row is not None:
                bullets.append(f"Biggest reach driver: <b>{top_imp_row[COL_ADSET]}</b> with <b>{fmt_int(top_imp_row['Impressions'])}</b> impressions.")
            if top_clk_row is not None:
                bullets.append(f"Most clicks: <b>{top_clk_row[COL_ADSET]}</b> with <b>{fmt_int(top_clk_row['Clicks'])}</b> clicks.")
            if top_eng_row is not None and top_eng_row["Engagements"] > 0:
                bullets.append(f"Most engaged audience: <b>{top_eng_row[COL_ADSET]}</b> with <b>{fmt_int(top_eng_row['Engagements'])}</b> engagements.")
            render_summary("Core targets insights", bullets, icon="🧭")

# ---------------------------------------------------------------------------
# Tab 4 — Funnel & Conversions
# ---------------------------------------------------------------------------
with tab4:
    funnel_map = {
        "Content views":   COL_CONTENT_VIEWS,
        "Landing views":   COL_LANDING_VIEWS,
        "Link clicks":     COL_LINK_CLICKS,
        "Add to cart":     COL_ADD_CART,
        "Checkout":        COL_CHECKOUT,
        "Payment info":    COL_PAY_INFO,
        "Purchases":       COL_PURCHASES,
    }
    funnel_vals = {
        label: col_sum(fdf, col)
        for label, col in funnel_map.items()
        if col in fdf.columns
    }
    funnel_vals = {k: v for k, v in funnel_vals.items() if pd.notna(v) and v > 0}

    col_a, col_b = st.columns([2, 1])
    with col_a:
        if funnel_vals:
            fig = go.Figure(go.Funnel(
                y=list(funnel_vals.keys()),
                x=list(funnel_vals.values()),
                textinfo="value+percent initial",
                marker={"color": "#a855f7"},
            ))
            fig.update_layout(title="Global conversion funnel", height=480)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No conversion events in current selection.")
    with col_b:
        st.subheader("Conversion KPIs")
        link_clicks = col_sum(fdf, COL_LINK_CLICKS)
        purchases = col_sum(fdf, COL_PURCHASES)
        conv_rate = (purchases / link_clicks * 100) if link_clicks else None
        st.metric("Total purchases", fmt_int(purchases))
        st.metric("Total leads", fmt_int(col_sum(fdf, COL_LEADS)))
        st.metric("Messages started", fmt_int(col_sum(fdf, COL_MSG)))
        st.metric("Conversion rate (purchases / link clicks)",
                  f"{conv_rate:.2f}%" if conv_rate else "—")
        roas = fdf[COL_ROAS].dropna() if COL_ROAS in fdf.columns else pd.Series(dtype=float)
        st.metric("Avg ROAS", f"{roas.mean():.2f}" if not roas.empty else "—")
        cart_value = col_sum(fdf, COL_CART_VALUE)
        st.metric("Cart conversion value", fmt_money(cart_value) if cart_value else "—")

    st.divider()

    # Per ad-set funnel summary table
    if COL_ADSET in fdf.columns:
        agg_cols = {label: (col, "sum") for label, col in funnel_map.items() if col in fdf.columns}
        if agg_cols:
            per_adset = (
                fdf.groupby(COL_ADSET, as_index=False)
                .agg(**{k: v for k, v in agg_cols.items()})
                .sort_values(list(agg_cols.keys())[0], ascending=False)
            )
            fig = px.bar(
                per_adset.melt(id_vars=COL_ADSET, var_name="Step", value_name="Count"),
                x=COL_ADSET, y="Count", color="Step", barmode="group",
                title="Funnel steps by ad set",
            )
            fig.update_layout(xaxis_tickangle=-30, height=480)
            st.plotly_chart(fig, use_container_width=True)

    # Cost-per-conversion summary
    cp_map = {
        "Cost / result":      COL_CPR,
        "Cost / content view": COL_CP_CONTENT,
        "Cost / landing view": COL_CP_LANDING,
        "Cost / cart add":    COL_CP_CART,
        "Cost / checkout":    COL_CP_CHECKOUT,
        "Cost / payment info": COL_CP_PAY,
        "Cost / purchase":    COL_CP_PURCHASE,
        "Cost / lead":        COL_CP_LEAD,
    }
    cp_rows = []
    for label, c in cp_map.items():
        if c in fdf.columns:
            v = fdf[c].dropna()
            if not v.empty:
                cp_rows.append({"Metric": label, "Avg cost (€)": v.mean()})
    if cp_rows:
        cp_df = pd.DataFrame(cp_rows).sort_values("Avg cost (€)")
        fig = px.bar(
            cp_df, x="Metric", y="Avg cost (€)",
            title="Average cost per funnel action (€)",
            text_auto=".2f", color="Avg cost (€)",
            color_continuous_scale="Reds",
        )
        fig.update_layout(xaxis_tickangle=-20, height=420, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Summary
    purchases = col_sum(fdf, COL_PURCHASES)
    link_clicks = col_sum(fdf, COL_LINK_CLICKS)
    conv_rate = (purchases / link_clicks * 100) if link_clicks else None
    leads_total = col_sum(fdf, COL_LEADS)
    roas_avg = col_mean(fdf, COL_ROAS)
    cp_purchase = col_mean(fdf, COL_CP_PURCHASE)
    cp_lead = col_mean(fdf, COL_CP_LEAD)
    render_summary(
        "Funnel & Conversions — key takeaways",
        [
            f"Funnel: <b>{fmt_int(link_clicks)}</b> link clicks → <b>{fmt_int(purchases)}</b> purchases" + (f" (conv. <b>{conv_rate:.2f}%</b>)." if conv_rate else "."),
            f"Total leads collected: <b>{fmt_int(leads_total)}</b>." if leads_total else "",
            f"Avg ROAS: <b>{roas_avg:.2f}</b>." if roas_avg else "",
            f"Avg cost per purchase: <b>{fmt_money(cp_purchase)}</b>." if cp_purchase else "",
            f"Avg cost per lead: <b>{fmt_money(cp_lead)}</b>." if cp_lead else "",
        ],
        icon="🎯",
    )

# ---------------------------------------------------------------------------
# Tab 5 — Raw Data
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Tab — Google Ads (separate CSV export)
# ---------------------------------------------------------------------------
with tab_google:
    st.markdown("### 🔍 Google Ads — campaign performance")
    st.caption("Source: `Biocyte Google Ads Performance.csv` (Google Ads export, UTF-16 / tab-separated).")

    _google_path = Path(__file__).parent / "Biocyte Google Ads Performance.csv"

    @st.cache_data(show_spinner=False)
    def _load_google_ads(path_str: str) -> pd.DataFrame:
        # Google Ads exports are UTF-16, tab-separated, with 2 header rows above the column names.
        encodings = ["utf-16", "utf-16-le", "utf-8-sig", "utf-8"]
        last_err: Exception | None = None
        for skip in (2, 0, 1):
            for enc in encodings:
                try:
                    g = pd.read_csv(path_str, encoding=enc, sep="\t", skiprows=skip)
                    if g.shape[1] >= 5:
                        return g
                except Exception as exc:  # noqa: BLE001
                    last_err = exc
        if last_err:
            raise last_err
        return pd.DataFrame()

    def _to_num(series: pd.Series) -> pd.Series:
        """Convert European-style numbers ('1 178', '23,55', '1,61%', '--') to floats."""
        def conv(v):
            if pd.isna(v):
                return None
            s = str(v).strip()
            if s in ("--", "", "nan", "NaN"):
                return None
            # Strip currency / percent / labels like "Page vue : 1,00"
            if ":" in s:
                s = s.split(":")[-1].strip()
            s = s.replace("%", "").replace("€", "").replace("\xa0", "").replace(" ", "")
            s = s.replace(",", ".")
            try:
                return float(s)
            except ValueError:
                return None
        return series.map(conv)

    if not _google_path.exists():
        st.warning(
            "`Biocyte Google Ads Performance.csv` not found in the dashboard folder. "
            "Drop the file in and refresh."
        )
    else:
        try:
            g_raw = _load_google_ads(str(_google_path))
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not read the Google Ads CSV: {exc}")
            g_raw = pd.DataFrame()

        if g_raw.empty:
            st.info("Google Ads file is empty.")
        else:
            # Keep only real campaign rows (drop the trailing 'Total : Campagnes' summary lines)
            G_CAMP = "Campagne"
            if "État de la campagne" in g_raw.columns:
                g = g_raw[~g_raw["État de la campagne"].fillna("").str.startswith("Total")].copy()
            else:
                g = g_raw.copy()
            g = g[g[G_CAMP].notna() & (g[G_CAMP].astype(str).str.strip() != "")]

            # Numeric conversion
            num_cols = [
                "Budget", "Coût", "Impr.", "Clics", "Interactions",
                "Résultats", "Page vue", "Ajout au panier", "Paiement initié",
                "Achetez", "Valeur des résultats", "Conversions", "Coût/conv.",
                "Conversions d'achat", "CPC moy.", "Coût moy.", "CTR",
            ]
            for c in num_cols:
                if c in g.columns:
                    g[c] = _to_num(g[c])

            # Derived: extract campaign goal + budget from the campaign name (same pattern as Meta)
            if G_CAMP in g.columns:
                g["Goal"] = g[G_CAMP].apply(_extract_goal)
                g["Budget (€)"] = g[G_CAMP].apply(_extract_budget)
                # Fall back to the "Budget" column if no budget is embedded in the name
                if "Budget" in g.columns:
                    g["Budget (€)"] = g["Budget (€)"].fillna(g["Budget"])

            # ── KPI row ─────────────────────────────────────────────────────
            total_cost   = g["Coût"].sum()         if "Coût" in g.columns else 0
            total_imp_g  = g["Impr."].sum()        if "Impr." in g.columns else 0
            total_clk_g  = g["Clics"].sum()        if "Clics" in g.columns else 0
            total_conv   = g["Conversions"].sum()  if "Conversions" in g.columns else 0
            total_purch  = g["Conversions d'achat"].sum() if "Conversions d'achat" in g.columns else 0
            avg_cpc_g    = g["CPC moy."].mean()    if "CPC moy." in g.columns else None
            avg_ctr_g    = (total_clk_g / total_imp_g * 100) if total_imp_g else None
            cost_per_conv = (total_cost / total_conv) if total_conv else None
            total_budget_g = g["Budget (€)"].sum() if "Budget (€)" in g.columns else 0
            remaining_g   = total_budget_g - total_cost if total_budget_g else None

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Total cost",        fmt_money(total_cost))
            k2.metric("Impressions",       fmt_int(total_imp_g))
            k3.metric("Clicks",            fmt_int(total_clk_g))
            k4.metric("Conversions",       fmt_int(total_conv))
            k5.metric("Purchase conv.",    fmt_int(total_purch))

            k6, k7, k8, k9, k10 = st.columns(5)
            k6.metric("Avg CTR",           f"{avg_ctr_g:.2f}%" if avg_ctr_g is not None else "—")
            k7.metric("Avg CPC",           fmt_money(avg_cpc_g) if avg_cpc_g is not None else "—")
            k8.metric("Cost / conv.",      fmt_money(cost_per_conv) if cost_per_conv is not None else "—")
            k9.metric("Total budget",      fmt_money(total_budget_g) if total_budget_g else "—")
            k10.metric("💰 Budget remaining", fmt_money(remaining_g) if remaining_g is not None else "—")

            st.divider()

            # ── Cost vs Conversions / Clicks bar chart per campaign ─────────
            if "Coût" in g.columns:
                chart_metrics = [c for c in
                                 ["Coût", "Impr.", "Clics", "Conversions",
                                  "Page vue", "Ajout au panier",
                                  "Paiement initié", "Achetez"]
                                 if c in g.columns]
                c1, c2 = st.columns([1, 3])
                with c1:
                    pick = st.selectbox("Metric", chart_metrics, key="google_metric")
                with c2:
                    plot_df = g[[G_CAMP, pick]].dropna()
                    if not plot_df.empty:
                        fig = px.bar(
                            plot_df.sort_values(pick, ascending=False),
                            x=G_CAMP, y=pick,
                            color=pick, color_continuous_scale="Blues",
                            text_auto=".2f",
                            title=f"{pick} by Google Ads campaign",
                        )
                        fig.update_layout(xaxis_tickangle=-30, height=420, coloraxis_showscale=False)
                        st.plotly_chart(fig, use_container_width=True)

            # ── Funnel for the (single) campaign ────────────────────────────
            funnel_map_g = [
                ("Impressions",     "Impr."),
                ("Clicks",          "Clics"),
                ("Page views",      "Page vue"),
                ("Add to cart",     "Ajout au panier"),
                ("Checkout",        "Paiement initié"),
                ("Purchases",       "Achetez"),
            ]
            funnel_rows = []
            for label, col in funnel_map_g:
                if col in g.columns:
                    val = g[col].sum()
                    if pd.notna(val):
                        funnel_rows.append({"Stage": label, "Count": val})
            if funnel_rows:
                f_df = pd.DataFrame(funnel_rows)
                fc1, fc2 = st.columns(2)
                with fc1:
                    fig = px.funnel(f_df, x="Count", y="Stage",
                                    title="Conversion funnel")
                    fig.update_layout(height=420)
                    st.plotly_chart(fig, use_container_width=True)
                with fc2:
                    # Per-campaign goal breakdown
                    if "Goal" in g.columns and g["Goal"].notna().any():
                        goal_df = (
                            g.dropna(subset=["Goal"])
                            .groupby("Goal", as_index=False)
                            .agg(Cost=("Coût", "sum"),
                                 Clicks=("Clics", "sum"),
                                 Conversions=("Conversions", "sum"))
                        )
                        fig = px.bar(
                            goal_df.melt(id_vars="Goal", value_vars=["Cost", "Clicks", "Conversions"]),
                            x="Goal", y="value", color="variable", barmode="group",
                            title="Performance by campaign goal",
                        )
                        fig.update_layout(height=420)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No goal information found in campaign names.")

            st.divider()

            # ── Campaign-level table ────────────────────────────────────────
            st.markdown("#### Campaign table")
            table_cols = [c for c in [
                G_CAMP, "État", "Type de campagne", "Goal", "Budget (€)",
                "Coût", "Impr.", "Clics", "CTR", "CPC moy.",
                "Conversions", "Coût/conv.", "Page vue", "Ajout au panier",
                "Paiement initié", "Achetez",
            ] if c in g.columns]
            show_g = g[table_cols].copy()
            for c in ["Budget (€)", "Coût", "CPC moy.", "Coût/conv."]:
                if c in show_g.columns:
                    show_g[c] = show_g[c].map(lambda v: fmt_money(v) if pd.notna(v) else "—")
            for c in ["Impr.", "Clics", "Conversions", "Page vue",
                      "Ajout au panier", "Paiement initié", "Achetez"]:
                if c in show_g.columns:
                    show_g[c] = show_g[c].map(lambda v: fmt_int(v) if pd.notna(v) else "—")
            if "CTR" in show_g.columns:
                show_g["CTR"] = show_g["CTR"].map(lambda v: f"{v:.2f}%" if pd.notna(v) else "—")
            st.dataframe(show_g, use_container_width=True, hide_index=True)

            with st.expander("Raw Google Ads export", expanded=False):
                st.dataframe(g_raw, use_container_width=True, height=320)

# ---------------------------------------------------------------------------
# Tab 5 — Raw Data
# ---------------------------------------------------------------------------
with tab5:
    st.dataframe(fdf, use_container_width=True, height=600)
    csv = fdf.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered data (CSV)", csv,
        file_name="biocyte_filtered.csv", mime="text/csv",
    )


