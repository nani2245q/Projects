"""
dashboard for the ecommerce analytics pipeline.
reads from the sqlite warehouse and shows the main analyses.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
import sys
import math

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'warehouse.db')

# generate warehouse if it doesn't exist yet
if not os.path.exists(DB_PATH):
    sys.path.insert(0, os.path.dirname(__file__))
    from etl.extract_load import main as run_etl
    from etl.transform import run_models
    run_etl()
    run_models()

# ─── theme config ──────────────────────────────────────────
THEMES = {
    'light': {
        'bg': 'white',
        'card_bg': '#f8f9fa',
        'card_border': '#e9ecef',
        'grid': '#f0f0f0',
        'text': '#1e293b',
        'subtext': '#64748b',
        'font_color': '#1e293b',
        'colorscale_seq': 'Blues',
        'colorscale_div': 'RdYlGn',
        'colorscale_heat': 'OrRd',
        'colorscale_tree': 'Greens',
    },
    'dark': {
        'bg': '#0e1117',
        'card_bg': '#1a1d23',
        'card_border': '#2d3139',
        'grid': '#1f2937',
        'text': '#e2e8f0',
        'subtext': '#94a3b8',
        'font_color': '#e2e8f0',
        'colorscale_seq': 'Blues',
        'colorscale_div': 'RdYlGn',
        'colorscale_heat': 'OrRd',
        'colorscale_tree': 'Greens',
    },
}

COLORS_LIGHT = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948']
COLORS_DARK = ['#6a9fd8', '#f5a854', '#f07b7d', '#8fd4cf', '#7cc76e', '#f2dc6b']


def get_theme():
    return THEMES[st.session_state.get('theme_mode', 'light')]


def get_colors():
    return COLORS_DARK if st.session_state.get('theme_mode', 'light') == 'dark' else COLORS_LIGHT


@st.cache_data(ttl=600)
def query(sql):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


def clean_chart(fig, height=360):
    """strip down plotly chrome so charts look less default"""
    t = get_theme()
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=10, t=35, b=0),
        title_font_size=14,
        title_font_color=t['text'],
        font_size=12,
        font_color=t['font_color'],
        plot_bgcolor=t['bg'],
        paper_bgcolor=t['bg'],
        showlegend=False,
        coloraxis_showscale=False
    )
    fig.update_xaxes(showgrid=True, gridcolor=t['grid'], tickfont_color=t['font_color'])
    fig.update_yaxes(showgrid=True, gridcolor=t['grid'], tickfont_color=t['font_color'])
    return fig


# ─── page setup ────────────────────────────────────────────
st.set_page_config(page_title="Commerce Analytics", layout="wide")

# initialize theme state
if 'theme_mode' not in st.session_state:
    st.session_state['theme_mode'] = 'light'

# theme toggle in header row
header_left, header_right = st.columns([8, 1])
with header_left:
    st.markdown("### Commerce Analytics")
with header_right:
    is_dark = st.toggle("Dark", value=st.session_state['theme_mode'] == 'dark', key='_dark_toggle')
    st.session_state['theme_mode'] = 'dark' if is_dark else 'light'

t = get_theme()
COLORS = get_colors()

# dynamic css based on theme — override streamlit's own theme completely
st.markdown(f"""
<style>
    /* page background */
    .stApp, [data-testid="stAppViewContainer"] {{
        background-color: {t['bg']};
        color: {t['text']};
    }}
    .stApp > header {{
        background-color: {t['bg']};
    }}
    [data-testid="stSidebar"] {{
        background-color: {t['card_bg']};
    }}

    /* text colors */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p,
    .stApp label, .stApp span, .stMarkdown {{
        color: {t['text']} !important;
    }}

    /* metric cards */
    [data-testid="stMetric"] {{
        background: {t['card_bg']};
        border: 1px solid {t['card_border']};
        border-radius: 6px;
        padding: 12px 16px;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.75rem;
        color: {t['subtext']} !important;
    }}
    [data-testid="stMetricLabel"] label, [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span {{
        color: {t['subtext']} !important;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.4rem;
        color: {t['text']} !important;
    }}
    [data-testid="stMetricValue"] div {{
        color: {t['text']} !important;
    }}

    /* tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        padding: 8px 16px;
        font-size: 0.85rem;
        color: {t['subtext']} !important;
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        color: {t['text']} !important;
        font-weight: 600;
    }}

    /* dataframe */
    [data-testid="stDataFrame"] {{
        background-color: {t['bg']};
    }}

    /* divider */
    hr {{
        border-color: {t['card_border']};
    }}

    /* toggle label */
    [data-testid="stToggle"] label span {{
        color: {t['text']} !important;
        font-weight: 500;
    }}
    [data-testid="stToggle"] {{
        opacity: 1 !important;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown(
    f"<span style='color:{t['subtext']}; font-size:0.85rem;'>"
    "marketing attribution / conversion analysis / customer segmentation / lifetime value / A/B testing"
    "</span>",
    unsafe_allow_html=True
)

# ─── KPIs ──────────────────────────────────────────────────
kpis = query("""
    SELECT
        (SELECT COUNT(*) FROM dim_customers) AS customers,
        (SELECT COUNT(*) FROM fact_orders) AS orders,
        (SELECT ROUND(SUM(total), 2) FROM fact_orders) AS revenue,
        (SELECT ROUND(AVG(total), 2) FROM fact_orders) AS aov,
        (SELECT COUNT(DISTINCT session_id) FROM fact_sessions) AS sessions
""").iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Customers", f"{int(kpis['customers']):,}")
c2.metric("Orders", f"{int(kpis['orders']):,}")
c3.metric("Revenue", f"${kpis['revenue']:,.0f}")
c4.metric("Avg Order Value", f"${kpis['aov']:,.2f}")
c5.metric("Sessions", f"{int(kpis['sessions']):,}")

st.markdown("---")

# ─── tabs ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Attribution", "Funnel", "Cohorts", "RFM", "LTV", "Revenue", "A/B Tests"
])

# ═══════════════════════════════════════════════════════════
# TAB 1 — Marketing Attribution
# ═══════════════════════════════════════════════════════════
with tab1:
    attr = query("SELECT * FROM analytics_attribution ORDER BY total_revenue DESC")

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            attr, x='total_revenue', y='channel', orientation='h',
            color_discrete_sequence=[COLORS[0]],
            title='Revenue by acquisition channel'
        )
        fig.update_traces(marker_line_width=0)
        clean_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            attr, x='conversion_rate', y='channel', orientation='h',
            color_discrete_sequence=[COLORS[1]],
            title='Session-to-purchase conversion rate (%)'
        )
        fig.update_traces(marker_line_width=0)
        clean_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

    left2, right2 = st.columns(2)

    with left2:
        fig = px.pie(
            attr, values='total_revenue', names='channel',
            title='Revenue share', color_discrete_sequence=COLORS
        )
        fig.update_layout(
            height=320, margin=dict(l=0, r=0, t=35, b=0),
            title_font_size=14, title_font_color=t['text'],
            font_color=t['font_color'],
            plot_bgcolor=t['bg'], paper_bgcolor=t['bg'],
            showlegend=True, legend=dict(font_size=11, font_color=t['font_color'])
        )
        fig.update_traces(textposition='inside', textinfo='percent')
        st.plotly_chart(fig, use_container_width=True)

    with right2:
        fig = px.bar(
            attr, x='channel', y='revenue_per_session',
            color_discrete_sequence=[COLORS[3]],
            title='Revenue per session ($)'
        )
        fig.update_traces(marker_line_width=0)
        clean_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

    # data table
    st.dataframe(
        attr[['channel', 'total_sessions', 'unique_visitors', 'conversions',
              'conversion_rate', 'total_revenue', 'avg_order_value',
              'revenue_per_session', 'revenue_share_pct']].rename(columns={
            'total_sessions': 'sessions', 'unique_visitors': 'visitors',
            'conversion_rate': 'conv %', 'total_revenue': 'revenue',
            'avg_order_value': 'AOV', 'revenue_per_session': 'rev/session',
            'revenue_share_pct': 'share %'
        }),
        use_container_width=True, hide_index=True
    )

    # findings
    best = attr.loc[attr['conversion_rate'].idxmax()]
    biggest = attr.loc[attr['total_sessions'].idxmax()]
    st.markdown(
        f"**Findings:** {best['channel']} converts best at {best['conversion_rate']}% "
        f"but has limited traffic ({int(best['total_sessions'])} sessions). "
        f"{biggest['channel']} has the most sessions ({int(biggest['total_sessions'])}) "
        f"but converts at only {biggest['conversion_rate']}%. "
        f"Scaling {best['channel']} traffic would likely have the highest ROI."
    )


