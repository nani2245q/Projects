"""
Run all analytics queries and generate visualizations.
Reads from the transformed warehouse tables and creates charts + an insights report.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'warehouse.db')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output', 'charts')

# use a clean style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('Set2')


def query(sql):
    """Helper to run a query and return a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


def plot_attribution():
    """Marketing attribution — revenue and conversion by channel."""
    df = query("SELECT * FROM analytics_attribution ORDER BY total_revenue DESC")

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # revenue by channel
    colors = sns.color_palette('Set2', len(df))
    axes[0].barh(df['channel'], df['total_revenue'], color=colors)
    axes[0].set_xlabel('Revenue ($)')
    axes[0].set_title('Revenue by Channel')
    axes[0].invert_yaxis()
    axes[0].xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))

    # conversion rate
    axes[1].barh(df['channel'], df['conversion_rate'], color=colors)
    axes[1].set_xlabel('Conversion Rate (%)')
    axes[1].set_title('Conversion Rate by Channel')
    axes[1].invert_yaxis()

    # revenue per session (efficiency)
    axes[2].barh(df['channel'], df['revenue_per_session'], color=colors)
    axes[2].set_xlabel('Revenue per Session ($)')
    axes[2].set_title('Revenue Efficiency by Channel')
    axes[2].invert_yaxis()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '01_marketing_attribution.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created 01_marketing_attribution.png")


def plot_funnel():
    """Conversion funnel visualization."""
    df = query("SELECT * FROM analytics_funnel ORDER BY stage_order")

    fig, ax = plt.subplots(figsize=(10, 4))

    # horizontal bars getting narrower
    max_users = df['unique_users'].max()
    labels = ['Page View', 'Product View', 'Add to Cart', 'Checkout Start', 'Purchase']

    colors = plt.cm.Blues(
        [0.3 + 0.15 * i for i in range(len(df))]
    )

    for i, (_, row) in enumerate(df.iterrows()):
        width = row['unique_users'] / max_users
        ax.barh(i, width, color=colors[i], height=0.6, left=(1 - width) / 2)
        ax.text(0.5, i, f"{labels[i]}: {int(row['unique_users'])} users ({row['pct_of_total']}%)",
                ha='center', va='center', fontweight='bold', fontsize=10)

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, len(df) - 0.5)
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('Checkout Conversion Funnel', fontsize=13, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '02_conversion_funnel.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created 02_conversion_funnel.png")


def plot_revenue_trends():
    """Monthly revenue with new vs returning customer split."""
    df = query("SELECT * FROM analytics_revenue_trends ORDER BY order_month")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))

    # stacked bar: new vs returning revenue
    axes[0].bar(df['order_month'], df['new_customer_revenue'], label='New Customers', color='#66c2a5')
    axes[0].bar(df['order_month'], df['returning_customer_revenue'],
                bottom=df['new_customer_revenue'], label='Returning Customers', color='#fc8d62')
    axes[0].set_title('Monthly Revenue: New vs Returning')
    axes[0].set_ylabel('Revenue ($)')
    axes[0].legend(fontsize=9)
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))

    # line chart: AOV trend
    axes[1].plot(df['order_month'], df['avg_order_value'], marker='o', color='#8da0cb', linewidth=2)
    axes[1].fill_between(df['order_month'], df['avg_order_value'], alpha=0.2, color='#8da0cb')
    axes[1].set_title('Average Order Value Trend')
    axes[1].set_ylabel('AOV ($)')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:.0f}'))

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '03_revenue_trends.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created 03_revenue_trends.png")


def plot_cohort_retention():
    """Cohort retention heatmap."""
    df = query("SELECT * FROM analytics_cohort_retention")

    # pivot into matrix for heatmap
    pivot = df.pivot_table(
        index='cohort_month',
        columns='months_since_signup',
        values='retention_rate',
        aggfunc='first'
    )

    # only keep months 0-6 to keep it readable
    pivot = pivot[[c for c in pivot.columns if c <= 6]]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        pivot, annot=True, fmt='.0f', cmap='YlGnBu',
        linewidths=0.5, ax=ax, cbar_kws={'label': 'Retention %'}
    )
    ax.set_title('Cohort Retention Rate (%)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Months Since Signup')
    ax.set_ylabel('Signup Cohort')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '04_cohort_retention.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created 04_cohort_retention.png")


