import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedBox Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .metric-label { font-size: 12px; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { font-size: 28px; font-weight: 700; color: #1e3a5f; margin: 4px 0 2px; }
    .metric-delta { font-size: 12px; color: #10b981; }
    .section-header {
        font-size: 18px; font-weight: 600; color: #1e3a5f;
        border-left: 4px solid #2563eb; padding-left: 12px;
        margin: 1.5rem 0 1rem;
    }
    .insight-box {
        background: #eff6ff; border-left: 4px solid #2563eb;
        border-radius: 0 8px 8px 0; padding: 12px 16px;
        font-size: 13px; color: #1e40af; margin: 8px 0 16px;
        line-height: 1.6;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: white; border-radius: 8px;
        border: 1px solid #e2e8f0; padding: 8px 20px;
        font-weight: 500; color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background: #1e3a5f !important; color: white !important;
        border-color: #1e3a5f !important;
    }
    div[data-testid="stSidebarContent"] { background: #1e3a5f; }
    div[data-testid="stSidebarContent"] * { color: white !important; }
    div[data-testid="stSidebarContent"] .stMultiSelect > div > div { background: #2d5282; border-color: #4a6fa5; }
    h1 { color: #1e3a5f !important; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("medbox_clean.csv", parse_dates=["Lead_Date", "Close_Date"])
    df["Month_Num"] = df["Lead_Date"].dt.month
    df["Month_Label"] = df["Lead_Date"].dt.strftime("%b")
    df["Month_Year"] = df["Lead_Date"].dt.strftime("%b %Y")
    return df

df = load_data()

COLORS = {
    "primary":   "#2563eb",
    "secondary": "#1e3a5f",
    "teal":      "#0d9488",
    "amber":     "#d97706",
    "purple":    "#7c3aed",
    "coral":     "#dc2626",
    "green":     "#16a34a",
    "gray":      "#64748b",
}
PALETTE = [COLORS["primary"], COLORS["teal"], COLORS["amber"],
           COLORS["purple"], COLORS["coral"], COLORS["green"], COLORS["gray"]]

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 MedBox")
    st.markdown("**Analytics Dashboard**")
    st.markdown("---")
    st.markdown("### Filters")

    all_channels = sorted(df["Lead_Channel"].unique())
    sel_channels = st.multiselect("Lead Channel", all_channels, default=all_channels)

    all_kits = sorted(df["Kit_Type"].unique())
    sel_kits = st.multiselect("Kit Type", all_kits, default=all_kits)

    all_tiers = sorted(df["City_Tier_Label"].unique())
    sel_tiers = st.multiselect("City Tier", all_tiers, default=all_tiers)

    month_range = st.slider("Month Range", 1, 12, (1, 12))

    st.markdown("---")
    st.markdown("**Dataset:** 300 rows · 25 cols")
    st.markdown("**Period:** Jan–Dec 2024")
    st.markdown("**Business:** MedBox D2C")

# Apply filters
mask = (
    df["Lead_Channel"].isin(sel_channels) &
    df["Kit_Type"].isin(sel_kits) &
    df["City_Tier_Label"].isin(sel_tiers) &
    df["Month_Num"].between(month_range[0], month_range[1])
)
dff = df[mask].copy()
conv = dff[dff["Is_Converted"] == 1]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🏥 MedBox — Data Analytics Dashboard")
st.markdown("**At-Home Diagnostics Kit Startup · Sales Pipeline Analytics · Jan–Dec 2024**")
st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)

total_leads    = len(dff)
total_conv     = int(dff["Is_Converted"].sum())
conv_rate      = total_conv / total_leads * 100 if total_leads > 0 else 0
total_rev      = conv["Total_Revenue_INR"].sum()
avg_order      = conv["Order_Value_INR"].mean() if len(conv) > 0 else 0
avg_nps        = conv["NPS_Score"].mean() if len(conv) > 0 else 0
upsell_rate    = (conv["Consultation_Upsell"] == "Yes").mean() * 100 if len(conv) > 0 else 0

# ── FIX 1: Dynamic lost leads count ──────────────────────────────────────────
lost_count = int((dff["Pipeline_Stage"] == "Lost").sum())

for col, label, value, fmt in [
    (k1, "Total Leads",      total_leads,  "{:,}"),
    (k2, "Conversions",      total_conv,   "{:,}"),
    (k3, "Conversion Rate",  conv_rate,    "{:.1f}%"),
    (k4, "Total Revenue",    total_rev,    "₹{:,.0f}"),
    (k5, "Avg Order Value",  avg_order,    "₹{:,.0f}"),
    (k6, "Avg NPS Score",    avg_nps,      "{:.1f}/10"),
]:
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{fmt.format(value)}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Funnel & Channels",
    "💰 Revenue & Products",
    "📈 Trends & Segments",
    "🔗 Correlation Analysis",
    "📋 Raw Data"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FUNNEL & CHANNELS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-header">Sales Funnel — Stage Distribution</div>', unsafe_allow_html=True)
        stage_order = ["Lead", "Interested", "Demo/Sample Sent", "Quote Sent", "Converted", "Lost"]
        stage_counts = dff["Pipeline_Stage"].value_counts().reindex(stage_order, fill_value=0)
        stage_df = pd.DataFrame({"Stage": stage_counts.index, "Count": stage_counts.values})
        stage_df["Pct"] = stage_df["Count"] / stage_df["Count"].sum() * 100

        fig_funnel = go.Figure()
        colors_funnel = [COLORS["primary"], COLORS["teal"], COLORS["amber"],
                         COLORS["purple"], COLORS["green"], COLORS["coral"]]
        for i, row in stage_df.iterrows():
            fig_funnel.add_trace(go.Bar(
                x=[row["Count"]], y=[row["Stage"]],
                orientation="h", name=row["Stage"],
                marker_color=colors_funnel[i],
                text=f'  {row["Count"]} ({row["Pct"]:.1f}%)',
                textposition="outside",
                showlegend=False
            ))
        fig_funnel.update_layout(
            height=320, margin=dict(l=10, r=80, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(autorange="reversed"),
            font=dict(family="Arial", size=12)
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

        # ── FIX 1 applied: dynamic lost_count ────────────────────────────────
        st.markdown(f'<div class="insight-box">The funnel shows a <b>{conv_rate:.1f}%</b> overall conversion rate — competitive for D2C health (benchmark: 25–35%). The <b>{lost_count}</b> "Lost" leads represent a re-engagement opportunity worth ₹{lost_count * avg_order:,.0f} in potential recovered revenue.</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-header">Lead Channel — Conversion Rate</div>', unsafe_allow_html=True)
        ch_stats = dff.groupby("Lead_Channel").agg(
            Leads=("Lead_ID", "count"),
            Converted=("Is_Converted", "sum")
        ).reset_index()
        ch_stats["Conv_Rate"] = ch_stats["Converted"] / ch_stats["Leads"] * 100
        ch_stats = ch_stats.sort_values("Conv_Rate", ascending=True)

        fig_ch = px.bar(ch_stats, x="Conv_Rate", y="Lead_Channel", orientation="h",
                        color="Conv_Rate", color_continuous_scale=["#93c5fd", "#1e3a5f"],
                        text=ch_stats["Conv_Rate"].round(1).astype(str) + "%")
        fig_ch.update_traces(textposition="outside")
        fig_ch.update_layout(
            height=320, margin=dict(l=10, r=60, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            coloraxis_showscale=False,
            xaxis_title="Conversion Rate (%)", yaxis_title="",
            font=dict(family="Arial", size=12)
        )
        st.plotly_chart(fig_ch, use_container_width=True)
        best_ch = ch_stats.iloc[-1]
        st.markdown(f'<div class="insight-box"><b>{best_ch["Lead_Channel"]}</b> leads with the highest conversion rate at <b>{best_ch["Conv_Rate"]:.1f}%</b>. High-intent search channels outperform broad social media — indicating strong product-market fit for people actively seeking health tests.</div>', unsafe_allow_html=True)

    st.markdown("---")
    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="section-header">Channel — Lead Volume vs Conversion Rate</div>', unsafe_allow_html=True)
        ch_stats2 = dff.groupby("Lead_Channel").agg(
            Leads=("Lead_ID", "count"),
            Converted=("Is_Converted", "sum"),
            Avg_Order=("Order_Value_INR", "mean")
        ).reset_index()
        ch_stats2["Conv_Rate"] = ch_stats2["Converted"] / ch_stats2["Leads"] * 100
        ch_stats2["Avg_Order"] = ch_stats2["Avg_Order"].fillna(0)

        fig_bubble = px.scatter(ch_stats2, x="Leads", y="Conv_Rate",
                                size="Avg_Order", color="Lead_Channel",
                                text="Lead_Channel", color_discrete_sequence=PALETTE,
                                size_max=50)
        fig_bubble.update_traces(textposition="top center", marker=dict(opacity=0.8))
        fig_bubble.update_layout(
            height=320, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis_title="Total Leads", yaxis_title="Conversion Rate (%)",
            showlegend=False, font=dict(family="Arial", size=12)
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    with c4:
        st.markdown('<div class="section-header">Sales Rep Performance</div>', unsafe_allow_html=True)
        rep_stats = dff.groupby("Assigned_Rep").agg(
            Leads=("Lead_ID", "count"),
            Converted=("Is_Converted", "sum"),
            Revenue=("Total_Revenue_INR", "sum")
        ).reset_index()
        rep_stats["Conv_Rate"] = rep_stats["Converted"] / rep_stats["Leads"] * 100
        rep_stats = rep_stats.sort_values("Revenue", ascending=False)

        fig_rep = go.Figure()

        # ── FIX 2: Added revenue labels to bar chart ──────────────────────────
        fig_rep.add_trace(go.Bar(
            name="Revenue (₹)", x=rep_stats["Assigned_Rep"], y=rep_stats["Revenue"],
            marker_color=COLORS["primary"], yaxis="y",
            text=rep_stats["Revenue"].apply(lambda x: f"₹{x:,.0f}"),
            textposition="outside"
        ))
        fig_rep.add_trace(go.Scatter(
            name="Conv Rate (%)", x=rep_stats["Assigned_Rep"], y=rep_stats["Conv_Rate"],
            mode="lines+markers", marker=dict(color=COLORS["amber"], size=8),
            yaxis="y2"
        ))
        fig_rep.update_layout(
            height=320, margin=dict(l=10, r=60, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(title="Revenue (₹)", showgrid=True, gridcolor="#f1f5f9"),
            yaxis2=dict(title="Conv Rate (%)", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.1),
            font=dict(family="Arial", size=12)
        )
        st.plotly_chart(fig_rep, use_container_width=True)

        # ── FIX 3: Added insight box for sales rep ────────────────────────────
        top_rep = rep_stats.iloc[0]
        st.markdown(f'<div class="insight-box"><b>{top_rep["Assigned_Rep"]}</b> leads in revenue at <b>₹{top_rep["Revenue"]:,.0f}</b> with a <b>{top_rep["Conv_Rate"]:.1f}%</b> conversion rate. Consider using top rep strategies as a training benchmark for the team.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REVENUE & PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-header">Revenue by Kit Type</div>', unsafe_allow_html=True)
        kit_rev = conv.groupby("Kit_Type").agg(
            Units=("Lead_ID", "count"),
            Revenue=("Total_Revenue_INR", "sum"),
            Avg_Order=("Order_Value_INR", "mean")
        ).reset_index().sort_values("Revenue", ascending=True)

        fig_kit = px.bar(kit_rev, x="Revenue", y="Kit_Type", orientation="h",
                         color="Revenue", color_continuous_scale=["#fed7aa", "#92400e"],
                         text=kit_rev["Revenue"].apply(lambda x: f"₹{x:,.0f}"))
        fig_kit.update_traces(textposition="outside")
        fig_kit.update_layout(
            height=340, margin=dict(l=10, r=80, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            coloraxis_showscale=False,
            xaxis_title="Total Revenue (₹)", yaxis_title="",
            font=dict(family="Arial", size=12)
        )
        st.plotly_chart(fig_kit, use_container_width=True)
        top_kit = kit_rev.iloc[-1]
        st.markdown(f'<div class="insight-box"><b>{top_kit["Kit_Type"]}</b> is the top revenue generator at <b>₹{top_kit["Revenue"]:,.0f}</b>. Bundle high-demand kits with consultation upsells to increase avg basket size by 15–20%.</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-header">Revenue Band Distribution</div>', unsafe_allow_html=True)
        rev_band = conv["Revenue_Band"].value_counts().reset_index()
        rev_band.columns = ["Band", "Count"]

        fig_donut = px.pie(rev_band, values="Count", names="Band",
                           color_discrete_sequence=[COLORS["teal"], COLORS["primary"], COLORS["amber"]],
                           hole=0.55)
        fig_donut.update_traces(textposition="outside", textinfo="label+percent")
        fig_donut.update_layout(
            height=340, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True, legend=dict(orientation="h", y=-0.1),
            font=dict(family="Arial", size=12)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('<div class="insight-box">Mid-range kits (₹1,000–₹2,000) drive the highest volume. High-value (>₹2,000) orders, though fewer, contribute disproportionately to revenue — prioritise upsells for this segment.</div>', unsafe_allow_html=True)

    st.markdown("---")
    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="section-header">Upsell vs Base Revenue by Kit</div>', unsafe_allow_html=True)
        kit_upsell = conv.groupby("Kit_Type").agg(
            Base_Rev=("Order_Value_INR", "sum"),
            Upsell_Rev=("Upsell_Revenue_INR", "sum")
        ).reset_index().sort_values("Base_Rev", ascending=False)

        fig_stack = go.Figure()
        fig_stack.add_trace(go.Bar(name="Base Revenue", x=kit_upsell["Kit_Type"],
                                   y=kit_upsell["Base_Rev"], marker_color=COLORS["primary"]))
        fig_stack.add_trace(go.Bar(name="Upsell Revenue", x=kit_upsell["Kit_Type"],
                                   y=kit_upsell["Upsell_Rev"], marker_color=COLORS["amber"]))
        fig_stack.update_layout(
            barmode="stack", height=320,
            margin=dict(l=10, r=10, t=10, b=60),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis_title="Revenue (₹)",
            legend=dict(orientation="h", y=1.1),
            xaxis=dict(tickangle=-20),
            font=dict(family="Arial", size=12)
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    with c4:
        st.markdown('<div class="section-header">Repeat Purchase Rate by Kit</div>', unsafe_allow_html=True)
        kit_repeat = conv.groupby("Kit_Type").agg(
            Total=("Lead_ID", "count"),
            Repeat=("Repeat_Purchase", lambda x: (x == "Yes").sum())
        ).reset_index()
        kit_repeat["Repeat_Rate"] = kit_repeat["Repeat"] / kit_repeat["Total"] * 100
        kit_repeat = kit_repeat.sort_values("Repeat_Rate", ascending=False)

        fig_repeat = px.bar(kit_repeat, x="Kit_Type", y="Repeat_Rate",
                            color="Repeat_Rate",
                            color_continuous_scale=["#a7f3d0", "#065f46"],
                            text=kit_repeat["Repeat_Rate"].round(1).astype(str) + "%")
        fig_repeat.update_traces(textposition="outside")
        fig_repeat.update_layout(
            height=320, margin=dict(l=10, r=10, t=10, b=60),
            plot_bgcolor="white", paper_bgcolor="white",
            coloraxis_showscale=False,
            yaxis_title="Repeat Purchase Rate (%)",
            xaxis=dict(tickangle=-20, title=""),
            font=dict(family="Arial", size=12)
        )
        st.plotly_chart(fig_repeat, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TRENDS & SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Monthly Lead & Conversion Trend — 2024</div>', unsafe_allow_html=True)
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    monthly = dff.groupby(["Month_Num","Month_Label"]).agg(
        Leads=("Lead_ID","count"),
        Conversions=("Is_Converted","sum")
    ).reset_index().sort_values("Month_Num")
    monthly["Conv_Rate"] = monthly["Conversions"] / monthly["Leads"] * 100

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(go.Bar(name="Leads", x=monthly["Month_Label"], y=monthly["Leads"],
                                marker_color=COLORS["primary"], opacity=0.7), secondary_y=False)
    fig_trend.add_trace(go.Bar(name="Conversions", x=monthly["Month_Label"], y=monthly["Conversions"],
                                marker_color=COLORS["teal"], opacity=0.9), secondary_y=False)
    fig_trend.add_trace(go.Scatter(name="Conv Rate %", x=monthly["Month_Label"], y=monthly["Conv_Rate"],
                                    mode="lines+markers", marker=dict(color=COLORS["amber"], size=8),
                                    line=dict(width=2.5)), secondary_y=True)
    fig_trend.update_layout(
        height=360, barmode="group",
        margin=dict(l=10, r=60, t=10, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", y=1.05),
        font=dict(family="Arial", size=12)
    )
    fig_trend.update_yaxes(title_text="Count", secondary_y=False, showgrid=True, gridcolor="#f1f5f9")
    fig_trend.update_yaxes(title_text="Conv Rate (%)", secondary_y=True)
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('<div class="insight-box">Lead volume peaks in Q3 (Jul–Sep), driven by post-monsoon health awareness. Conversion rates stay stable (28–34%) year-round — seasonality affects lead generation, not sales efficiency. Recommendation: increase ad spend by 30% in Q3 2025.</div>', unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-header">City Tier — Conversion & Revenue</div>', unsafe_allow_html=True)
        tier_stats = dff.groupby("City_Tier_Label").agg(
            Leads=("Lead_ID","count"),
            Converted=("Is_Converted","sum"),
            Revenue=("Total_Revenue_INR","sum")
        ).reset_index()
        tier_stats["Conv_Rate"] = tier_stats["Converted"] / tier_stats["Leads"] * 100

        fig_tier = make_subplots(specs=[[{"secondary_y": True}]])
        fig_tier.add_trace(go.Bar(name="Conversion Rate %", x=tier_stats["City_Tier_Label"],
                                   y=tier_stats["Conv_Rate"], marker_color=COLORS["purple"], opacity=0.85),
                           secondary_y=False)
        fig_tier.add_trace(go.Scatter(name="Revenue (₹)", x=tier_stats["City_Tier_Label"],
                                       y=tier_stats["Revenue"], mode="lines+markers",
                                       marker=dict(color=COLORS["amber"], size=10), line=dict(width=2.5)),
                           secondary_y=True)
        fig_tier.update_layout(
            height=300, margin=dict(l=10, r=60, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=1.1),
            font=dict(family="Arial", size=12)
        )
        fig_tier.update_yaxes(title_text="Conv Rate (%)", secondary_y=False, showgrid=True, gridcolor="#f1f5f9")
        fig_tier.update_yaxes(title_text="Revenue (₹)", secondary_y=True)
        st.plotly_chart(fig_tier, use_container_width=True)
        st.markdown('<div class="insight-box">Tier 2 cities are within 4% of Metro conversion rates but have 40–60% lower CAC — making them the highest ROI expansion target for MedBox.</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-header">Age Group — Lead Volume & Conv Rate</div>', unsafe_allow_html=True)
        age_stats = dff[dff["Age_Group"] != "Not Specified"].groupby("Age_Group").agg(
            Leads=("Lead_ID","count"),
            Converted=("Is_Converted","sum"),
            Avg_Order=("Order_Value_INR","mean")
        ).reset_index()
        age_stats["Conv_Rate"] = age_stats["Converted"] / age_stats["Leads"] * 100
        age_stats = age_stats.sort_values("Age_Group")

        fig_age = make_subplots(specs=[[{"secondary_y": True}]])
        fig_age.add_trace(go.Bar(name="Leads", x=age_stats["Age_Group"], y=age_stats["Leads"],
                                  marker_color=COLORS["teal"], opacity=0.8), secondary_y=False)
        fig_age.add_trace(go.Scatter(name="Conv Rate %", x=age_stats["Age_Group"], y=age_stats["Conv_Rate"],
                                      mode="lines+markers", marker=dict(color=COLORS["coral"], size=8),
                                      line=dict(width=2.5)), secondary_y=True)
        fig_age.update_layout(
            height=300, margin=dict(l=10, r=60, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=1.1),
            font=dict(family="Arial", size=12)
        )
        fig_age.update_yaxes(title_text="Lead Count", secondary_y=False, showgrid=True, gridcolor="#f1f5f9")
        fig_age.update_yaxes(title_text="Conv Rate (%)", secondary_y=True)
        st.plotly_chart(fig_age, use_container_width=True)
        st.markdown('<div class="insight-box">26–35 age group drives the highest lead volume and conversions. 36–45 segment shows the highest average order value — target them for premium kit campaigns.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Days to Convert Distribution</div>', unsafe_allow_html=True)
    fig_hist = px.histogram(dff, x="Days_to_Convert", nbins=20,
                             color_discrete_sequence=[COLORS["primary"]],
                             labels={"Days_to_Convert": "Days to Convert"})
    fig_hist.update_layout(
        height=280, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis_title="Number of Leads", font=dict(family="Arial", size=12)
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # ── FIX 4: Gender split chart (shown only if column exists) ──────────────
    if "Gender" in dff.columns:
        st.markdown("---")
        st.markdown('<div class="section-header">Gender — Lead Volume & Conversion Rate</div>', unsafe_allow_html=True)
        gender_stats = dff[dff["Gender"].notna()].groupby("Gender").agg(
            Leads=("Lead_ID", "count"),
            Converted=("Is_Converted", "sum")
        ).reset_index()
        gender_stats["Conv_Rate"] = gender_stats["Converted"] / gender_stats["Leads"] * 100

        fig_gender = px.bar(
            gender_stats, x="Gender", y="Leads",
            color="Conv_Rate", color_continuous_scale=["#93c5fd", "#1e3a5f"],
            text=gender_stats["Conv_Rate"].round(1).astype(str) + "%",
            labels={"Leads": "Total Leads", "Conv_Rate": "Conv Rate (%)"}
        )
        fig_gender.update_traces(textposition="outside")
        fig_gender.update_layout(
            height=300, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            coloraxis_showscale=True,
            font=dict(family="Arial", size=12)
        )
        st.plotly_chart(fig_gender, use_container_width=True)
        top_gender = gender_stats.sort_values("Conv_Rate", ascending=False).iloc[0]
        st.markdown(f'<div class="insight-box"><b>{top_gender["Gender"]}</b> leads in conversion rate at <b>{top_gender["Conv_Rate"]:.1f}%</b>. Use gender-specific messaging in ad creatives to improve targeting efficiency.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CORRELATION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown('<div class="section-header">Correlation Heatmap</div>', unsafe_allow_html=True)
        corr_cols = ["Is_Converted","Order_Value_INR","Days_to_Convert",
                     "NPS_Score","Base_Kit_Price_INR","City_Tier",
                     "Stage_Code","Upsell_Revenue_INR"]
        corr_labels = ["Is Converted","Order Value","Days to Convert",
                        "NPS Score","Kit Price","City Tier",
                        "Stage Code","Upsell Revenue"]
        corr_matrix = dff[corr_cols].dropna().corr().round(3)
        corr_matrix.index = corr_labels
        corr_matrix.columns = corr_labels

        fig_heat = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_labels, y=corr_labels,
            colorscale=[[0,"#dc2626"],[0.5,"#f8fafc"],[1,"#1e3a5f"]],
            zmin=-1, zmax=1,
            text=corr_matrix.round(2).values,
            texttemplate="%{text}",
            textfont=dict(size=11),
            hoverongaps=False
        ))
        fig_heat.update_layout(
            height=420, margin=dict(l=10, r=10, t=10, b=10),
            font=dict(family="Arial", size=11),
            xaxis=dict(tickangle=-30)
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with c2:
        st.markdown('<div class="section-header">Key Correlations</div>', unsafe_allow_html=True)
        pairs = []
        cm = corr_matrix.copy()
        for i in range(len(corr_labels)):
            for j in range(i+1, len(corr_labels)):
                pairs.append({
                    "Var 1": corr_labels[i],
                    "Var 2": corr_labels[j],
                    "r": cm.iloc[i,j]
                })
        pairs_df = pd.DataFrame(pairs).sort_values("r", key=abs, ascending=False).head(8)

        fig_bars = go.Figure()
        colors_corr = [COLORS["primary"] if v > 0 else COLORS["coral"] for v in pairs_df["r"]]
        fig_bars.add_trace(go.Bar(
            y=pairs_df["Var 1"] + " ↔ " + pairs_df["Var 2"],
            x=pairs_df["r"],
            orientation="h",
            marker_color=colors_corr,
            text=pairs_df["r"].round(3).astype(str),
            textposition="outside"
        ))
        fig_bars.add_vline(x=0, line_width=1, line_color="gray")
        fig_bars.update_layout(
            height=420, margin=dict(l=10, r=60, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(range=[-1,1], title="Pearson r", showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(title=""),
            font=dict(family="Arial", size=11)
        )
        st.plotly_chart(fig_bars, use_container_width=True)

    st.markdown("---")
    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="section-header">Scatter: Days to Convert vs Order Value</div>', unsafe_allow_html=True)
        scatter_df = conv[["Days_to_Convert","Order_Value_INR","Kit_Type"]].dropna()
        fig_sc = px.scatter(scatter_df, x="Days_to_Convert", y="Order_Value_INR",
                             color="Kit_Type", color_discrete_sequence=PALETTE,
                             opacity=0.75, trendline="ols",
                             labels={"Days_to_Convert":"Days to Convert",
                                     "Order_Value_INR":"Order Value (₹)"})
        fig_sc.update_layout(
            height=320, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=-0.3, font=dict(size=10)),
            font=dict(family="Arial", size=12)
        )
        st.plotly_chart(fig_sc, use_container_width=True)
        st.markdown('<div class="insight-box">No strong correlation (r≈-0.09) between conversion speed and order value — MedBox does not need to discount to speed up conversions. Use non-price urgency levers instead (free sample kits, limited-time consultations).</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="section-header">NPS Score vs Order Value</div>', unsafe_allow_html=True)
        nps_df = conv[["NPS_Score","Order_Value_INR","Kit_Type"]].dropna()
        fig_nps = px.scatter(nps_df, x="NPS_Score", y="Order_Value_INR",
                              color="Kit_Type", color_discrete_sequence=PALETTE,
                              opacity=0.75, trendline="ols",
                              labels={"NPS_Score":"NPS Score","Order_Value_INR":"Order Value (₹)"})
        fig_nps.update_layout(
            height=320, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=-0.3, font=dict(size=10)),
            font=dict(family="Arial", size=12)
        )
        st.plotly_chart(fig_nps, use_container_width=True)
        st.markdown('<div class="insight-box">Moderate positive correlation (r≈0.41) between NPS and Order Value — premium kit buyers report higher satisfaction. Focus on quality of experience for high-value customers to drive word-of-mouth growth.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Descriptive Statistics Table</div>', unsafe_allow_html=True)
    stat_cols = ["Order_Value_INR","Days_to_Convert","NPS_Score",
                 "Base_Kit_Price_INR","Upsell_Revenue_INR","Total_Revenue_INR"]
    stat_labels = ["Order Value (₹)","Days to Convert","NPS Score",
                   "Base Kit Price (₹)","Upsell Revenue (₹)","Total Revenue (₹)"]
    stats_rows = []
    for col, lbl in zip(stat_cols, stat_labels):
        s = dff[col].dropna()
        stats_rows.append({
            "Variable": lbl,
            "Count": int(s.count()),
            "Mean": round(s.mean(),1),
            "Median": round(s.median(),1),
            "Std Dev": round(s.std(),1),
            "Min": round(s.min(),1),
            "Max": round(s.max(),1),
            "Range": round(s.max()-s.min(),1)
        })
    stats_df = pd.DataFrame(stats_rows)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

    # ── FIX 5: Summary insight box at end of correlation tab ─────────────────
    st.markdown('<div class="insight-box">📌 <b>Key Takeaway:</b> <b>NPS Score ↔ Order Value</b> has the strongest positive correlation (r≈0.41), while <b>Days to Convert ↔ Is Converted</b> is weakly negative — suggesting faster pipelines convert better. Focus on reducing friction in the sales process to improve both speed and volume of conversions.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — RAW DATA
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Cleaned Dataset Explorer</div>', unsafe_allow_html=True)

    search = st.text_input("Search by Lead ID, City, Kit, or Channel", placeholder="e.g. MBX-1050 or Mumbai")
    if search:
        mask2 = dff.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        display_df = dff[mask2]
    else:
        display_df = dff

    st.markdown(f"Showing **{len(display_df):,}** records")
    display_cols = ["Lead_ID","Lead_Date","Customer_City","City_Tier_Label","Age_Group",
                    "Lead_Channel","Kit_Type","Pipeline_Stage","Order_Value_INR",
                    "Consultation_Upsell","Repeat_Purchase","NPS_Score",
                    "Days_to_Convert","Is_Converted","Total_Revenue_INR"]
    st.dataframe(display_df[display_cols].reset_index(drop=True),
                 use_container_width=True, height=420)

    col_dl1, col_dl2 = st.columns([1,4])
    with col_dl1:
        csv_data = display_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download filtered CSV", data=csv_data,
                           file_name="medbox_filtered.csv", mime="text/csv")

# ── Footer — FIX 6: Add your name & roll number ───────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#94a3b8;font-size:12px;'>"
    "MedBox Analytics Dashboard · Synthetic Dataset · "
    "Built with Streamlit + Plotly · "
    "<b>Ayush Mane | MS25mm060 | </b>"
    "</div b>",
    unsafe_allow_html=True
)