# ═══════════════════════════════════════════════════════════
# TAB 2 — Conversion Funnel
# ═══════════════════════════════════════════════════════════
with tab2:
    funnel = query("SELECT * FROM analytics_funnel ORDER BY stage_order")
    stage_labels = ['Page View', 'Product View', 'Add to Cart', 'Checkout Start', 'Purchase']
    funnel['label'] = stage_labels

    funnel_colors_light = [COLORS[0], '#6a9ecf', '#8bb8d9', '#aed2e6', '#d0e8f2']
    funnel_colors_dark = [COLORS[0], '#5585b5', '#426f99', '#2f5a80', '#1e4568']
    f_colors = funnel_colors_dark if st.session_state['theme_mode'] == 'dark' else funnel_colors_light

    fig = go.Figure(go.Funnel(
        y=funnel['label'],
        x=funnel['unique_users'],
        textinfo="value+percent initial",
        marker=dict(color=f_colors),
        connector=dict(line=dict(color=t['grid']))
    ))
    fig.update_layout(
        height=380, margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor=t['bg'], paper_bgcolor=t['bg'],
        font_color=t['font_color']
    )
    st.plotly_chart(fig, use_container_width=True)

    # calculate dropoffs
    funnel['prev_users'] = funnel['unique_users'].shift(1)
    funnel['drop_pct'] = ((funnel['prev_users'] - funnel['unique_users']) / funnel['prev_users'] * 100).round(1)
    funnel.loc[funnel.index[0], 'drop_pct'] = 0

    overall = funnel.iloc[-1]['unique_users'] / funnel.iloc[0]['unique_users'] * 100

    col_m, col_t = st.columns([1, 3])
    with col_m:
        st.metric("Overall conversion", f"{overall:.1f}%")
    with col_t:
        st.dataframe(
            funnel[['label', 'unique_users', 'unique_sessions', 'pct_of_total', 'drop_pct']].rename(columns={
                'label': 'Stage', 'unique_users': 'Users', 'unique_sessions': 'Sessions',
                'pct_of_total': '% of top', 'drop_pct': 'Drop-off %'
            }),
            use_container_width=True, hide_index=True
        )

    worst_idx = funnel['drop_pct'].iloc[1:].idxmax()
    worst_stage = funnel.loc[worst_idx, 'label']
    worst_pct = funnel.loc[worst_idx, 'drop_pct']
    st.markdown(
        f"**Findings:** Largest drop-off is at **{worst_stage}** ({worst_pct}%). "
        f"Cart abandonment emails and checkout simplification would help here."
    )


