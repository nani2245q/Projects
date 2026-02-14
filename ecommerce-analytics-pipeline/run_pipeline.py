"""
Main pipeline runner — executes the full analytics workflow:
1. Extract & Load: generate raw ecommerce data into SQLite warehouse
2. Transform: run dbt-style SQL models (staging -> marts -> analytics)
3. Analyze: generate visualizations and insights report

Usage: python run_pipeline.py
"""

import sys
import os

# add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from etl.extract_load import main as run_extract_load
from etl.transform import run_models
from analysis.run_analysis import main as run_analysis
from analysis.generate_report import generate as run_report


def main():
    print("=" * 60)
    print("E-Commerce Analytics Pipeline")
    print("=" * 60)

    print("\n[1/4] EXTRACT & LOAD")
    print("-" * 40)
    run_extract_load()

    print("\n[2/4] TRANSFORM (SQL Models)")
    print("-" * 40)
    run_models()

    print("\n[3/4] ANALYZE (Visualizations)")
    print("-" * 40)
    run_analysis()

    print("\n[4/4] GENERATE REPORT")
    print("-" * 40)
    run_report()

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print(f"  Charts: output/charts/")
    print(f"  Report: output/insights_report.md")
    print("=" * 60)


if __name__ == '__main__':
    main()
