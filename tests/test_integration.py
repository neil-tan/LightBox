"""Integration tests for generated LightBox projects.

These tests verify that generated projects:
1. Have proper Claude Code integration files
2. Can import and run key components
3. Have valid configurations
"""

import subprocess
import sys
from pathlib import Path

import pytest

from conftest import OPTION_COMBINATIONS


@pytest.mark.parametrize("cookiecutter_options", OPTION_COMBINATIONS, indirect=True)
class TestClaudeIntegration:
    """Test Claude Code integration files are generated correctly."""

    def test_claude_md_exists(self, generated_project: Path):
        """CLAUDE.md is generated at project root."""
        claude_md = generated_project / "CLAUDE.md"
        assert claude_md.exists(), "CLAUDE.md not found"

    def test_claude_md_has_expected_sections(self, generated_project: Path):
        """CLAUDE.md contains expected documentation sections."""
        claude_md = generated_project / "CLAUDE.md"
        content = claude_md.read_text()

        expected_sections = [
            "## Project Overview",
            "## Commands",
            "### Training",
            "### Testing",
            "## Architecture",
            "## LightBox Integration",
            "/lightbox",
        ]

        for section in expected_sections:
            assert section in content, f"CLAUDE.md missing section: {section}"

    def test_skill_file_exists(self, generated_project: Path):
        """LightBox skill file is generated."""
        skill_file = generated_project / ".claude" / "skills" / "lightbox" / "SKILL.md"
        assert skill_file.exists(), "Skill file .claude/skills/lightbox/SKILL.md not found"

    def test_skill_file_has_frontmatter(self, generated_project: Path):
        """Skill file has required YAML frontmatter for Claude Code discovery."""
        skill_file = generated_project / ".claude" / "skills" / "lightbox" / "SKILL.md"
        content = skill_file.read_text()

        # Must start with YAML frontmatter
        assert content.startswith("---"), "Skill file must start with YAML frontmatter (---)"
        assert "name: lightbox" in content, "Skill file missing 'name: lightbox' in frontmatter"
        assert "description:" in content, "Skill file missing 'description:' in frontmatter"

    def test_skill_file_has_expected_content(self, generated_project: Path):
        """Skill file contains comprehensive integration guidance."""
        skill_file = generated_project / ".claude" / "skills" / "lightbox" / "SKILL.md"
        content = skill_file.read_text()

        expected_topics = [
            "## Quick Reference",
            "## LightningReflow Integration",
            "TorchCompileCallback",
            "max-autotune",  # Memory leak warning
            "reduce-overhead",  # Recommended mode
            "## LightningTune HPO Integration",
            "copy.deepcopy",  # Critical pattern
            "## Common Pitfalls",
            "OneCycleLR",
            "CUDA Graphs",
            "Sanity Check",
            "## Debugging Tips",
        ]

        for topic in expected_topics:
            assert topic in content, f"Skill file missing topic: {topic}"

    def test_skill_file_no_unrendered_templates(self, generated_project: Path):
        """Skill file has no unrendered cookiecutter variables."""
        skill_file = generated_project / ".claude" / "skills" / "lightbox" / "SKILL.md"
        content = skill_file.read_text()

        # Should not have raw cookiecutter markers
        assert "{{cookiecutter." not in content
        # But SHOULD have the rendered model name
        assert "testmodel" in content


@pytest.mark.parametrize("cookiecutter_options", OPTION_COMBINATIONS, indirect=True)
class TestConfigValidation:
    """Test that generated configuration files are valid."""

    def test_yaml_configs_are_valid(self, generated_project: Path):
        """All YAML config files are parseable."""
        yaml = pytest.importorskip("yaml", reason="PyYAML not installed")

        config_files = list(generated_project.glob("configs/*.yaml"))
        assert len(config_files) >= 1, "No config files found"

        for config_file in config_files:
            content = config_file.read_text()
            try:
                # Parse YAML (ignore Jinja2 remnants which shouldn't exist)
                yaml.safe_load(content)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {config_file.name}: {e}")

    def test_config_has_required_sections(self, generated_project: Path):
        """Main config has trainer, model, and data sections."""
        yaml = pytest.importorskip("yaml", reason="PyYAML not installed")

        config_file = generated_project / "configs" / "testmodel.yaml"
        assert config_file.exists(), "Main config file not found"

        config = yaml.safe_load(config_file.read_text())

        required_keys = ["trainer", "model", "data"]
        for key in required_keys:
            assert key in config, f"Config missing required section: {key}"