# ═══════════════════════════════════════════════════════════
# TAB 3 — Cohort Retention
# ═══════════════════════════════════════════════════════════
with tab3:
    cohort = query("SELECT * FROM analytics_cohort_retention")

    # retention heatmap
    pivot_ret = cohort.pivot_table(
        index='cohort_month', columns='months_since_signup',
        values='retention_rate', aggfunc='first'
    )
    pivot_ret = pivot_ret[[c for c in pivot_ret.columns if c <= 6]]

    fig = px.imshow(
        pivot_ret, text_auto='.0f', aspect='auto',
        color_continuous_scale=t['colorscale_seq'],
        labels=dict(x='Months after signup', y='Signup cohort', color='Retention %'),
        title='Retention rate by cohort (%)'
    )
    fig.update_layout(
        height=450, margin=dict(l=0, r=0, t=35, b=0),
        title_font_size=14, title_font_color=t['text'],
        font_color=t['font_color'],
        plot_bgcolor=t['bg'], paper_bgcolor=t['bg'],
        coloraxis_showscale=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # revenue heatmap
    pivot_rev = cohort.pivot_table(
        index='cohort_month', columns='months_since_signup',
        values='cohort_revenue', aggfunc='sum'
    )
    pivot_rev = pivot_rev[[c for c in pivot_rev.columns if c <= 6]]

    fig2 = px.imshow(
        pivot_rev, text_auto=',.0f', aspect='auto',
        color_continuous_scale=t['colorscale_heat'],
        labels=dict(x='Months after signup', y='Signup cohort', color='Revenue $'),
        title='Revenue by cohort ($)'
    )
    fig2.update_layout(
        height=450, margin=dict(l=0, r=0, t=35, b=0),
        title_font_size=14, title_font_color=t['text'],
        font_color=t['font_color'],
        plot_bgcolor=t['bg'], paper_bgcolor=t['bg'],
        coloraxis_showscale=True
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        "**Findings:** Month-0 retention is naturally highest. "
        "The drop from month 0 to month 1 is where most churn happens. "
        "A post-purchase email series in the first 30 days could improve month-1 retention."
    )


# ═══════════════════════════════════════════════════════════
# TAB 4 — RFM Segmentation
# ═══════════════════════════════════════════════════════════
with tab4:
    rfm_agg = query("""
        SELECT rfm_segment, COUNT(*) AS customers,
               ROUND(AVG(monetary), 2) AS avg_spend,
               ROUND(AVG(frequency), 1) AS avg_orders,
               ROUND(AVG(recency_days), 0) AS avg_recency
        FROM analytics_rfm GROUP BY rfm_segment ORDER BY avg_spend DESC
    """)

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            rfm_agg, x='customers', y='rfm_segment', orientation='h',
            color_discrete_sequence=[COLORS[0]],
            title='Customers by segment'
        )
        fig.update_traces(marker_line_width=0)
        clean_chart(fig, 380)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            rfm_agg, x='avg_spend', y='rfm_segment', orientation='h',
            color_discrete_sequence=[COLORS[4]],
            title='Avg lifetime spend by segment'
        )
        fig.update_traces(marker_line_width=0)
        clean_chart(fig, 380)
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(rfm_agg, use_container_width=True, hide_index=True)

    # scatter plot
    rfm_all = query("SELECT * FROM analytics_rfm")
    fig = px.scatter(
        rfm_all, x='recency_days', y='monetary', color='rfm_segment',
        size='frequency', hover_data=['full_name', 'acquisition_channel'],
        color_discrete_sequence=COLORS,
        title='Recency vs lifetime spend (size = order count)'
    )
    fig.update_layout(
        height=480, margin=dict(l=0, r=0, t=35, b=0),
        title_font_size=14, title_font_color=t['text'],
        font_color=t['font_color'],
        plot_bgcolor=t['bg'], paper_bgcolor=t['bg'],
        legend=dict(font_size=10, font_color=t['font_color'], orientation='h', y=-0.15)
    )
    fig.update_xaxes(title='Days since last order', showgrid=True, gridcolor=t['grid'], tickfont_color=t['font_color'])
    fig.update_yaxes(title='Lifetime spend ($)', showgrid=True, gridcolor=t['grid'], tickfont_color=t['font_color'])
    st.plotly_chart(fig, use_container_width=True)

    champs = rfm_agg[rfm_agg['rfm_segment'] == 'Champions']
    at_risk = rfm_agg[rfm_agg['rfm_segment'] == 'At Risk']
    findings = "**Findings:** "
    if not champs.empty:
        findings += f"Champions ({int(champs.iloc[0]['customers'])} customers, avg ${champs.iloc[0]['avg_spend']:,.0f} spend) should get loyalty rewards. "
    if not at_risk.empty:
        findings += f"At Risk segment ({int(at_risk.iloc[0]['customers'])} customers) needs win-back campaigns before they churn."
    st.markdown(findings)


