# LLM-Based PyTorch to JAX Translation

Capstone research project analyzing the quality of LLM-generated translations from PyTorch GPU kernels to JAX/XLA. Includes a custom scoring metric (AQS), a data pipeline for benchmarking 212 GPU kernels, statistical analysis, and detailed visualizations.

## What This Does

- Generates a dataset of 212 GPU kernels across 15 categories (matrix ops, attention, convolution, etc.)
- Computes an **Aggregate Quality Score (AQS)** for each translation based on syntactic correctness, semantic equivalence, numerical precision, and performance
- Runs statistical tests (ANOVA, t-test, Kruskal-Wallis, regression) to find what affects translation quality
- Creates publication-ready visualizations of the results

## AQS Metric

The Aggregate Quality Score is a weighted composite:

```
AQS = 0.20 * Syntactic + 0.35 * Semantic + 0.25 * Precision + 0.20 * Performance
```

| Component | Weight | What it measures |
|-----------|--------|-----------------|
| Syntactic Correctness | 20% | Does the JAX code compile? |
| Semantic Equivalence | 35% | Does it produce correct outputs? |
| Numerical Precision | 25% | Are results within tolerance? |
| Performance Score | 20% | Is JAX faster than PyTorch? |

## Project Structure

```
llm-pytorch-jax-translation/
├── main.py                    # Run the full pipeline
├── src/
│   ├── pipeline/
│   │   ├── kernel_loader.py   # Generate/load 212 kernel dataset
│   │   └── benchmark_runner.py # End-to-end pipeline orchestration
│   ├── analysis/
│   │   ├── aqs_scorer.py      # AQS scoring metric
│   │   └── statistical_analysis.py  # Hypothesis tests & correlations
│   ├── translation/
│   │   └── translator.py      # PyTorch→JAX API mapping & examples
│   └── visualization/
│       └── plots.py           # 8 publication-quality charts
├── tests/
│   ├── test_aqs_scorer.py     # Unit tests for AQS
│   └── test_pipeline.py       # Integration tests
├── data/
│   ├── kernels/               # Kernel dataset CSV
│   └── results/               # Benchmark output + figures
├── requirements.txt
└── setup.py
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline
python main.py

# Run with custom kernel count
python main.py --kernels 100

# Skip plots
python main.py --no-plots
```

## Run Tests

```bash
pytest tests/ -v
```

## Output

The pipeline generates:
- `data/results/benchmark_results.csv` — full results for all 212 kernels
- `data/results/benchmark_report.json` — structured analysis report
- `data/results/figures/` — 8 visualization charts:
  - AQS distribution histogram
  - AQS by complexity (box plot)
  - AQS by category (bar chart)
  - Speedup distribution
  - Speedup vs LOC scatter plot
  - Correlation heatmap
  - Success rate by category
  - AQS component breakdown

## Key Findings

- Translation success rate varies significantly by kernel complexity
- Simple and moderate kernels translate well (~85%+ success), highly complex ones drop to ~60%
- JAX shows meaningful speedups for matrix operations and attention kernels
- Lines of code is a weak but significant predictor of AQS quality
- Semantic equivalence is the hardest component to achieve for complex kernels

## Tech Stack

- Python 3.9+
- pandas, NumPy — data processing
- SciPy — statistical testing
- Matplotlib, Seaborn — visualization
- pytest — testing
