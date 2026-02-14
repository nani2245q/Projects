# aqs_scorer.py
# Computes the Aggregate Quality Score (AQS) for kernel translations
#
# AQS = w1*Syntactic + w2*Semantic + w3*Precision + w4*Performance
# weights default to 0.20, 0.35, 0.25, 0.20
# (semantic equivalence weighted highest since that's what matters most)

import numpy as np
import pandas as pd


class AQSScorer:

    DEFAULT_WEIGHTS = {
        "syntactic": 0.20,
        "semantic": 0.35,
        "precision": 0.25,
        "performance": 0.20
    }

    def __init__(self, weights=None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        assert abs(sum(self.weights.values()) - 1.0) < 1e-6, "Weights must sum to 1.0"

    def compute_performance_score(self, speedup_ratio):
        # sigmoid to normalize speedup to [0,1]
        # speedup=1.0 -> ~0.5, speedup>2x -> ~1.0, speedup<0.5 -> ~0.0
        return 1.0 / (1.0 + np.exp(-2.5 * (speedup_ratio - 1.0)))

    def compute_aqs(self, syntactic, semantic, precision, speedup_ratio):
        """Compute AQS for a single kernel."""
        perf = self.compute_performance_score(speedup_ratio)
        aqs = (
            self.weights["syntactic"] * syntactic +
            self.weights["semantic"] * semantic +
            self.weights["precision"] * precision +
            self.weights["performance"] * perf
        )
        return round(float(np.clip(aqs, 0, 1)), 4)

    def compute_aqs_batch(self, df):
        """Compute AQS for all rows. Adds aqs_score and aqs_grade columns."""
        df = df.copy()

        perf_scores = df["speedup_ratio"].apply(self.compute_performance_score)

        df["performance_score"] = perf_scores.round(4)
        df["aqs_score"] = (
            self.weights["syntactic"] * df["syntactic_correctness"] +
            self.weights["semantic"] * df["semantic_equivalence"] +
            self.weights["precision"] * df["numerical_precision"] +
            self.weights["performance"] * perf_scores
        ).clip(0, 1).round(4)

        # bin into grade categories
        df["aqs_grade"] = pd.cut(
            df["aqs_score"],
            bins=[0, 0.4, 0.6, 0.8, 1.0],
            labels=["Poor", "Fair", "Good", "Excellent"],
            include_lowest=True
        )

        return df

    def get_weight_description(self):
        # mostly for the report / documentation
        return {
            "formula": "AQS = w1*Syntactic + w2*Semantic + w3*Precision + w4*Performance",
            "weights": self.weights,
            "rationale": {
                "syntactic": "Does the translated code compile? Basic requirement.",
                "semantic": "Does it produce correct outputs? Most critical for usability.",
                "precision": "Are numerical results within acceptable tolerance?",
                "performance": "Does the JAX version run faster than PyTorch?"
            }
        }
