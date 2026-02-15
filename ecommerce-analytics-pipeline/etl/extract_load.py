"""
Extract & Load — generates realistic ecommerce data and loads it into SQLite.
Simulates what Fivetran/Stitch would do: pull raw data from source systems
into a warehouse (we use SQLite as a local stand-in for Snowflake).
"""

import sqlite3
import random
import hashlib
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'warehouse.db')

CHANNELS = ['organic', 'paid_search', 'social_media', 'email', 'referral', 'direct']
DEVICES = ['desktop', 'mobile', 'tablet']
CITIES = ['Austin', 'Portland', 'Denver', 'Chicago', 'Seattle', 'New York', 'LA', 'Miami', 'Boston', 'Atlanta']
STATES = ['TX', 'OR', 'CO', 'IL', 'WA', 'NY', 'CA', 'FL', 'MA', 'GA']
PAYMENT_METHODS = ['credit_card', 'debit_card', 'paypal', 'apple_pay']

PRODUCTS = [
    ('Wireless Bluetooth Headphones', 'electronics', 89.99, 129.99),
    ('Smart Fitness Watch', 'electronics', 199.99, None),
    ('USB-C Hub 7-in-1', 'electronics', 49.99, 69.99),
    ('Mechanical Keyboard RGB', 'electronics', 129.99, None),
    ('4K Webcam Pro', 'electronics', 79.99, None),
    ('Organic Cotton T-Shirt', 'clothing', 29.99, None),
    ('Slim Fit Chinos', 'clothing', 59.99, None),
    ('Merino Wool Sweater', 'clothing', 89.99, 119.99),
    ('Running Jacket Waterproof', 'clothing', 149.99, None),
    ('Ceramic Pour-Over Coffee Set', 'home', 44.99, None),
    ('Bamboo Desk Organizer', 'home', 34.99, None),
    ('Scented Soy Candle Set', 'home', 24.99, None),
    ('LED Smart Lamp', 'home', 54.99, 79.99),
    ('Vitamin C Serum', 'beauty', 38.99, None),
    ('Natural Lip Balm Pack', 'beauty', 14.99, None),
    ('Yoga Mat Premium 6mm', 'sports', 39.99, None),
    ('Resistance Bands Set', 'sports', 19.99, None),
    ('Stainless Steel Water Bottle', 'sports', 27.99, None),
    ('Data Science from Scratch', 'books', 39.99, None),
    ('Designing Data-Intensive Apps', 'books', 44.99, None),
    ('The Lean Startup', 'books', 16.99, None),
    ('Atomic Habits', 'books', 18.99, None),
    ('Portable Charger 20000mAh', 'electronics', 35.99, 49.99),
    ('Noise Cancelling Earbuds', 'electronics', 69.99, None),
    ('Cotton Hoodie Oversized', 'clothing', 44.99, None),
]

# first names / last names for generating realistic customer names
FIRST_NAMES = [
    'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason',
    'Isabella', 'James', 'Mia', 'Benjamin', 'Charlotte', 'Lucas', 'Amelia',
    'Henry', 'Harper', 'Alexander', 'Evelyn', 'Daniel', 'Abigail', 'Jack',
    'Emily', 'Sebastian', 'Ella', 'Owen', 'Scarlett', 'Ryan', 'Grace', 'Leo',
    'Aria', 'Nathan', 'Lily', 'Caleb', 'Chloe', 'Isaac', 'Zoey', 'Connor',
    'Hannah', 'Dylan', 'Nora', 'Wyatt', 'Riley', 'Luke', 'Stella', 'Andrew',
    'Penelope', 'Jayden', 'Layla', 'Gabriel'
]
LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
    'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
    'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
    'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
    'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
    'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green',
    'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
    'Carter', 'Roberts'
]


