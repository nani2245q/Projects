# benchmark_runner.py
# Runs the whole pipeline end to end:
# load kernels -> score them -> stats -> save results

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

from pipeline.kernel_loader import KernelLoader
from analysis.aqs_scorer import AQSScorer
from analysis.statistical_analysis import StatisticalAnalyzer


class BenchmarkRunner:
    def __init__(self, data_dir="data", output_dir="data/results"):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.loader = KernelLoader(os.path.join(data_dir, "kernels"))
        self.scorer = AQSScorer()
        self.analyzer = StatisticalAnalyzer()
        self.results_df = None

    def run_pipeline(self, n_kernels=212, save=True):
        """Run the full benchmarking pipeline."""
        print(f"[Pipeline] Starting benchmark with {n_kernels} kernels...")

        # generate kernel data
        print("[Step 1/4] Generating kernel dataset...")
        df = self.loader.generate_kernel_dataset(n_kernels)
        if save:
            self.loader.save_dataset()

        # compute AQS scores
        print("[Step 2/4] Computing AQS scores...")
        df = self.scorer.compute_aqs_batch(df)

        # run stats
        print("[Step 3/4] Running statistical analysis...")
        analysis = self.analyzer.run_full_analysis(df)

        # save everything
        print("[Step 4/4] Saving results...")
        if save:
            os.makedirs(self.output_dir, exist_ok=True)

            res_path = os.path.join(self.output_dir, "benchmark_results.csv")
            df.to_csv(res_path, index=False)

            report = self._build_report(df, analysis)
            rpt_path = os.path.join(self.output_dir, "benchmark_report.json")
            with open(rpt_path, "w") as f:
                json.dump(report, f, indent=2, default=str)

            print(f"[Pipeline] Results saved to {self.output_dir}/")

        self.results_df = df
        print("[Pipeline] Benchmark complete!")
        return df, analysis

    def _build_report(self, df, analysis):
        # put together the JSON report
        return {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_kernels": len(df),
                "pipeline_version": "1.0.0"
            },
            "summary": {
                "total_kernels": len(df),
                "translation_success_rate": round(df["translation_success"].mean() * 100, 2),
                "avg_aqs": round(df["aqs_score"].mean(), 4),
                "median_aqs": round(df["aqs_score"].median(), 4),
                "avg_speedup": round(df["speedup_ratio"].mean(), 4),
                "kernels_with_speedup": int((df["speedup_ratio"] > 1.0).sum()),
                "kernels_with_regression": int((df["speedup_ratio"] <= 1.0).sum()),
            },
            "aqs_distribution": {
                "excellent (>0.8)": int((df["aqs_score"] > 0.8).sum()),
                "good (0.6-0.8)": int(((df["aqs_score"] > 0.6) & (df["aqs_score"] <= 0.8)).sum()),
                "fair (0.4-0.6)": int(((df["aqs_score"] > 0.4) & (df["aqs_score"] <= 0.6)).sum()),
                "poor (<0.4)": int((df["aqs_score"] <= 0.4).sum()),
            },
            "by_category": df.groupby("category").agg({
                "aqs_score": "mean",
                "speedup_ratio": "mean",
                "translation_success": "mean"
            }).round(4).to_dict(orient="index"),
            "by_complexity": df.groupby("complexity").agg({
                "aqs_score": "mean",
                "speedup_ratio": "mean",
                "translation_success": "mean",
                "lines_of_code": "mean"
            }).round(4).to_dict(orient="index"),
            "statistical_tests": analysis.get("tests", {}),
            "correlations": analysis.get("correlations", {})
        }
