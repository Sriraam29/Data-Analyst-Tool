from setuptools import setup, find_packages

setup(
    name="ai-data-analysis-agent",
    version="0.1.0",
    description="An AI-powered natural language data analysis tool",
    author="raam",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=1.5.3",
        "duckdb>=0.9.0",
        "openai>=1.3.0",
        "plotly>=5.15.0",
        "openpyxl>=3.1.2",
        "xlrd>=2.0.1",
        "python-dotenv>=1.0.0",
        "numpy>=1.25.2",
        "scikit-learn>=1.3.0",
    ],
    python_requires='>=3.9',
) 