def plot_rfm():
    """RFM segment distribution."""
    df = query("""
        SELECT rfm_segment, COUNT(*) AS count,
               ROUND(AVG(monetary), 2) AS avg_spend,
               ROUND(AVG(frequency), 1) AS avg_orders
        FROM analytics_rfm
        GROUP BY rfm_segment
        ORDER BY count DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

    colors = sns.color_palette('Set2', len(df))

    # segment sizes
    axes[0].barh(df['rfm_segment'], df['count'], color=colors)
    axes[0].set_xlabel('Number of Customers')
    axes[0].set_title('Customer Segments (RFM)')
    axes[0].invert_yaxis()

    # avg spend per segment
    axes[1].barh(df['rfm_segment'], df['avg_spend'], color=colors)
    axes[1].set_xlabel('Average Lifetime Spend ($)')
    axes[1].set_title('Avg Spend by RFM Segment')
    axes[1].invert_yaxis()
    axes[1].xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '05_rfm_segments.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created 05_rfm_segments.png")


def plot_ltv_by_channel():
    """LTV comparison across acquisition channels."""
    df = query("""
        SELECT acquisition_channel,
               SUM(num_customers) AS customers,
               ROUND(SUM(total_ltv) / SUM(num_customers), 2) AS avg_ltv,
               ROUND(SUM(CASE WHEN customer_segment != 'never_purchased' THEN num_customers ELSE 0 END)
                     * 100.0 / SUM(num_customers), 1) AS purchase_rate
        FROM analytics_customer_ltv
        GROUP BY acquisition_channel
        ORDER BY avg_ltv DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    colors = sns.color_palette('Set2', len(df))

    axes[0].bar(df['acquisition_channel'], df['avg_ltv'], color=colors)
    axes[0].set_ylabel('Avg Customer LTV ($)')
    axes[0].set_title('Customer Lifetime Value by Channel')
    axes[0].tick_params(axis='x', rotation=30)
    axes[0].yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))

    axes[1].bar(df['acquisition_channel'], df['purchase_rate'], color=colors)
    axes[1].set_ylabel('Purchase Rate (%)')
    axes[1].set_title('Purchase Rate by Acquisition Channel')
    axes[1].tick_params(axis='x', rotation=30)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '06_ltv_by_channel.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created 06_ltv_by_channel.png")


def plot_channel_device():
    """Channel x device heatmap."""
    df = query("SELECT * FROM analytics_channel_device")

    pivot = df.pivot_table(index='channel', columns='device_type', values='conversion_rate')

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn', linewidths=0.5, ax=ax,
                cbar_kws={'label': 'Conversion Rate (%)'})
    ax.set_title('Conversion Rate: Channel x Device', fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '07_channel_device_heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created 07_channel_device_heatmap.png")


def plot_product_performance():
    """Top and bottom products by various metrics."""
    df = query("""
        SELECT product_name, category, total_views, total_purchases,
               total_revenue, view_to_cart_rate, cart_to_purchase_rate
        FROM dim_products
        WHERE total_views > 0
        ORDER BY total_revenue DESC
        LIMIT 10
    """)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # top 10 by revenue
    colors = sns.color_palette('Set2', len(df))
    short_names = [n[:22] + '...' if len(n) > 22 else n for n in df['product_name']]
    axes[0].barh(short_names, df['total_revenue'], color=colors)
    axes[0].set_xlabel('Revenue ($)')
    axes[0].set_title('Top 10 Products by Revenue')
    axes[0].invert_yaxis()
    axes[0].xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))

    # view to cart vs cart to purchase scatter
    all_prods = query("""
        SELECT product_name, category, view_to_cart_rate, cart_to_purchase_rate, total_revenue
        FROM dim_products WHERE total_views > 5
    """)
    categories = all_prods['category'].unique()
    cat_colors = {cat: sns.color_palette('Set2')[i] for i, cat in enumerate(categories)}

    for cat in categories:
        subset = all_prods[all_prods['category'] == cat]
        axes[1].scatter(
            subset['view_to_cart_rate'], subset['cart_to_purchase_rate'],
            s=subset['total_revenue'].clip(lower=1) * 0.5,
            alpha=0.7, label=cat, color=cat_colors[cat]
        )
    axes[1].set_xlabel('View → Cart Rate (%)')
    axes[1].set_ylabel('Cart → Purchase Rate (%)')
    axes[1].set_title('Product Conversion Rates (size = revenue)')
    axes[1].legend(fontsize=8, loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '08_product_performance.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Created 08_product_performance.png")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating analytics visualizations...\n")

    plot_attribution()
    plot_funnel()
    plot_revenue_trends()
    plot_cohort_retention()
    plot_rfm()
    plot_ltv_by_channel()
    plot_channel_device()
    plot_product_performance()

    print(f"\nAll charts saved to {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
