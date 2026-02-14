# kernel_loader.py
# Loads/generates the dataset of 212 GPU kernels we use for benchmarking
# Each kernel has metadata like category, complexity, LOC, etc.

import pandas as pd
import numpy as np
import json
import os


class KernelLoader:
    # all the kernel types we're looking at
    KERNEL_CATEGORIES = [
        "matrix_ops", "convolution", "attention", "normalization",
        "activation", "pooling", "embedding", "loss_function",
        "optimizer_step", "reduction", "elementwise", "fft",
        "sparse_ops", "rnn_cell", "transformer_block"
    ]

    COMPLEXITY_LEVELS = ["simple", "moderate", "complex", "highly_complex"]

    def __init__(self, data_dir="data/kernels"):
        self.data_dir = data_dir
        self.kernels_df = None

    def generate_kernel_dataset(self, n_kernels=212, seed=42):
        """Generate synthetic kernel dataset for benchmarking."""
        rng = np.random.RandomState(seed)

        records = []
        for i in range(n_kernels):
            cat = rng.choice(self.KERNEL_CATEGORIES)
            complexity = rng.choice(
                self.COMPLEXITY_LEVELS,
                p=[0.25, 0.35, 0.25, 0.15]
            )

            # maps complexity to a multiplier for various metrics
            cmult = {
                "simple": 1.0, "moderate": 2.0,
                "complex": 3.5, "highly_complex": 6.0
            }[complexity]

            loc = int(rng.normal(50 * cmult, 15 * cmult))
            loc = max(10, loc)  # don't want negative or tiny LOC

            n_params = int(rng.exponential(3) * cmult) + 1
            uses_shared_mem = rng.random() < (0.3 * cmult / 2)
            uses_tensor_cores = rng.random() < 0.4
            has_custom_backward = rng.random() < (0.2 * cmult / 3)

            # base execution times by category (in ms)
            # TODO: these are rough estimates, might want to calibrate against real data
            base_time = {
                "matrix_ops": 2.5, "convolution": 4.0, "attention": 6.0,
                "normalization": 1.0, "activation": 0.5, "pooling": 1.2,
                "embedding": 1.5, "loss_function": 0.8, "optimizer_step": 3.0,
                "reduction": 1.0, "elementwise": 0.3, "fft": 3.5,
                "sparse_ops": 5.0, "rnn_cell": 4.5, "transformer_block": 8.0
            }[cat]

            pytorch_time = max(0.1, rng.normal(base_time * cmult, base_time * 0.3))

            # JAX time - sometimes faster, sometimes not
            speedup = rng.normal(1.1, 0.3)
            jax_time = pytorch_time / max(0.3, speedup)

            # quality metrics (beta distributions felt right for this)
            syn_correct = min(1.0, max(0.0, rng.beta(8, 2)))
            sem_equiv = min(1.0, max(0.0, rng.beta(6, 2.5)))
            num_prec = min(1.0, max(0.0, rng.beta(9, 1.5)))

            records.append({
                "kernel_id": f"K{i+1:04d}",
                "name": f"{cat}_{complexity}_{i+1}",
                "category": cat,
                "complexity": complexity,
                "lines_of_code": loc,
                "num_parameters": n_params,
                "uses_shared_memory": uses_shared_mem,
                "uses_tensor_cores": uses_tensor_cores,
                "has_custom_backward": has_custom_backward,
                "pytorch_exec_time_ms": round(pytorch_time, 4),
                "jax_exec_time_ms": round(jax_time, 4),
                "speedup_ratio": round(pytorch_time / jax_time, 4),
                "syntactic_correctness": round(syn_correct, 4),
                "semantic_equivalence": round(sem_equiv, 4),
                "numerical_precision": round(num_prec, 4),
                "translation_success": sem_equiv > 0.5 and syn_correct > 0.6
            })

        self.kernels_df = pd.DataFrame(records)
        return self.kernels_df

    def save_dataset(self, filename="kernel_dataset.csv"):
        if self.kernels_df is None:
            self.generate_kernel_dataset()
        path = os.path.join(self.data_dir, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.kernels_df.to_csv(path, index=False)
        return path

    def load_dataset(self, filename="kernel_dataset.csv"):
        path = os.path.join(self.data_dir, filename)
        self.kernels_df = pd.read_csv(path)
        return self.kernels_df

    def get_summary(self):
        """Quick summary stats for the dataset."""
        if self.kernels_df is None:
            return {}

        df = self.kernels_df
        return {
            "total_kernels": len(df),
            "categories": df["category"].nunique(),
            "category_distribution": df["category"].value_counts().to_dict(),
            "complexity_distribution": df["complexity"].value_counts().to_dict(),
            "avg_loc": round(df["lines_of_code"].mean(), 1),
            "avg_pytorch_time_ms": round(df["pytorch_exec_time_ms"].mean(), 4),
            "avg_jax_time_ms": round(df["jax_exec_time_ms"].mean(), 4),
            "avg_speedup": round(df["speedup_ratio"].mean(), 4),
            "translation_success_rate": round(df["translation_success"].mean() * 100, 2),
        }
