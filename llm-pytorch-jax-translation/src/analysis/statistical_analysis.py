# statistical_analysis.py
# Runs hypothesis tests, correlations, group comparisons on the benchmark data

import numpy as np
import pandas as pd
from scipy import stats


class StatisticalAnalyzer:

    def run_full_analysis(self, df):
        """Run all the stats and return everything in a dict."""
        res = {
            "tests": {},
            "correlations": {},
            "descriptive": {},
            "group_comparisons": {}
        }

        res["descriptive"] = self._descriptive_stats(df)
        res["correlations"] = self._correlation_analysis(df)

        # hypothesis tests
        res["tests"]["complexity_aqs_anova"] = self._anova_complexity_aqs(df)
        res["tests"]["category_speedup_kruskal"] = self._kruskal_category_speedup(df)
        res["tests"]["speedup_ttest"] = self._ttest_speedup_vs_one(df)
        res["tests"]["loc_aqs_regression"] = self._regression_loc_aqs(df)

        res["group_comparisons"] = self._group_comparisons(df)

        return res

    def _descriptive_stats(self, df):
        metrics = ["aqs_score", "speedup_ratio", "syntactic_correctness",
                    "semantic_equivalence", "numerical_precision", "lines_of_code"]
        out = {}
        for col in metrics:
            if col in df.columns:
                out[col] = {
                    "mean": round(df[col].mean(), 4),
                    "median": round(df[col].median(), 4),
                    "std": round(df[col].std(), 4),
                    "min": round(df[col].min(), 4),
                    "max": round(df[col].max(), 4),
                    "q25": round(df[col].quantile(0.25), 4),
                    "q75": round(df[col].quantile(0.75), 4),
                    "skewness": round(df[col].skew(), 4),
                    "kurtosis": round(df[col].kurtosis(), 4)
                }
        return out

    def _correlation_analysis(self, df):
        """Pearson + Spearman correlations between the main metrics."""
        num_cols = ["aqs_score", "speedup_ratio", "lines_of_code",
                    "num_parameters", "syntactic_correctness",
                    "semantic_equivalence", "numerical_precision"]
        cols = [c for c in num_cols if c in df.columns]

        pearson = df[cols].corr(method="pearson").round(4).to_dict()
        spearman = df[cols].corr(method="spearman").round(4).to_dict()

        # pull out a few key insights
        insights = []
        if "aqs_score" in df.columns and "lines_of_code" in df.columns:
            r, p = stats.pearsonr(df["aqs_score"], df["lines_of_code"])
            direction = "negative" if r < 0 else "positive"
            insights.append({
                "pair": "AQS vs Lines of Code",
                "pearson_r": round(r, 4),
                "p_value": round(p, 6),
                "interpretation": f"{'Significant' if p < 0.05 else 'Not significant'} {direction} correlation"
            })

        if "speedup_ratio" in df.columns and "lines_of_code" in df.columns:
            r, p = stats.pearsonr(df["speedup_ratio"], df["lines_of_code"])
            insights.append({
                "pair": "Speedup vs Lines of Code",
                "pearson_r": round(r, 4),
                "p_value": round(p, 6),
                "interpretation": f"{'Significant' if p < 0.05 else 'Not significant'} correlation"
            })

        return {
            "pearson": pearson,
            "spearman": spearman,
            "key_insights": insights
        }

    def _anova_complexity_aqs(self, df):
        # one-way ANOVA: does complexity level affect AQS?
        groups = [grp["aqs_score"].values for _, grp in df.groupby("complexity")]
        if len(groups) < 2:
            return {"test": "ANOVA", "error": "Not enough groups"}

        f_stat, p_val = stats.f_oneway(*groups)
        return {
            "test": "One-way ANOVA",
            "hypothesis": "H0: Mean AQS is the same across all complexity levels",
            "f_statistic": round(float(f_stat), 4),
            "p_value": round(float(p_val), 6),
            "significant": p_val < 0.05,
            "interpretation": "Reject H0 — complexity significantly affects AQS" if p_val < 0.05
                             else "Fail to reject H0 — no significant difference in AQS across complexity"
        }

    def _kruskal_category_speedup(self, df):
        # non-parametric test since speedup isn't necessarily normal
        groups = [grp["speedup_ratio"].values for _, grp in df.groupby("category")]
        if len(groups) < 2:
            return {"test": "Kruskal-Wallis", "error": "Not enough groups"}

        h_stat, p_val = stats.kruskal(*groups)
        return {
            "test": "Kruskal-Wallis H-test",
            "hypothesis": "H0: Speedup distributions are the same across categories",
            "h_statistic": round(float(h_stat), 4),
            "p_value": round(float(p_val), 6),
            "significant": p_val < 0.05,
            "interpretation": "Significant difference in speedup across categories" if p_val < 0.05
                             else "No significant difference in speedup across categories"
        }

    def _ttest_speedup_vs_one(self, df):
        # is mean speedup significantly different from 1.0?
        t_stat, p_val = stats.ttest_1samp(df["speedup_ratio"], 1.0)
        avg = df["speedup_ratio"].mean()
        return {
            "test": "One-sample t-test",
            "hypothesis": "H0: Mean speedup ratio = 1.0 (no speedup from translation)",
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(p_val), 6),
            "mean_speedup": round(float(avg), 4),
            "significant": p_val < 0.05,
            "interpretation": f"JAX translations are {'significantly faster' if avg > 1 and p_val < 0.05 else 'not significantly different'} than PyTorch"
        }

    def _regression_loc_aqs(self, df):
        # simple linear regression: LOC -> AQS
        # TODO: might want to try polynomial or log transform here
        slope, intercept, r_val, p_val, std_err = stats.linregress(
            df["lines_of_code"], df["aqs_score"]
        )
        return {
            "test": "Linear Regression (LOC → AQS)",
            "slope": round(float(slope), 6),
            "intercept": round(float(intercept), 4),
            "r_squared": round(float(r_val ** 2), 4),
            "p_value": round(float(p_val), 6),
            "std_error": round(float(std_err), 6),
            "interpretation": f"LOC explains {round(r_val**2 * 100, 1)}% of AQS variance"
        }

    def _group_comparisons(self, df):
        comparisons = {}

        # by complexity
        comp_stats = df.groupby("complexity").agg({
            "aqs_score": ["mean", "std", "count"],
            "speedup_ratio": ["mean", "std"],
            "translation_success": "mean"
        }).round(4)
        comp_stats.columns = ["_".join(c) for c in comp_stats.columns]
        comparisons["by_complexity"] = comp_stats.to_dict(orient="index")

        # by category
        cat_stats = df.groupby("category").agg({
            "aqs_score": ["mean", "std", "count"],
            "speedup_ratio": ["mean", "std"],
            "translation_success": "mean"
        }).round(4)
        cat_stats.columns = ["_".join(c) for c in cat_stats.columns]
        comparisons["by_category"] = cat_stats.to_dict(orient="index")

        return comparisons
