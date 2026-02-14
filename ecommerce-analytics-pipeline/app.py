"""
E-Commerce Analytics Dashboard — Streamlit App
Interactive dashboard that runs SQL queries against the warehouse
and visualizes marketing attribution, conversion funnels, cohort retention,
RFM segmentation, and customer LTV.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
import sys

# run the pipeline on first load (generates the SQLite DB if missing)
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'warehouse.db')

if not os.path.exists(DB_PATH):
    sys.path.insert(0, os.path.dirname(__file__))
    from etl.extract_load import main as run_etl
    from etl.transform import run_models
    run_etl()
    run_models()


def query(sql):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


# ─── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 E-Commerce Analytics Dashboard")
st.caption("SQL-powered analytics pipeline · Marketing Attribution · Cohort Retention · RFM Segmentation")

# ─── KPIs ───────────────────────────────────────────────────
kpis = query("""
    SELECT
        (SELECT COUNT(*) FROM dim_customers) AS total_customers,
        (SELECT COUNT(*) FROM fact_orders) AS total_orders,
        (SELECT ROUND(SUM(total), 2) FROM fact_orders) AS total_revenue,
        (SELECT ROUND(AVG(total), 2) FROM fact_orders) AS avg_order_value,
        (SELECT COUNT(DISTINCT session_id) FROM fact_sessions) AS total_sessions,
        (SELECT COUNT(*) FROM dim_products) AS total_products
