"""
Transform layer — reads SQL model files and executes them against the warehouse.
This is a simplified version of what dbt does: run SQL transformations
in dependency order to build staging tables, dimensional models, and analytics views.
"""

import sqlite3
import os
import glob

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'warehouse.db')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')


def run_sql_file(conn, filepath):
    """Execute a SQL file against the warehouse."""
    with open(filepath, 'r') as f:
        sql = f.read()

    # support multiple statements separated by semicolons
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        conn.execute(stmt)
    conn.commit()


def run_models():
    """Run all SQL models in order: staging -> marts -> analytics."""
    conn = sqlite3.connect(DB_PATH)

    # order matters — staging first, then dims/facts, then analytics
    model_groups = ['staging', 'marts', 'analytics']

    for group in model_groups:
        group_dir = os.path.join(MODELS_DIR, group)
        if not os.path.isdir(group_dir):
            print(f"  Skipping {group}/ (not found)")
            continue

        sql_files = sorted(glob.glob(os.path.join(group_dir, '*.sql')))
        print(f"\n--- {group.upper()} ({len(sql_files)} models) ---")

        for filepath in sql_files:
            name = os.path.basename(filepath)
            try:
                run_sql_file(conn, filepath)
                print(f"  OK  {name}")
            except Exception as e:
                print(f"  ERR {name}: {e}")

    conn.close()
    print("\nAll transformations complete.")


if __name__ == '__main__':
    run_models()
