"""Setup script for {{cookiecutter.project_name}}.

This setup.py provides extended configuration for submodule support
and development installation.
"""

from pathlib import Path
from setuptools import setup, find_packages

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split("\n")
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith("#")]
else:
    requirements = ["torch", "lightning"]

setup(
    name="{{cookiecutter.project_slug}}",
    version="0.1.0",
    description="{{cookiecutter.description}}",
    author="{{cookiecutter.author}}",
    author_email="{{cookiecutter.author_email}}",
    packages=find_packages(exclude=["tests*", "external*"]),
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "isort",
        ],
    },
    python_requires=">={{cookiecutter.python_version}}",
)
