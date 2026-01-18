"""Tests for core template generation functionality."""

import subprocess
import sys
from pathlib import Path

import pytest

from conftest import OPTION_COMBINATIONS, list_project_files


@pytest.mark.parametrize("cookiecutter_options", OPTION_COMBINATIONS, indirect=True)
class TestTemplateGeneration:
    """Test that the template generates correctly for all option combinations."""

    def test_project_generated_successfully(self, generated_project: Path):
        """Template generates without errors."""
        assert generated_project.exists()
        assert generated_project.is_dir()

    def test_project_slug_is_correct(self, generated_project: Path):
        """Project directory has correct slug-formatted name."""
        # "Test ML Project" -> "test-ml-project"
        assert generated_project.name == "test-ml-project"

    def test_has_expected_top_level_structure(self, generated_project: Path):
        """Project has expected top-level directories."""
        expected_dirs = {"configs", "scripts", "tests", "external"}

        actual_dirs = {
            d.name for d in generated_project.iterdir() if d.is_dir() and not d.name.startswith(".")
        }

        # Check that expected dirs are present (may have more)
        missing = expected_dirs - actual_dirs
        assert not missing, f"Missing top-level directories: {missing}"

    def test_has_python_package(self, generated_project: Path):
        """Project contains a Python package directory."""
        # Package name: "Test ML Project" -> "test_ml_project"
        package_name = "test_ml_project"
        package_dir = generated_project / package_name

        assert package_dir.exists(), f"Package directory {package_name} not found"
        assert (package_dir / "__init__.py").exists(), "Package missing __init__.py"

    def test_has_config_file(self, generated_project: Path):
        """Project has a model config file."""
        config_files = list(generated_project.glob("configs/*.yaml"))
        assert len(config_files) >= 1, "No config files found in configs/"

    def test_has_training_script(self, generated_project: Path):
        """Project has a training script."""
        train_scripts = list(generated_project.glob("scripts/train_*.py"))
        assert len(train_scripts) >= 1, "No training script found in scripts/"

    def test_has_pyproject_toml(self, generated_project: Path):
        """Project has pyproject.toml for packaging."""
        assert (generated_project / "pyproject.toml").exists()

    def test_python_package_is_importable(self, generated_project: Path):
        """Python package can be imported (syntax check)."""
        package_name = "test_ml_project"
        package_dir = generated_project / package_name

        # Check all Python files are syntactically valid
        for py_file in package_dir.rglob("*.py"):
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"Syntax error in {py_file.name}: {result.stderr}"

    def test_no_unrendered_templates(self, generated_project: Path):
        """No cookiecutter template variables remain unrendered."""
        files = list_project_files(generated_project)

        unrendered_markers = ["{{cookiecutter.", "{% if", "{% endif"]

        for file_path in files:
            full_path = generated_project / file_path
            # Skip binary files
            try:
                content = full_path.read_text()
            except UnicodeDecodeError:
                continue

            for marker in unrendered_markers:
                assert marker not in content, (
                    f"Unrendered template marker '{marker}' found in {file_path}"
                )

    def test_pip_install_dry_run(self, generated_project: Path):
        """pip install -e . can parse the package (dry-run check)."""
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".", "--dry-run"],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        # Dry run should succeed (it validates setup but doesn't install)
        assert result.returncode == 0, f"pip install dry-run failed: {result.stderr}"
