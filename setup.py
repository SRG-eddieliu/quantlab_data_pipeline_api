from setuptools import setup, find_packages


setup(
    name="quantlab_data_pipeline",
    version="0.1.0",
    description="Financial data pipeline using WRDS and Alpha Vantage MCP.",
    packages=find_packages(exclude=("tests", "notebooks")),
)