""").iloc[0]

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Customers", f"{int(kpis['total_customers'])}")
col2.metric("Orders", f"{int(kpis['total_orders'])}")
col3.metric("Revenue", f"${kpis['total_revenue']:,.0f}")
col4.metric("Avg Order", f"${kpis['avg_order_value']:,.2f}")
col5.metric("Sessions", f"{int(kpis['total_sessions']):,}")
col6.metric("Products", f"{int(kpis['total_products'])}")

st.divider()

# ─── Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Attribution", "🔄 Conversion Funnel", "📅 Cohort Retention",
    "👥 RFM Segments", "💰 Customer LTV", "📈 Revenue & Products"
])

# ─── TAB 1: Marketing Attribution ───────────────────────────
with tab1:
    st.subheader("Marketing Attribution Report")
    st.caption("Which channels drive revenue vs just traffic?")

    attr = query("SELECT * FROM analytics_attribution ORDER BY total_revenue DESC")

    col_a, col_b = st.columns(2)

    with col_a:
        fig = px.bar(
            attr, x='total_revenue', y='channel', orientation='h',
            color='channel', title='Revenue by Channel',
            labels={'total_revenue': 'Revenue ($)', 'channel': ''},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig = px.bar(
            attr, x='conversion_rate', y='channel', orientation='h',
            color='channel', title='Conversion Rate by Channel',
            labels={'conversion_rate': 'Conversion Rate (%)', 'channel': ''},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        fig = px.pie(
            attr, values='total_revenue', names='channel',
            title='Revenue Share by Channel',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        fig = px.bar(
            attr, x='channel', y='revenue_per_session',
            color='channel', title='Revenue per Session (Efficiency)',
            labels={'revenue_per_session': '$/Session', 'channel': ''},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        attr[['channel', 'total_sessions', 'unique_visitors', 'conversions',
              'conversion_rate', 'total_revenue', 'avg_order_value', 'revenue_per_session', 'revenue_share_pct']],
        use_container_width=True, hide_index=True
    )

    # insight box
    best = attr.loc[attr['conversion_rate'].idxmax()]
    most_traffic = attr.loc[attr['total_sessions'].idxmax()]
    st.info(
        f"💡 **{best['channel']}** has the highest conversion rate ({best['conversion_rate']}%) "
        f"but only {int(best['total_sessions'])} sessions. **{most_traffic['channel']}** drives the most "
        f"traffic ({int(most_traffic['total_sessions'])} sessions) at {most_traffic['conversion_rate']}% conversion. "
        f"**Recommendation:** Scale {best['channel']} traffic for higher ROI."
    )


# ─── TAB 2: Conversion Funnel ──────────────────────────────
with tab2:
    st.subheader("Checkout Conversion Funnel")
    st.caption("User journey from first page view to completed purchase")

    funnel = query("SELECT * FROM analytics_funnel ORDER BY stage_order")
    labels = ['Page View', 'Product View', 'Add to Cart', 'Checkout Start', 'Purchase']
    funnel['label'] = labels

    fig = go.Figure(go.Funnel(
        y=funnel['label'],
        x=funnel['unique_users'],
        textinfo="value+percent initial",
        marker=dict(color=['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe'])
    ))
    fig.update_layout(title='Checkout Funnel', height=400)
    st.plotly_chart(fig, use_container_width=True)

    # drop-off table
    funnel['drop_off'] = funnel['unique_users'].diff().fillna(0).astype(int)
    funnel['drop_off_pct'] = ''
    for i in range(1, len(funnel)):
        prev = funnel.iloc[i-1]['unique_users']
        if prev > 0:
            drop = (prev - funnel.iloc[i]['unique_users']) / prev * 100
            funnel.loc[funnel.index[i], 'drop_off_pct'] = f"{drop:.1f}%"

    overall = funnel.iloc[-1]['unique_users'] / funnel.iloc[0]['unique_users'] * 100
    st.metric("Overall Conversion Rate", f"{overall:.1f}%")

    st.dataframe(
        funnel[['label', 'unique_users', 'unique_sessions', 'pct_of_total', 'drop_off_pct']].rename(
            columns={'label': 'Stage', 'unique_users': 'Users', 'unique_sessions': 'Sessions',
                     'pct_of_total': '% of Total', 'drop_off_pct': 'Drop-off'}
        ),
        use_container_width=True, hide_index=True
    )

    biggest_drop_idx = (funnel['unique_users'].diff().abs()).iloc[1:].idxmax()
    drop_stage = funnel.loc[biggest_drop_idx, 'label']
    st.warning(
        f"⚠️ Biggest drop-off is at **{drop_stage}**. "
        f"Optimizing this stage would have the highest impact on revenue."
    )


# ─── TAB 3: Cohort Retention ───────────────────────────────
with tab3:
    st.subheader("Cohort Retention Analysis")
    st.caption("Do customers come back after their first month?")

    cohort = query("SELECT * FROM analytics_cohort_retention")

    pivot = cohort.pivot_table(
        index='cohort_month', columns='months_since_signup',
        values='retention_rate', aggfunc='first'
    )
    # limit to 0-6 months
    cols_to_show = [c for c in pivot.columns if c <= 6]
    pivot = pivot[cols_to_show]

    fig = px.imshow(
        pivot, text_auto='.0f', aspect='auto',
        color_continuous_scale='YlGnBu',
        labels=dict(x='Months Since Signup', y='Cohort', color='Retention %'),
        title='Cohort Retention Heatmap (%)'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # cohort revenue
    rev_pivot = cohort.pivot_table(
        index='cohort_month', columns='months_since_signup',
        values='cohort_revenue', aggfunc='sum'
    )
    rev_cols = [c for c in rev_pivot.columns if c <= 6]
    rev_pivot = rev_pivot[rev_cols]

    fig2 = px.imshow(
        rev_pivot, text_auto=',.0f', aspect='auto',
        color_continuous_scale='Oranges',
        labels=dict(x='Months Since Signup', y='Cohort', color='Revenue ($)'),
        title='Cohort Revenue Heatmap ($)'
    )
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)


# ─── TAB 4: RFM Segments ───────────────────────────────────
with tab4:
    st.subheader("RFM Customer Segmentation")
    st.caption("Recency × Frequency × Monetary scoring for customer targeting")

    rfm_summary = query("""
        SELECT rfm_segment, COUNT(*) AS customers,
               ROUND(AVG(monetary), 2) AS avg_spend,
               ROUND(AVG(frequency), 1) AS avg_orders,
               ROUND(AVG(recency_days), 0) AS avg_recency_days
        FROM analytics_rfm GROUP BY rfm_segment ORDER BY customers DESC
    """)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            rfm_summary, x='customers', y='rfm_segment', orientation='h',
            color='rfm_segment', title='Customers per RFM Segment',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            rfm_summary, x='avg_spend', y='rfm_segment', orientation='h',
            color='rfm_segment', title='Avg Lifetime Spend by Segment',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(rfm_summary, use_container_width=True, hide_index=True)

    # scatter: recency vs monetary colored by segment
    rfm_detail = query("SELECT * FROM analytics_rfm")
    fig = px.scatter(
        rfm_detail, x='recency_days', y='monetary', color='rfm_segment',
        size='frequency', hover_data=['full_name', 'acquisition_channel'],
        title='Customer Map: Recency vs Spend (size = order frequency)',
        labels={'recency_days': 'Days Since Last Order', 'monetary': 'Lifetime Spend ($)'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    champions = rfm_summary[rfm_summary['rfm_segment'] == 'Champions']
    at_risk = rfm_summary[rfm_summary['rfm_segment'] == 'At Risk']
    if not champions.empty and not at_risk.empty:
        st.info(
            f"💡 **Champions** ({int(champions.iloc[0]['customers'])} customers, "
            f"avg ${champions.iloc[0]['avg_spend']:,.0f}) are your best — reward them. "
            f"**At Risk** ({int(at_risk.iloc[0]['customers'])} customers) need win-back campaigns now."
        )


# ─── TAB 5: Customer LTV ───────────────────────────────────
with tab5:
    st.subheader("Customer Lifetime Value Analysis")
    st.caption("Which acquisition channels produce the most valuable customers?")

    ltv = query("""
        SELECT acquisition_channel,
               SUM(num_customers) AS customers,
               ROUND(SUM(total_ltv) / SUM(num_customers), 2) AS avg_ltv,
               ROUND(SUM(CASE WHEN customer_segment != 'never_purchased' THEN num_customers ELSE 0 END)
                     * 100.0 / SUM(num_customers), 1) AS purchase_rate
        FROM analytics_customer_ltv
        GROUP BY acquisition_channel ORDER BY avg_ltv DESC
    """)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            ltv, x='acquisition_channel', y='avg_ltv', color='acquisition_channel',
            title='Average Customer LTV by Channel',
            labels={'avg_ltv': 'Avg LTV ($)', 'acquisition_channel': ''},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            ltv, x='acquisition_channel', y='purchase_rate', color='acquisition_channel',
            title='Purchase Rate by Channel',
            labels={'purchase_rate': 'Purchase Rate (%)', 'acquisition_channel': ''},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(ltv, use_container_width=True, hide_index=True)

    # segment breakdown
    ltv_detail = query("""
        SELECT customer_segment, acquisition_channel, num_customers, avg_ltv, avg_orders, purchase_rate
        FROM analytics_customer_ltv
        WHERE customer_segment != 'never_purchased'
        ORDER BY avg_ltv DESC
    """)

    fig = px.treemap(
        ltv_detail, path=['acquisition_channel', 'customer_segment'],
        values='num_customers', color='avg_ltv',
        color_continuous_scale='Greens',
        title='Customer Segments by Channel (color = avg LTV)'
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

    best = ltv.iloc[0]
    st.success(
        f"💰 **{best['acquisition_channel']}** produces the highest-LTV customers "
        f"(avg ${best['avg_ltv']:,.2f}). If your CAC for this channel is below this, scale it."
    )


# ─── TAB 6: Revenue & Products ─────────────────────────────
with tab6:
    st.subheader("Revenue Trends & Product Performance")

    rev = query("SELECT * FROM analytics_revenue_trends ORDER BY order_month")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=rev['order_month'], y=rev['new_customer_revenue'],
                         name='New Customers', marker_color='#66c2a5'))
    fig.add_trace(go.Bar(x=rev['order_month'], y=rev['returning_customer_revenue'],
                         name='Returning Customers', marker_color='#fc8d62'))
    fig.update_layout(
        barmode='stack', title='Monthly Revenue: New vs Returning',
        xaxis_title='Month', yaxis_title='Revenue ($)', height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            rev, x='order_month', y='avg_order_value',
            title='Average Order Value Trend', markers=True,
            labels={'avg_order_value': 'AOV ($)', 'order_month': 'Month'}
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # channel x device heatmap
        cd = query("SELECT * FROM analytics_channel_device")
        pivot_cd = cd.pivot_table(index='channel', columns='device_type', values='conversion_rate')
        fig = px.imshow(
            pivot_cd, text_auto='.1f', color_continuous_scale='RdYlGn',
            title='Conversion Rate: Channel × Device',
            labels=dict(color='Conv %')
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # top products
    products = query("""
        SELECT product_name, category, price, total_views, total_purchases,
               total_revenue, view_to_cart_rate, cart_to_purchase_rate
        FROM dim_products WHERE total_views > 0
        ORDER BY total_revenue DESC LIMIT 15
    """)

    fig = px.bar(
        products.head(10), x='total_revenue', y='product_name', orientation='h',
        color='category', title='Top 10 Products by Revenue',
        labels={'total_revenue': 'Revenue ($)', 'product_name': ''},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    # product scatter
    all_prods = query("""
        SELECT product_name, category, view_to_cart_rate, cart_to_purchase_rate, total_revenue
        FROM dim_products WHERE total_views > 5
    """)
    fig = px.scatter(
        all_prods, x='view_to_cart_rate', y='cart_to_purchase_rate',
        size='total_revenue', color='category', hover_name='product_name',
        title='Product Conversion Rates (bubble size = revenue)',
        labels={'view_to_cart_rate': 'View → Cart %', 'cart_to_purchase_rate': 'Cart → Purchase %'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)


# ─── Footer ────────────────────────────────────────────────
st.divider()
st.caption("Built with Python, SQL, Pandas, Plotly & Streamlit · Data pipeline: ETL → SQL Transformations → Analytics")
