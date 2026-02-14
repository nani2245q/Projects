# plots.py
# Generates all the charts/figures for the benchmark results

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np
import pandas as pd
import os


class BenchmarkVisualizer:

    def __init__(self, output_dir="data/results/figures"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        sns.set_theme(style="whitegrid", font_scale=1.1)
        self.palette = sns.color_palette("viridis", 15)

    def plot_all(self, df):
        """Generate all the plots at once."""
        self.plot_aqs_distribution(df)
        self.plot_aqs_by_complexity(df)
        self.plot_aqs_by_category(df)
        self.plot_speedup_distribution(df)
        self.plot_speedup_vs_loc(df)
        self.plot_correlation_heatmap(df)
        self.plot_success_rate_by_category(df)
        self.plot_component_scores_radar(df)
        print(f"[Visualizer] All plots saved to {self.output_dir}/")

    def plot_aqs_distribution(self, df):
        fig, ax = plt.subplots(figsize=(10, 6))

        # shade the grade regions
        ax.axvspan(0, 0.4, alpha=0.08, color="red", label="Poor")
        ax.axvspan(0.4, 0.6, alpha=0.08, color="orange", label="Fair")
        ax.axvspan(0.6, 0.8, alpha=0.08, color="yellow", label="Good")
        ax.axvspan(0.8, 1.0, alpha=0.08, color="green", label="Excellent")

        sns.histplot(df["aqs_score"], bins=30, kde=True, color="#4f46e5", ax=ax)
        ax.axvline(df["aqs_score"].mean(), color="red", linestyle="--", label=f'Mean: {df["aqs_score"].mean():.3f}')
        ax.axvline(df["aqs_score"].median(), color="blue", linestyle=":", label=f'Median: {df["aqs_score"].median():.3f}')

        ax.set_xlabel("Aggregate Quality Score (AQS)")
        ax.set_ylabel("Count")
        ax.set_title("Distribution of AQS Across 212 GPU Kernels")
        ax.legend(loc="upper left", fontsize=9)

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_dir, "aqs_distribution.png"), dpi=150)
        plt.close()

    def plot_aqs_by_complexity(self, df):
        fig, ax = plt.subplots(figsize=(9, 6))
        order = ["simple", "moderate", "complex", "highly_complex"]
        sns.boxplot(data=df, x="complexity", y="aqs_score", order=order,
                    palette="coolwarm", ax=ax)
        sns.stripplot(data=df, x="complexity", y="aqs_score", order=order,
                      color="black", alpha=0.3, size=3, ax=ax)

        ax.set_xlabel("Kernel Complexity")
        ax.set_ylabel("AQS Score")
        ax.set_title("AQS by Kernel Complexity Level")

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_dir, "aqs_by_complexity.png"), dpi=150)
        plt.close()

    def plot_aqs_by_category(self, df):
        # horizontal bars sorted by mean AQS
        fig, ax = plt.subplots(figsize=(10, 7))
        cat_means = df.groupby("category")["aqs_score"].mean().sort_values()
        colors = sns.color_palette("viridis", len(cat_means))

        bars = ax.barh(cat_means.index, cat_means.values, color=colors)

        for bar, val in zip(bars, cat_means.values):
            ax.text(val + 0.005, bar.get_y() + bar.get_height()/2, f"{val:.3f}",
                    va="center", fontsize=9)

        ax.set_xlabel("Mean AQS Score")
        ax.set_title("Mean AQS by Kernel Category")
        ax.set_xlim(0, 1)

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_dir, "aqs_by_category.png"), dpi=150)
        plt.close()

    def plot_speedup_distribution(self, df):
        fig, ax = plt.subplots(figsize=(10, 6))

        sns.histplot(df["speedup_ratio"], bins=30, kde=True, color="#10b981", ax=ax)
        ax.axvline(1.0, color="red", linewidth=2, linestyle="--", label="No speedup (1.0x)")
        ax.axvline(df["speedup_ratio"].mean(), color="blue", linestyle=":",
                    label=f'Mean: {df["speedup_ratio"].mean():.2f}x')

        pct_faster = (df["speedup_ratio"] > 1.0).mean() * 100
        ax.text(0.98, 0.95, f'{pct_faster:.0f}% kernels faster in JAX',
                transform=ax.transAxes, ha="right", va="top", fontsize=10,
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

        ax.set_xlabel("Speedup Ratio (PyTorch / JAX)")
        ax.set_ylabel("Count")
        ax.set_title("Distribution of Speedup Ratios")
        ax.legend()

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_dir, "speedup_distribution.png"), dpi=150)
        plt.close()

    def plot_speedup_vs_loc(self, df):
        # scatter: LOC vs speedup, color = AQS
        fig, ax = plt.subplots(figsize=(10, 7))

        sc = ax.scatter(
            df["lines_of_code"], df["speedup_ratio"],
            c=df["aqs_score"], cmap="viridis", alpha=0.7, s=40, edgecolor="white"
        )
        plt.colorbar(sc, ax=ax, label="AQS Score")
        ax.axhline(1.0, color="red", linestyle="--", alpha=0.5)

        ax.set_xlabel("Lines of Code")
        ax.set_ylabel("Speedup Ratio")
        ax.set_title("Speedup vs Code Complexity (colored by AQS)")

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_dir, "speedup_vs_loc.png"), dpi=150)
        plt.close()

    def plot_correlation_heatmap(self, df):
        fig, ax = plt.subplots(figsize=(10, 8))

        cols = ["aqs_score", "speedup_ratio", "lines_of_code", "num_parameters",
                "syntactic_correctness", "semantic_equivalence", "numerical_precision"]
        cols = [c for c in cols if c in df.columns]

        corr = df[cols].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                    center=0, vmin=-1, vmax=1, ax=ax, square=True)

        ax.set_title("Correlation Matrix")
        plt.tight_layout()
        fig.savefig(os.path.join(self.output_dir, "correlation_heatmap.png"), dpi=150)
        plt.close()

    def plot_success_rate_by_category(self, df):
        # grouped bar: success rate + mean AQS per category
        fig, ax1 = plt.subplots(figsize=(12, 6))

        cat_data = df.groupby("category").agg({
            "translation_success": "mean",
            "aqs_score": "mean"
        }).sort_values("aqs_score", ascending=False)

        x = np.arange(len(cat_data))
        width = 0.35

        bars1 = ax1.bar(x - width/2, cat_data["translation_success"] * 100, width,
                        label="Success Rate (%)", color="#4f46e5")
        bars2 = ax1.bar(x + width/2, cat_data["aqs_score"] * 100, width,
                        label="Mean AQS (%)", color="#10b981")

        ax1.set_xticks(x)
        ax1.set_xticklabels(cat_data.index, rotation=45, ha="right")
        ax1.set_ylabel("Percentage")
        ax1.set_title("Translation Success Rate & AQS by Category")
        ax1.legend()

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_dir, "success_rate_by_category.png"), dpi=150)
        plt.close()

    def plot_component_scores_radar(self, df):
        # not actually a radar chart, just bars comparing the 4 AQS components
        # TODO: could make this a real radar/spider chart if we want to be fancy
        fig, ax = plt.subplots(figsize=(8, 5))

        components = {
            "Syntactic\nCorrectness": df["syntactic_correctness"].mean(),
            "Semantic\nEquivalence": df["semantic_equivalence"].mean(),
            "Numerical\nPrecision": df["numerical_precision"].mean(),
            "Performance\nScore": df["performance_score"].mean() if "performance_score" in df.columns else 0
        }

        colors = ["#4f46e5", "#7c3aed", "#10b981", "#f59e0b"]
        bars = ax.bar(components.keys(), components.values(), color=colors)

        for bar, val in zip(bars, components.values()):
            ax.text(bar.get_x() + bar.get_width()/2, val + 0.01, f"{val:.3f}",
                    ha="center", fontsize=10, fontweight="bold")

        ax.set_ylim(0, 1.1)
        ax.set_ylabel("Average Score")
        ax.set_title("AQS Component Breakdown (Average Across All Kernels)")

        plt.tight_layout()
        fig.savefig(os.path.join(self.output_dir, "component_scores.png"), dpi=150)
        plt.close()
