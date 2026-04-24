"""
Batam Meta Ads Dashboard
Interactive Streamlit dashboard for Facebook/Instagram campaign analytics.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Batam Meta Ads Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).parent / "mg_batam.xlsx"

# Column name constants (French headers from the source file)
COL_START = "Début des rapports"
COL_END = "Fin des rapports"
COL_CAMPAIGN = "Nom de la campagne"
COL_AGE = "Âge"
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

mask = (
    df[COL_CAMPAIGN].isin(sel_campaigns)
    & df[COL_AGE].isin(sel_ages)
    & df[COL_OBJECTIVE].isin(sel_obj)
)
fdf = df.loc[mask].copy()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("📊 Batam — Meta Ads Performance Dashboard")
st.caption(
    f"{len(fdf):,} rows · {fdf[COL_CAMPAIGN].nunique()} campaigns · "
    f"{fdf[COL_AGE].nunique()} age groups"
)

if fdf.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
def fmt_int(x):
    return f"{int(x):,}" if pd.notna(x) else "—"


def fmt_money(x):
    return f"${x:,.2f}" if pd.notna(x) else "—"


def fmt_pct(x):
    return f"{x:.2f}%" if pd.notna(x) else "—"


total_impr = fdf[COL_IMPRESSIONS].sum()
total_reach = fdf[COL_REACH].sum()
total_clicks = fdf[COL_CLICKS].sum()
total_spend = fdf["Spend (est.)"].sum()
avg_ctr = fdf[COL_CTR].mean()
avg_cpc = fdf[COL_CPC_ALL].mean()
avg_cpm = fdf[COL_CPM].mean()
total_purch = fdf[COL_PURCHASES].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Impressions", fmt_int(total_impr))
c2.metric("Reach", fmt_int(total_reach))
c3.metric("Clicks", fmt_int(total_clicks))
c4.metric("Spend (est.)", fmt_money(total_spend))

c5, c6, c7, c8 = st.columns(4)
c5.metric("Avg CTR", fmt_pct(avg_ctr))
c6.metric("Avg CPC", fmt_money(avg_cpc))
c7.metric("Avg CPM", fmt_money(avg_cpm))
c8.metric("Purchases", fmt_int(total_purch))

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Reach & Impressions", "💰 Cost & Efficiency", "❤️ Engagement",
     "🎯 Audience & Funnel", "🗂️ Raw Data"]
)

# ---- Tab 1: Reach & Impressions ----
with tab1:
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
        barmode="group", title="Top 20 Campaigns — Impressions vs Reach",
        xaxis_tickangle=-40, height=520, legend_orientation="h",
    )
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        by_obj = fdf.groupby(COL_OBJECTIVE, as_index=False)[COL_IMPRESSIONS].sum()
        fig = px.pie(by_obj, names=COL_OBJECTIVE, values=COL_IMPRESSIONS,
                     title="Impressions share by objective", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        by_age = fdf.groupby(COL_AGE, as_index=False)[[COL_IMPRESSIONS, COL_REACH]].sum()
        fig = px.bar(by_age, x=COL_AGE, y=[COL_IMPRESSIONS, COL_REACH],
                     barmode="group", title="Impressions & Reach by age group")
        st.plotly_chart(fig, use_container_width=True)

# ---- Tab 2: Cost & Efficiency ----
with tab2:
    cost_df = (
        fdf.groupby(COL_CAMPAIGN, as_index=False)
        .agg({COL_CTR: "mean", COL_CPC_ALL: "mean", COL_CPM: "mean",
              "Spend (est.)": "sum"})
        .sort_values("Spend (est.)", ascending=False)
        .head(20)
    )
    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.bar(cost_df, x=COL_CAMPAIGN, y="Spend (est.)",
                     title="Estimated spend by campaign (top 20)",
                     color="Spend (est.)", color_continuous_scale="Blues")
        fig.update_layout(xaxis_tickangle=-40, height=480)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig = px.scatter(
            fdf, x=COL_CPC_ALL, y=COL_CTR, size=COL_IMPRESSIONS,
            color=COL_OBJECTIVE, hover_name=COL_CAMPAIGN,
            title="CTR vs CPC (bubble = Impressions)",
        )
        fig.update_layout(height=480)
        st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(cost_df.melt(id_vars=COL_CAMPAIGN,
                              value_vars=[COL_CTR, COL_CPC_ALL, COL_CPM]),
                 x=COL_CAMPAIGN, y="value", color="variable", barmode="group",
                 title="CTR / CPC / CPM by campaign (top 20 by spend)")
    fig.update_layout(xaxis_tickangle=-40, height=500)
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

    col_a, col_b = st.columns(2)
    with col_a:
        video = fdf[[COL_CAMPAIGN, COL_3SEC_VIEWS, COL_THRUPLAYS]].dropna(
            subset=[COL_3SEC_VIEWS, COL_THRUPLAYS], how="all"
        )
        if not video.empty:
            video = video.groupby(COL_CAMPAIGN, as_index=False).sum().sort_values(
                COL_3SEC_VIEWS, ascending=False
            ).head(15)
            fig = px.bar(video, x=COL_CAMPAIGN, y=[COL_3SEC_VIEWS, COL_THRUPLAYS],
                         barmode="group", title="Video performance")
            fig.update_layout(xaxis_tickangle=-40, height=420)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No video metrics in current selection.")
    with col_b:
        ig = fdf.groupby(COL_CAMPAIGN, as_index=False)[COL_IG_FOLLOWERS].sum()
        ig = ig[ig[COL_IG_FOLLOWERS] > 0].sort_values(COL_IG_FOLLOWERS, ascending=False).head(15)
        if not ig.empty:
            fig = px.bar(ig, x=COL_CAMPAIGN, y=COL_IG_FOLLOWERS,
                         title="Instagram followers gained", color=COL_IG_FOLLOWERS,
                         color_continuous_scale="Magenta")
            fig.update_layout(xaxis_tickangle=-40, height=420)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Instagram followers data in current selection.")

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

# ---- Tab 5: Raw Data ----
with tab5:
    st.dataframe(fdf, use_container_width=True, height=600)
    csv = fdf.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered data (CSV)", csv,
                       file_name="batam_filtered.csv", mime="text/csv")
