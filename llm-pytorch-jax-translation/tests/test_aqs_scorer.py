# tests for the AQS scoring metric

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
import numpy as np
import pandas as pd
from analysis.aqs_scorer import AQSScorer


class TestAQSScorer:

    def setup_method(self):
        self.scorer = AQSScorer()

    def test_weights_sum_to_one(self):
        assert abs(sum(self.scorer.weights.values()) - 1.0) < 1e-6

    def test_perfect_score(self):
        score = self.scorer.compute_aqs(1.0, 1.0, 1.0, 2.0)
        assert score > 0.9

    def test_zero_score(self):
        score = self.scorer.compute_aqs(0.0, 0.0, 0.0, 0.1)
        assert score < 0.1

    def test_score_in_range(self):
        # just throw random inputs at it and make sure we stay in [0,1]
        for _ in range(100):
            syn = np.random.random()
            sem = np.random.random()
            prec = np.random.random()
            speed = np.random.uniform(0.1, 5.0)
            score = self.scorer.compute_aqs(syn, sem, prec, speed)
            assert 0 <= score <= 1

    def test_performance_score_symmetry(self):
        # speedup of 1.0 should be right around 0.5
        ps = self.scorer.compute_performance_score(1.0)
        assert 0.45 <= ps <= 0.55

    def test_performance_score_monotonic(self):
        scores = [self.scorer.compute_performance_score(s) for s in [0.5, 1.0, 1.5, 2.0, 3.0]]
        for i in range(len(scores) - 1):
            assert scores[i] < scores[i + 1]

    def test_batch_computation(self):
        df = pd.DataFrame({
            "syntactic_correctness": [0.9, 0.5, 0.1],
            "semantic_equivalence": [0.8, 0.6, 0.2],
            "numerical_precision": [0.95, 0.7, 0.3],
            "speedup_ratio": [1.5, 1.0, 0.5]
        })
        res = self.scorer.compute_aqs_batch(df)
        assert "aqs_score" in res.columns
        assert "aqs_grade" in res.columns
        assert len(res) == 3
        # first row should score higher than last
        assert res["aqs_score"].iloc[0] > res["aqs_score"].iloc[2]

    def test_custom_weights(self):
        custom = AQSScorer(weights={"syntactic": 0.5, "semantic": 0.2, "precision": 0.2, "performance": 0.1})
        score = custom.compute_aqs(1.0, 0.0, 0.0, 1.0)
        assert score > 0.5  # heavy syntactic weight + perfect syntactic
