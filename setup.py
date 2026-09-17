"""
PyLedger Setup Configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PyLedger",
    version="2.1.0",
    author="PyLedger Contributors",
    author_email="support@pyledger.dev",
    description="Professional Accounting Library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    url="https://github.com/yourusername/pyledger",
    project_urls={
        "Documentation": "https://pyledger.readthedocs.io",
        "Bug Tracker": "https://github.com/yourusername/pyledger/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Accounting",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "reportlab>=4.0",
        "arabic_reshaper>=3.0",
        "python-bidi>=0.6",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.12",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ],
        "database": [
            "sqlalchemy>=1.4",
            "psycopg2-binary>=2.9",
            "pymysql>=1.0",
        ],
        "cli": [
            "click>=8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyledger=pyledger.cli:cli",
            "pyliger=pyledger.cli:cli",
        ],
    },
)
