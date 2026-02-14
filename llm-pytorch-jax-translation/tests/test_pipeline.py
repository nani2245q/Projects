# tests for the data pipeline and stats

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
import pandas as pd
from pipeline.kernel_loader import KernelLoader
from analysis.statistical_analysis import StatisticalAnalyzer
from analysis.aqs_scorer import AQSScorer


class TestKernelLoader:

    def test_generate_default_count(self):
        loader = KernelLoader()
        df = loader.generate_kernel_dataset()
        assert len(df) == 212

    def test_generate_custom_count(self):
        loader = KernelLoader()
        df = loader.generate_kernel_dataset(n_kernels=50)
        assert len(df) == 50

    def test_required_columns(self):
        loader = KernelLoader()
        df = loader.generate_kernel_dataset(n_kernels=10)
        required = ["kernel_id", "name", "category", "complexity", "lines_of_code",
                     "pytorch_exec_time_ms", "jax_exec_time_ms", "speedup_ratio",
                     "syntactic_correctness", "semantic_equivalence", "numerical_precision"]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_deterministic_seed(self):
        loader = KernelLoader()
        df1 = loader.generate_kernel_dataset(seed=42)
        df2 = loader.generate_kernel_dataset(seed=42)
        pd.testing.assert_frame_equal(df1, df2)

    def test_valid_ranges(self):
        loader = KernelLoader()
        df = loader.generate_kernel_dataset(n_kernels=100)
        assert (df["syntactic_correctness"] >= 0).all() and (df["syntactic_correctness"] <= 1).all()
        assert (df["semantic_equivalence"] >= 0).all() and (df["semantic_equivalence"] <= 1).all()
        assert (df["numerical_precision"] >= 0).all() and (df["numerical_precision"] <= 1).all()
        assert (df["lines_of_code"] > 0).all()
        assert (df["speedup_ratio"] > 0).all()

    def test_summary(self):
        loader = KernelLoader()
        loader.generate_kernel_dataset(n_kernels=50)
        summary = loader.get_summary()
        assert summary["total_kernels"] == 50
        assert "category_distribution" in summary


class TestStatisticalAnalyzer:

    def setup_method(self):
        loader = KernelLoader()
        df = loader.generate_kernel_dataset(n_kernels=100)
        scorer = AQSScorer()
        self.df = scorer.compute_aqs_batch(df)
        self.analyzer = StatisticalAnalyzer()

    def test_full_analysis_returns_all_keys(self):
        res = self.analyzer.run_full_analysis(self.df)
        assert "tests" in res
        assert "correlations" in res
        assert "descriptive" in res
        assert "group_comparisons" in res

    def test_anova_result_structure(self):
        res = self.analyzer.run_full_analysis(self.df)
        anova = res["tests"]["complexity_aqs_anova"]
        assert "f_statistic" in anova
        assert "p_value" in anova
        assert "significant" in anova

    def test_ttest_result_structure(self):
        res = self.analyzer.run_full_analysis(self.df)
        ttest = res["tests"]["speedup_ttest"]
        assert "t_statistic" in ttest
        assert "p_value" in ttest
        assert "mean_speedup" in ttest