@pytest.mark.parametrize("cookiecutter_options", OPTION_COMBINATIONS, indirect=True)
class TestScriptImports:
    """Test that generated scripts have valid imports."""

    def test_training_script_syntax(self, generated_project: Path):
        """Training script has valid Python syntax."""
        train_script = generated_project / "scripts" / "train_testmodel.py"
        assert train_script.exists(), "Training script not found"

        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(train_script)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Syntax error in training script: {result.stderr}"

    def test_training_script_has_reflow_import(self, generated_project: Path):
        """Training script imports LightningReflowCLI."""
        train_script = generated_project / "scripts" / "train_testmodel.py"
        content = train_script.read_text()

        assert "from lightning_reflow import LightningReflowCLI" in content
        assert "LightningReflowCLI(" in content

    def test_hpo_script_exists_when_enabled(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """HPO script exists when use_hpo=yes."""
        if cookiecutter_options.get("use_hpo") != "yes":
            pytest.skip("HPO not enabled")

        hpo_script = generated_project / "scripts" / "testmodel_hpo.py"
        assert hpo_script.exists(), "HPO script not found when use_hpo=yes"

    def test_hpo_script_has_deepcopy(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """HPO script uses copy.deepcopy (critical pattern)."""
        if cookiecutter_options.get("use_hpo") != "yes":
            pytest.skip("HPO not enabled")

        hpo_script = generated_project / "scripts" / "testmodel_hpo.py"
        content = hpo_script.read_text()

        # Should import copy and use deepcopy
        assert "import copy" in content or "from copy import deepcopy" in content
        assert "deepcopy" in content, "HPO script should use copy.deepcopy"


@pytest.mark.parametrize("cookiecutter_options", OPTION_COMBINATIONS, indirect=True)
class TestPackageStructure:
    """Test that generated package has expected structure."""

    def test_models_module_exists(self, generated_project: Path):
        """Package has models module with base model."""
        models_init = generated_project / "test_ml_project" / "models" / "__init__.py"
        base_model = generated_project / "test_ml_project" / "models" / "base.py"

        assert models_init.exists(), "models/__init__.py not found"
        assert base_model.exists(), "models/base.py not found"

    def test_data_module_exists(self, generated_project: Path):
        """Package has data module with base datamodule."""
        data_init = generated_project / "test_ml_project" / "data" / "__init__.py"
        datamodule = generated_project / "test_ml_project" / "data" / "datamodule.py"

        assert data_init.exists(), "data/__init__.py not found"
        assert datamodule.exists(), "data/datamodule.py not found"

    def test_hpo_module_exists_when_enabled(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """Package has hpo module when use_hpo=yes."""
        if cookiecutter_options.get("use_hpo") != "yes":
            pytest.skip("HPO not enabled")

        hpo_init = generated_project / "test_ml_project" / "hpo" / "__init__.py"
        hpo_config = generated_project / "test_ml_project" / "hpo" / "config.py"

        assert hpo_init.exists(), "hpo/__init__.py not found when use_hpo=yes"
        assert hpo_config.exists(), "hpo/config.py not found when use_hpo=yes"

    def test_paths_module_exists(self, generated_project: Path):
        """Package has centralized paths module."""
        paths_module = generated_project / "test_ml_project" / "paths.py"
        assert paths_module.exists(), "paths.py not found"


@pytest.mark.parametrize(
    "cookiecutter_options",
    [
        pytest.param(
            {"use_hpo": "yes", "use_wandb": "yes", "use_dataporter": "yes", "create_virtualenv": "no", "pytest_workers": "0"},
            id="full-features",
        ),
    ],
    indirect=True,
)
class TestGeneratedProjectTests:
    """Test that the generated project's own tests pass.

    Note: This test requires real LightningReflow/LightningTune installations,
    not the mock git repos used for other tests. It's skipped in CI environments
    where only mock submodules are available.
    """

    def test_generated_tests_pass(self, generated_project: Path):
        """Generated project's tests should pass (requires real submodules)."""
        # Check if real submodules are available (not mocks)
        # Mock submodules only have README.md, real ones have Python packages
        reflow_init = generated_project / "external" / "LightningReflow" / "lightning_reflow" / "__init__.py"
        if not reflow_init.exists():
            pytest.skip(
                "Skipping: test requires real LightningReflow/LightningTune submodules, "
                "not mock repos. Run with real submodules to test generated project tests."
            )

        # Install the project first (in a subprocess to isolate)
        install_result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".", "-q"],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )

        if install_result.returncode != 0:
            pytest.skip(f"Could not install project: {install_result.stderr}")

        # Run pytest on the generated project
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-x"],
            cwd=generated_project,
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Print output for debugging
        if result.returncode != 0:
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")

        assert result.returncode == 0, f"Generated project tests failed:\n{result.stdout}\n{result.stderr}"