# ═══════════════════════════════════════════════════════════
# TAB 5 — Customer LTV
# ═══════════════════════════════════════════════════════════
with tab5:
    ltv = query("""
        SELECT acquisition_channel AS channel,
               SUM(num_customers) AS customers,
               ROUND(SUM(total_ltv) / SUM(num_customers), 2) AS avg_ltv,
               ROUND(SUM(CASE WHEN customer_segment != 'never_purchased' THEN num_customers ELSE 0 END)
                     * 100.0 / SUM(num_customers), 1) AS purchase_rate
        FROM analytics_customer_ltv
        GROUP BY acquisition_channel ORDER BY avg_ltv DESC
    """)

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            ltv, x='channel', y='avg_ltv',
            color_discrete_sequence=[COLORS[0]],
            title='Average customer LTV by channel'
        )
        fig.update_traces(marker_line_width=0)
        clean_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            ltv, x='channel', y='purchase_rate',
            color_discrete_sequence=[COLORS[4]],
            title='Purchase rate by channel (%)'
        )
        fig.update_traces(marker_line_width=0)
        clean_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(ltv, use_container_width=True, hide_index=True)

    # treemap
    ltv_detail = query("""
        SELECT customer_segment, acquisition_channel AS channel,
               num_customers, avg_ltv, avg_orders
        FROM analytics_customer_ltv
        WHERE customer_segment != 'never_purchased'
        ORDER BY avg_ltv DESC
    """)

    fig = px.treemap(
        ltv_detail, path=['channel', 'customer_segment'],
        values='num_customers', color='avg_ltv',
        color_continuous_scale=t['colorscale_tree'],
        title='Segment breakdown by channel (color = LTV)'
    )
    fig.update_layout(
        height=420, margin=dict(l=0, r=0, t=35, b=0),
        title_font_size=14, title_font_color=t['text'],
        font_color=t['font_color'],
        paper_bgcolor=t['bg']
    )
    st.plotly_chart(fig, use_container_width=True)

    best_ch = ltv.iloc[0]
    st.markdown(
        f"**Findings:** {best_ch['channel']} produces the highest-LTV customers "
        f"(${best_ch['avg_ltv']:,.2f} avg). If CAC for this channel stays below that, "
        f"it's worth scaling."
    )


