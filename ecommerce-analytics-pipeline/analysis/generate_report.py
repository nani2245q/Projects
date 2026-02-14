"""
Generate an insights report from the analytics tables.
Pulls key findings and writes them as a markdown file — this is the
"turn data into a story" part that analysts need to do.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'warehouse.db')
REPORT_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'insights_report.md')


def query_one(sql):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(sql)
    row = cursor.fetchone()
    cols = [d[0] for d in cursor.description]
    conn.close()
    return dict(zip(cols, row)) if row else {}


def query_all(sql):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(sql)
    cols = [d[0] for d in cursor.description]
    rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
    conn.close()
    return rows


def generate():
    report = []
    report.append("# E-Commerce Analytics Report")
    report.append("")
    report.append("*Automated insights generated from the analytics data pipeline.*")
    report.append("")

    # --- Overview KPIs ---
    kpis = query_one("""
        SELECT
            COUNT(DISTINCT customer_id) AS total_customers,
            (SELECT COUNT(*) FROM fact_orders) AS total_orders,
            (SELECT ROUND(SUM(total), 2) FROM fact_orders) AS total_revenue,
            (SELECT ROUND(AVG(total), 2) FROM fact_orders) AS avg_order_value,
            (SELECT COUNT(DISTINCT session_id) FROM fact_sessions) AS total_sessions
        FROM dim_customers
    """)

    report.append("## Key Performance Indicators")
    report.append("")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Total Customers | {kpis['total_customers']} |")
    report.append(f"| Total Orders | {kpis['total_orders']} |")
    report.append(f"| Total Revenue | ${kpis['total_revenue']:,.2f} |")
    report.append(f"| Avg Order Value | ${kpis['avg_order_value']:,.2f} |")
    report.append(f"| Total Sessions | {kpis['total_sessions']} |")
    report.append("")

    # --- Funnel ---
    funnel = query_all("SELECT * FROM analytics_funnel ORDER BY stage_order")
    if funnel:
        overall_conv = round(funnel[-1]['unique_users'] / funnel[0]['unique_users'] * 100, 2)
        report.append("## Conversion Funnel")
        report.append("")
        report.append(f"Overall conversion rate (page view to purchase): **{overall_conv}%**")
        report.append("")
        report.append("| Stage | Users | % of Total |")
        report.append("|-------|-------|------------|")
        for row in funnel:
            stage_name = row['stage'].replace('_', ' ').title()
            report.append(f"| {stage_name} | {row['unique_users']} | {row['pct_of_total']}% |")
        report.append("")

        # find biggest dropoff
        max_drop = 0
        drop_stage = ""
        for i in range(1, len(funnel)):
            drop = funnel[i-1]['unique_users'] - funnel[i]['unique_users']
            pct = drop / funnel[i-1]['unique_users'] * 100
            if pct > max_drop:
                max_drop = pct
                drop_stage = funnel[i]['stage'].replace('_', ' ').title()

        report.append(f"**Insight:** The biggest drop-off happens at the **{drop_stage}** stage "
                      f"({max_drop:.1f}% drop). This suggests optimizing the {drop_stage.lower()} "
                      f"experience could have the highest impact on revenue.")
        report.append("")

    # --- Attribution ---
    attr = query_all("SELECT * FROM analytics_attribution ORDER BY total_revenue DESC")
    if attr:
        report.append("## Marketing Attribution")
        report.append("")
        report.append("| Channel | Sessions | Revenue | Conv. Rate | Rev/Session |")
        report.append("|---------|----------|---------|------------|-------------|")
        for row in attr:
            report.append(
                f"| {row['channel']} | {row['total_sessions']} | "
                f"${row['total_revenue']:,.2f} | {row['conversion_rate']}% | "
                f"${row['revenue_per_session']:.2f} |"
            )
        report.append("")

        # insight: best conversion vs best traffic
        best_conv = max(attr, key=lambda x: x['conversion_rate'])
        most_traffic = max(attr, key=lambda x: x['total_sessions'])
        best_efficiency = max(attr, key=lambda x: x['revenue_per_session'])

        report.append(f"**Insights:**")
        report.append(f"- **{best_conv['channel']}** has the highest conversion rate "
                      f"({best_conv['conversion_rate']}%) but only {best_conv['total_sessions']} sessions")
        report.append(f"- **{most_traffic['channel']}** drives the most traffic "
                      f"({most_traffic['total_sessions']} sessions) but converts at {most_traffic['conversion_rate']}%")
        report.append(f"- **{best_efficiency['channel']}** is the most efficient channel "
                      f"at ${best_efficiency['revenue_per_session']:.2f} revenue per session")
        report.append(f"- **Recommendation:** Invest in scaling {best_conv['channel']} traffic — "
                      f"it converts well but has low volume. "
                      f"For {most_traffic['channel']}, focus on CRO to improve its {most_traffic['conversion_rate']}% rate.")
        report.append("")

    # --- RFM ---
    rfm = query_all("""
        SELECT rfm_segment, COUNT(*) AS count, ROUND(AVG(monetary), 2) AS avg_spend
        FROM analytics_rfm GROUP BY rfm_segment ORDER BY count DESC
    """)
    if rfm:
        report.append("## Customer Segmentation (RFM)")
        report.append("")
        report.append("| Segment | Customers | Avg Spend |")
        report.append("|---------|-----------|-----------|")
        for row in rfm:
            report.append(f"| {row['rfm_segment']} | {row['count']} | ${row['avg_spend']:,.2f} |")
        report.append("")

        champions = next((r for r in rfm if r['rfm_segment'] == 'Champions'), None)
        at_risk = next((r for r in rfm if r['rfm_segment'] == 'At Risk'), None)
        lost = next((r for r in rfm if r['rfm_segment'] == 'Lost'), None)

        report.append("**Insights:**")
        if champions:
            report.append(f"- **Champions** ({champions['count']} customers, avg ${champions['avg_spend']:,.2f}) "
                          f"— these are your best customers. Offer loyalty rewards and early access.")
        if at_risk:
            report.append(f"- **At Risk** ({at_risk['count']} customers) — previously active buyers who are "
                          f"slipping away. Target with win-back email campaigns and special offers.")
        if lost:
            report.append(f"- **Lost** ({lost['count']} customers) — haven't bought in a long time. "
                          f"Consider a final re-engagement attempt before removing from active campaigns.")
        report.append("")

    # --- LTV by channel ---
    ltv = query_all("""
        SELECT acquisition_channel,
               SUM(num_customers) AS customers,
               ROUND(SUM(total_ltv) / SUM(num_customers), 2) AS avg_ltv
        FROM analytics_customer_ltv
        GROUP BY acquisition_channel
        ORDER BY avg_ltv DESC
    """)
    if ltv:
        report.append("## Customer Lifetime Value by Channel")
        report.append("")
        report.append("| Channel | Customers | Avg LTV |")
        report.append("|---------|-----------|---------|")
        for row in ltv:
            report.append(f"| {row['acquisition_channel']} | {row['customers']} | ${row['avg_ltv']:,.2f} |")
        report.append("")

        best_ltv = ltv[0]
        report.append(f"**Insight:** Customers from **{best_ltv['acquisition_channel']}** have the highest "
                      f"lifetime value (${best_ltv['avg_ltv']:,.2f}). If CAC for this channel is below this "
                      f"amount, it's a profitable acquisition strategy worth scaling.")
        report.append("")

    # --- Top products ---
    top_prods = query_all("""
        SELECT product_name, category, total_revenue, total_purchases, view_to_cart_rate
        FROM dim_products
        ORDER BY total_revenue DESC LIMIT 5
    """)
    if top_prods:
        report.append("## Top 5 Products by Revenue")
        report.append("")
        report.append("| Product | Category | Revenue | Purchases | View→Cart |")
        report.append("|---------|----------|---------|-----------|-----------|")
        for p in top_prods:
            report.append(
                f"| {p['product_name']} | {p['category']} | "
                f"${p['total_revenue']:,.2f} | {p['total_purchases']} | {p['view_to_cart_rate']}% |"
            )
        report.append("")

    # --- Recommendations ---
    report.append("## Strategic Recommendations")
    report.append("")
    report.append("1. **Optimize the checkout flow** — the conversion funnel shows significant "
                  "drop-off between add-to-cart and checkout. Implement cart abandonment emails, "
                  "simplify the checkout process, and consider guest checkout.")
    report.append("")
    report.append("2. **Double down on high-LTV channels** — invest more budget in acquisition "
                  "channels that produce customers with higher lifetime value, even if the initial "
                  "CPA is slightly higher.")
    report.append("")
    report.append("3. **Launch win-back campaigns** — the RFM analysis identified a segment of "
                  "'At Risk' customers who used to buy but have gone quiet. Automated email sequences "
                  "with personalized offers could recover this revenue.")
    report.append("")
    report.append("4. **Mobile optimization** — check the channel x device heatmap for mobile "
                  "conversion gaps. If mobile converts significantly lower, prioritize UX improvements "
                  "on mobile checkout.")
    report.append("")
    report.append("5. **Product bundling opportunities** — the top products span multiple categories. "
                  "Consider cross-sell bundles (e.g., electronics + accessories) to increase AOV.")
    report.append("")

    # Write report
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, 'w') as f:
        f.write('\n'.join(report))

    print(f"Insights report written to {REPORT_PATH}")


if __name__ == '__main__':
    generate()
