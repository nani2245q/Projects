from setuptools import setup, find_packages

setup(
    name="llm-pytorch-jax-translation",
    version="1.0.0",
    description="LLM-Based PyTorch to JAX Translation Tool with AQS Benchmarking",
    author="Prashanth Kambalapally",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "scipy>=1.11.0",
        "tqdm>=4.65.0",
        "tabulate>=0.9.0",
    ],
)