# ═══════════════════════════════════════════════════════════
# TAB 6 — Revenue Trends & Products
# ═══════════════════════════════════════════════════════════
with tab6:
    rev = query("SELECT * FROM analytics_revenue_trends ORDER BY order_month")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rev['order_month'], y=rev['new_customer_revenue'],
        name='New customers', marker_color=COLORS[0]
    ))
    fig.add_trace(go.Bar(
        x=rev['order_month'], y=rev['returning_customer_revenue'],
        name='Returning customers', marker_color=COLORS[1]
    ))
    fig.update_layout(
        barmode='stack', title='Monthly revenue — new vs returning',
        height=380, margin=dict(l=0, r=0, t=35, b=0),
        title_font_size=14, title_font_color=t['text'],
        font_color=t['font_color'],
        plot_bgcolor=t['bg'], paper_bgcolor=t['bg'],
        legend=dict(font_size=11, font_color=t['font_color'], orientation='h', y=1.05)
    )
    fig.update_xaxes(showgrid=False, tickfont_color=t['font_color'])
    fig.update_yaxes(showgrid=True, gridcolor=t['grid'], title='Revenue ($)', tickfont_color=t['font_color'])
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        fig = px.line(
            rev, x='order_month', y='avg_order_value', markers=True,
            title='AOV trend', color_discrete_sequence=[COLORS[0]]
        )
        clean_chart(fig, 320)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        cd = query("SELECT * FROM analytics_channel_device")
        pivot_cd = cd.pivot_table(index='channel', columns='device_type', values='conversion_rate')
        fig = px.imshow(
            pivot_cd, text_auto='.1f', color_continuous_scale=t['colorscale_div'],
            title='Conversion: channel x device'
        )
        fig.update_layout(
            height=320, margin=dict(l=0, r=0, t=35, b=0),
            title_font_size=14, title_font_color=t['text'],
            font_color=t['font_color'],
            plot_bgcolor=t['bg'], paper_bgcolor=t['bg'],
            coloraxis_showscale=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # top products
    products = query("""
        SELECT product_name, category, total_revenue, total_purchases,
               view_to_cart_rate, cart_to_purchase_rate
        FROM dim_products WHERE total_views > 0
        ORDER BY total_revenue DESC LIMIT 10
    """)

    fig = px.bar(
        products, x='total_revenue', y='product_name', orientation='h',
        color='category', title='Top 10 products by revenue',
        color_discrete_sequence=COLORS
    )
    fig.update_layout(
        height=380, margin=dict(l=0, r=10, t=35, b=0),
        title_font_size=14, title_font_color=t['text'],
        font_color=t['font_color'],
        plot_bgcolor=t['bg'], paper_bgcolor=t['bg'],
        yaxis={'categoryorder': 'total ascending'},
        legend=dict(font_size=10, font_color=t['font_color'], orientation='h', y=-0.15)
    )
    fig.update_xaxes(showgrid=True, gridcolor=t['grid'], title='Revenue ($)', tickfont_color=t['font_color'])
    fig.update_yaxes(showgrid=False, tickfont_color=t['font_color'])
    st.plotly_chart(fig, use_container_width=True)

    # conversion scatter
    all_prods = query("""
        SELECT product_name, category, view_to_cart_rate, cart_to_purchase_rate, total_revenue
        FROM dim_products WHERE total_views > 5
    """)
    fig = px.scatter(
        all_prods, x='view_to_cart_rate', y='cart_to_purchase_rate',
        size='total_revenue', color='category', hover_name='product_name',
        color_discrete_sequence=COLORS,
        title='Product conversion rates (size = revenue)'
    )
    fig.update_layout(
        height=420, margin=dict(l=0, r=0, t=35, b=0),
        title_font_size=14, title_font_color=t['text'],
        font_color=t['font_color'],
        plot_bgcolor=t['bg'], paper_bgcolor=t['bg'],
        legend=dict(font_size=10, font_color=t['font_color'], orientation='h', y=-0.12)
    )
    fig.update_xaxes(title='View to cart %', showgrid=True, gridcolor=t['grid'], tickfont_color=t['font_color'])
    fig.update_yaxes(title='Cart to purchase %', showgrid=True, gridcolor=t['grid'], tickfont_color=t['font_color'])
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 7 — A/B Test Results
# ═══════════════════════════════════════════════════════════
def compute_significance(n_c, conv_c, n_t, conv_t):
    """Z-test for two proportions. Returns z-score, p-value, and lift."""
    p_c = conv_c / n_c if n_c > 0 else 0
    p_t = conv_t / n_t if n_t > 0 else 0
    lift = ((p_t - p_c) / p_c * 100) if p_c > 0 else 0

    # pooled proportion
    p_pool = (conv_c + conv_t) / (n_c + n_t) if (n_c + n_t) > 0 else 0
    se = math.sqrt(p_pool * (1 - p_pool) * (1/n_c + 1/n_t)) if (n_c > 0 and n_t > 0 and p_pool > 0 and p_pool < 1) else 0
    z = (p_t - p_c) / se if se > 0 else 0

    # two-tailed p-value approximation (no scipy needed)
    # using the complementary error function
    p_value = math.erfc(abs(z) / math.sqrt(2))

    return z, p_value, lift


with tab7:
    ab = query("SELECT * FROM analytics_ab_test_results ORDER BY test_id, variant")

    if ab.empty:
        st.info("No A/B test data available. Run the ETL pipeline to generate test data.")
    else:
        # get unique tests
        tests = ab[['test_id', 'test_name', 'description', 'metric', 'status']].drop_duplicates()

        for _, test in tests.iterrows():
            test_data = ab[ab['test_id'] == test['test_id']]
            control = test_data[test_data['variant'] == 'control'].iloc[0] if len(test_data[test_data['variant'] == 'control']) > 0 else None
            treatment = test_data[test_data['variant'] == 'treatment'].iloc[0] if len(test_data[test_data['variant'] == 'treatment']) > 0 else None

            if control is None or treatment is None:
                continue

            # compute statistical significance
            z, p_val, lift = compute_significance(
                int(control['sample_size']), int(control['conversions']),
                int(treatment['sample_size']), int(treatment['conversions'])
            )
            significant = p_val < 0.05

            # header with status badge
            status_color = COLORS[4] if test['status'] == 'completed' else COLORS[1]
            st.markdown(
                f"**{test['test_name']}** "
                f"<span style='background:{status_color}; color:white; padding:2px 8px; "
                f"border-radius:3px; font-size:0.75rem;'>{test['status']}</span>",
                unsafe_allow_html=True
            )
            st.markdown(f"<span style='color:{t['subtext']}; font-size:0.85rem;'>{test['description']}</span>",
                        unsafe_allow_html=True)

            # metrics row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Control conv. rate", f"{control['conversion_rate']}%")
            m2.metric("Treatment conv. rate", f"{treatment['conversion_rate']}%")
            m3.metric("Lift", f"{lift:+.1f}%")
            sig_label = "Yes (p<0.05)" if significant else "No"
            m4.metric("Significant", sig_label)

            # side-by-side charts
            left, right = st.columns(2)

            with left:
                bar_data = pd.DataFrame({
                    'variant': ['Control', 'Treatment'],
                    'conversion_rate': [control['conversion_rate'], treatment['conversion_rate']],
                    'sample_size': [control['sample_size'], treatment['sample_size']]
                })
                fig = px.bar(
                    bar_data, x='variant', y='conversion_rate',
                    text='conversion_rate',
                    color='variant',
                    color_discrete_map={'Control': COLORS[0], 'Treatment': COLORS[4]},
                    title='Conversion rate by variant (%)'
                )
                fig.update_traces(texttemplate='%{text}%', textposition='outside', marker_line_width=0)
                clean_chart(fig, 300)
                st.plotly_chart(fig, use_container_width=True)

            with right:
                bar_data2 = pd.DataFrame({
                    'variant': ['Control', 'Treatment'],
                    'avg_value': [control['avg_conversion_value'] or 0, treatment['avg_conversion_value'] or 0]
                })
                fig = px.bar(
                    bar_data2, x='variant', y='avg_value',
                    text='avg_value',
                    color='variant',
                    color_discrete_map={'Control': COLORS[0], 'Treatment': COLORS[4]},
                    title='Avg conversion value ($)'
                )
                fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside', marker_line_width=0)
                clean_chart(fig, 300)
                st.plotly_chart(fig, use_container_width=True)

            # detail table
            detail = test_data[['variant', 'sample_size', 'conversions', 'conversion_rate',
                                'avg_conversion_value', 'total_value']].rename(columns={
                'sample_size': 'n', 'conversion_rate': 'conv %',
                'avg_conversion_value': 'avg value', 'total_value': 'total value'
            })
            st.dataframe(detail, use_container_width=True, hide_index=True)

            # interpretation
            if significant:
                winner = "treatment" if lift > 0 else "control"
                st.markdown(
                    f"**Result:** Statistically significant (z={z:.2f}, p={p_val:.4f}). "
                    f"The **{winner}** variant performed better with a {abs(lift):.1f}% lift in conversion rate. "
                    f"Recommend rolling out the {winner} to all users."
                )
            else:
                st.markdown(
                    f"**Result:** Not statistically significant (z={z:.2f}, p={p_val:.4f}). "
                    f"The {abs(lift):.1f}% observed difference could be due to chance. "
                    f"Consider extending the test or increasing sample size."
                )

            st.markdown("---")