def create_tables(conn):
    """Create raw tables — these mimic what you'd get from a source system."""
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS raw_customers (
        customer_id INTEGER PRIMARY KEY,
        email TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        acquisition_channel TEXT,
        created_at TEXT,
        last_active_at TEXT,
        city TEXT,
        state TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS raw_products (
        product_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT,
        price REAL,
        compare_at_price REAL,
        created_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS raw_orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        subtotal REAL,
        tax REAL,
        shipping REAL,
        total REAL,
        status TEXT,
        payment_method TEXT,
        attribution_channel TEXT,
        session_id TEXT,
        created_at TEXT,
        completed_at TEXT,
        FOREIGN KEY (customer_id) REFERENCES raw_customers(customer_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS raw_order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        unit_price REAL,
        FOREIGN KEY (order_id) REFERENCES raw_orders(order_id),
        FOREIGN KEY (product_id) REFERENCES raw_products(product_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS raw_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        session_id TEXT,
        event_type TEXT,
        product_id INTEGER,
        attribution_channel TEXT,
        device_type TEXT,
        page_url TEXT,
        time_on_page INTEGER,
        event_timestamp TEXT,
        FOREIGN KEY (customer_id) REFERENCES raw_customers(customer_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS raw_ab_tests (
        test_id INTEGER PRIMARY KEY,
        test_name TEXT NOT NULL,
        description TEXT,
        metric TEXT,
        start_date TEXT,
        end_date TEXT,
        status TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS raw_ab_assignments (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER,
        customer_id INTEGER,
        variant TEXT,
        assigned_at TEXT,
        converted INTEGER DEFAULT 0,
        conversion_value REAL DEFAULT 0.0,
        FOREIGN KEY (test_id) REFERENCES raw_ab_tests(test_id),
        FOREIGN KEY (customer_id) REFERENCES raw_customers(customer_id)
    )''')

    conn.commit()


def generate_data(conn, num_customers=200):
    """Generate fake but realistic ecommerce data for the warehouse."""
    c = conn.cursor()
    now = datetime.now()
    start_date = now - timedelta(days=365)  # one year of data

    # --- Products ---
    for i, (name, cat, price, compare) in enumerate(PRODUCTS, 1):
        c.execute(
            'INSERT INTO raw_products VALUES (?, ?, ?, ?, ?, ?)',
            (i, name, cat, price, compare,
             (start_date - timedelta(days=random.randint(0, 90))).isoformat())
        )

    # --- Customers ---
    customers = []
    for i in range(1, num_customers + 1):
        days_ago = random.randint(1, 350)
        created = now - timedelta(days=days_ago)
        last_active = created + timedelta(days=random.randint(0, days_ago))
        channel = random.choice(CHANNELS)
        city_idx = random.randint(0, len(CITIES) - 1)

        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        # make email from name
        email = f"{fname.lower()}.{lname.lower()}{i}@example.com"

        c.execute(
            'INSERT INTO raw_customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (i, email, fname, lname, channel,
             created.isoformat(), last_active.isoformat(),
             CITIES[city_idx], STATES[city_idx])
        )
        customers.append({
            'id': i, 'created': created, 'last_active': last_active,
            'channel': channel
        })

    # --- Events + Orders ---
    order_id = 0
    all_events = []
    all_orders = []
    all_items = []

    for cust in customers:
        # each customer has 1-12 sessions
        num_sessions = random.randint(1, 12)

        for s in range(num_sessions):
            # session happens between customer creation and now
            session_offset = random.random() * (now - cust['created']).total_seconds()
            session_start = cust['created'] + timedelta(seconds=session_offset)
            session_id = f"s_{cust['id']}_{s}_{int(session_start.timestamp())}"

            # 60% chance they use their original channel, 40% random
            channel = cust['channel'] if random.random() < 0.6 else random.choice(CHANNELS)
            device = random.choice(DEVICES)

            # page view event
            all_events.append((
                cust['id'], session_id, 'page_view', None,
                channel, device, '/', None, session_start.isoformat()
            ))

            # browse 1-6 products
            num_views = random.randint(1, 6)
            viewed_products = random.sample(range(1, len(PRODUCTS) + 1), min(num_views, len(PRODUCTS)))

            for j, pid in enumerate(viewed_products):
                t = session_start + timedelta(seconds=30 * (j + 1))
                time_on = random.randint(5, 180)
                all_events.append((
                    cust['id'], session_id, 'product_view', pid,
                    channel, device, f'/product/{pid}', time_on, t.isoformat()
                ))

            # add to cart — 35% chance per viewed product
            carted = [p for p in viewed_products if random.random() < 0.35]
            for pid in carted:
                t = session_start + timedelta(seconds=random.randint(120, 300))
                all_events.append((
                    cust['id'], session_id, 'add_to_cart', pid,
                    channel, device, f'/product/{pid}', None, t.isoformat()
                ))

            # checkout flow
            if carted and random.random() < 0.55:
                t_start = session_start + timedelta(seconds=random.randint(300, 600))
                all_events.append((
                    cust['id'], session_id, 'checkout_start', None,
                    channel, device, '/checkout', None, t_start.isoformat()
                ))

                # 25% abandon
                if random.random() < 0.25:
                    t_abandon = t_start + timedelta(seconds=random.randint(30, 300))
                    all_events.append((
                        cust['id'], session_id, 'checkout_abandon', None,
                        channel, device, '/checkout', None, t_abandon.isoformat()
                    ))
                else:
                    # complete order
                    order_id += 1
                    t_complete = t_start + timedelta(seconds=random.randint(60, 600))

                    items = []
                    subtotal = 0.0
                    for pid in carted:
                        qty = random.randint(1, 3)
                        price = PRODUCTS[pid - 1][2]
                        items.append((order_id, pid, qty, price))
                        subtotal += price * qty

                    tax = round(subtotal * 0.08, 2)
                    shipping = 0.0 if subtotal > 50 else 9.99
                    total = round(subtotal + tax + shipping, 2)
                    status = random.choice(['delivered', 'delivered', 'delivered', 'shipped', 'processing', 'pending'])

                    all_events.append((
                        cust['id'], session_id, 'checkout_complete', None,
                        channel, device, '/checkout/success', None, t_complete.isoformat()
                    ))

                    all_orders.append((
                        order_id, cust['id'], round(subtotal, 2), tax, shipping, total,
                        status, random.choice(PAYMENT_METHODS), channel,
                        session_id, t_complete.isoformat(), t_complete.isoformat()
                    ))
                    all_items.extend(items)

    # bulk insert everything
    c.executemany(
        'INSERT INTO raw_events (customer_id, session_id, event_type, product_id, '
        'attribution_channel, device_type, page_url, time_on_page, event_timestamp) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        all_events
    )

    c.executemany(
        'INSERT INTO raw_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        all_orders
    )

    c.executemany(
        'INSERT INTO raw_order_items (order_id, product_id, quantity, unit_price) '
        'VALUES (?, ?, ?, ?)',
        all_items
    )

    conn.commit()

    # --- A/B Tests ---
    # define a few realistic experiments
    ab_tests = [
        (1, 'Checkout Flow Redesign', 'Simplified single-page checkout vs multi-step',
         'conversion_rate', (now - timedelta(days=90)).date().isoformat(),
         (now - timedelta(days=30)).date().isoformat(), 'completed'),
        (2, 'Homepage Hero Banner', 'Product carousel vs lifestyle image hero',
         'conversion_rate', (now - timedelta(days=60)).date().isoformat(),
         (now - timedelta(days=15)).date().isoformat(), 'completed'),
        (3, 'Free Shipping Threshold', '$50 free shipping vs $35 free shipping threshold',
         'avg_order_value', (now - timedelta(days=45)).date().isoformat(),
         (now - timedelta(days=5)).date().isoformat(), 'completed'),
        (4, 'Product Page Layout', 'Larger images with sticky add-to-cart vs standard layout',
         'conversion_rate', (now - timedelta(days=20)).date().isoformat(),
         None, 'running'),
    ]

    c.executemany(
        'INSERT INTO raw_ab_tests VALUES (?, ?, ?, ?, ?, ?, ?)',
        ab_tests
    )

    # assign customers to tests and simulate outcomes
    ab_assignments = []
    # build a lookup of which customers placed orders (for realistic conversion)
    ordering_customers = set()
    for order in all_orders:
        ordering_customers.add(order[1])  # customer_id is index 1

    for test_id, name, desc, metric, start, end, status in ab_tests:
        test_start = datetime.fromisoformat(start)
        test_end = datetime.fromisoformat(end) if end else now

        # pick a random subset of customers for this test (60-80%)
        pool_size = int(num_customers * (0.6 + random.random() * 0.2))
        pool = random.sample(range(1, num_customers + 1), pool_size)

        # treatment effect — how much better the variant converts
        if test_id == 1:
            base_rate, lift = 0.12, 0.035   # checkout redesign: 12% -> ~15.5%
        elif test_id == 2:
            base_rate, lift = 0.08, 0.012   # hero banner: smaller effect
        elif test_id == 3:
            base_rate, lift = 0.15, 0.045   # free shipping: strong effect on AOV proxy
        else:
            base_rate, lift = 0.10, 0.018   # product page: moderate

        for cid in pool:
            variant = 'control' if random.random() < 0.5 else 'treatment'
            assigned_at = test_start + timedelta(
                seconds=random.random() * (test_end - test_start).total_seconds()
            )

            # conversion probability depends on variant
            conv_rate = base_rate if variant == 'control' else base_rate + lift
            converted = 1 if random.random() < conv_rate else 0

            # conversion value (order total if converted)
            if converted:
                if metric == 'avg_order_value':
                    # treatment gets slightly higher AOV
                    base_val = 60 + random.random() * 80
                    value = base_val * (1.12 if variant == 'treatment' else 1.0)
                else:
                    value = 40 + random.random() * 120
            else:
                value = 0.0

            ab_assignments.append((
                test_id, cid, variant,
                assigned_at.isoformat(),
                converted, round(value, 2)
            ))

    c.executemany(
        'INSERT INTO raw_ab_assignments (test_id, customer_id, variant, assigned_at, converted, conversion_value) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        ab_assignments
    )

    conn.commit()

    print(f"Loaded {num_customers} customers")
    print(f"Loaded {len(PRODUCTS)} products")
    print(f"Loaded {len(all_events)} behavior events")
    print(f"Loaded {len(all_orders)} orders with {len(all_items)} line items")
    print(f"Loaded {len(ab_tests)} A/B tests with {len(ab_assignments)} assignments")


def main():
    # wipe and rebuild
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    print("Creating raw tables...")
    create_tables(conn)

    print("Generating ecommerce data...")
    generate_data(conn, num_customers=200)

    conn.close()
    print(f"\nWarehouse ready: {DB_PATH}")


if __name__ == '__main__':
    main()
