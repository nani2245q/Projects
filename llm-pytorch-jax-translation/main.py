# main.py
# Entry point for the PyTorch-to-JAX translation benchmark pipeline
#
# Usage:
#   python main.py                  # full pipeline
#   python main.py --no-plots       # skip charts
#   python main.py --kernels 100    # fewer kernels

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pipeline.benchmark_runner import BenchmarkRunner
from visualization.plots import BenchmarkVisualizer


def main():
    parser = argparse.ArgumentParser(description="PyTorch-to-JAX Translation Benchmark")
    parser.add_argument("--kernels", type=int, default=212,
                        help="Number of kernels to benchmark (default: 212)")
    parser.add_argument("--no-plots", action="store_true",
                        help="Skip generating visualizations")
    parser.add_argument("--output-dir", type=str, default="data/results",
                        help="Output directory")
    args = parser.parse_args()

    print("=" * 60)
    print("LLM-Based PyTorch to JAX Translation - Benchmark Pipeline")
    print("=" * 60)

    runner = BenchmarkRunner(output_dir=args.output_dir)
    df, analysis = runner.run_pipeline(n_kernels=args.kernels)

    # print out a summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Total kernels analyzed:     {len(df)}")
    print(f"Translation success rate:   {df['translation_success'].mean()*100:.1f}%")
    print(f"Mean AQS score:             {df['aqs_score'].mean():.4f}")
    print(f"Median AQS score:           {df['aqs_score'].median():.4f}")
    print(f"Mean speedup ratio:         {df['speedup_ratio'].mean():.3f}x")
    print(f"Kernels faster in JAX:      {(df['speedup_ratio'] > 1).sum()}/{len(df)}")

    print("\nAQS Grade Distribution:")
    for grade in ["Excellent", "Good", "Fair", "Poor"]:
        cnt = (df["aqs_grade"] == grade).sum()
        pct = cnt / len(df) * 100
        print(f"  {grade:12s} {cnt:4d} ({pct:5.1f}%)")

    print("\nTop Statistical Findings:")
    tests = analysis.get("tests", {})
    for name, res in tests.items():
        sig = "SIGNIFICANT" if res.get("significant") else "not significant"
        print(f"  [{sig:>15s}] {res.get('test', name)}: p={res.get('p_value', 'N/A')}")

    # make plots unless told not to
    if not args.no_plots:
        print("\nGenerating visualizations...")
        viz = BenchmarkVisualizer(os.path.join(args.output_dir, "figures"))
        viz.plot_all(df)

    print("\nDone! Results saved to:", args.output_dir)


if __name__ == "__main__":
    main()
