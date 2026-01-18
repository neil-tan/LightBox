"""Tests for conditional feature inclusion based on cookiecutter options."""

from pathlib import Path

import pytest

from conftest import OPTION_COMBINATIONS


@pytest.mark.parametrize("cookiecutter_options", OPTION_COMBINATIONS, indirect=True)
class TestConditionalFeatures:
    """Test that features are included/excluded based on options."""

    def test_hpo_files_when_use_hpo_yes(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """When use_hpo=yes, HPO-related files should exist."""
        if cookiecutter_options["use_hpo"] != "yes":
            pytest.skip("use_hpo is not 'yes'")

        # Check for HPO script (pattern-based)
        hpo_scripts = list(generated_project.glob("scripts/*hpo*"))
        assert len(hpo_scripts) >= 1, "No HPO script found when use_hpo=yes"

        # Check for HPO package directory
        hpo_dirs = list(generated_project.glob("**/hpo"))
        hpo_dirs = [d for d in hpo_dirs if d.is_dir()]
        assert len(hpo_dirs) >= 1, "No HPO directory found when use_hpo=yes"

        # Check for HPO test files
        hpo_tests = list(generated_project.glob("tests/*hpo*"))
        assert len(hpo_tests) >= 1, "No HPO test files found when use_hpo=yes"

    def test_no_hpo_files_when_use_hpo_no(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """When use_hpo=no, HPO-related files should not exist."""
        if cookiecutter_options["use_hpo"] != "no":
            pytest.skip("use_hpo is not 'no'")

        # Check that no HPO scripts exist
        hpo_scripts = list(generated_project.glob("scripts/*hpo*"))
        assert len(hpo_scripts) == 0, f"HPO scripts found when use_hpo=no: {hpo_scripts}"

        # Check that no HPO package directory exists
        package_hpo_dirs = list(generated_project.glob("test_ml_project/hpo"))
        assert len(package_hpo_dirs) == 0, "HPO directory found when use_hpo=no"

        # Check that no HPO test files exist
        hpo_tests = list(generated_project.glob("tests/*hpo*"))
        assert len(hpo_tests) == 0, f"HPO tests found when use_hpo=no: {hpo_tests}"

        # Check that helpers directory is removed (it's HPO-specific)
        helpers_dirs = list(generated_project.glob("tests/helpers"))
        assert len(helpers_dirs) == 0, "tests/helpers directory found when use_hpo=no"

    def test_wandb_logger_when_use_wandb_yes(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """When use_wandb=yes, config should contain logger section."""
        if cookiecutter_options["use_wandb"] != "yes":
            pytest.skip("use_wandb is not 'yes'")

        config_files = list(generated_project.glob("configs/*.yaml"))
        assert len(config_files) >= 1, "No config files found"

        # Check that at least one config has logger section
        found_logger = False
        for config_file in config_files:
            content = config_file.read_text()
            if "logger:" in content and "WandbLogger" in content:
                found_logger = True
                break

        assert found_logger, "No logger section with WandbLogger found when use_wandb=yes"

    def test_no_wandb_logger_when_use_wandb_no(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """When use_wandb=no, config should not contain logger section."""
        if cookiecutter_options["use_wandb"] != "no":
            pytest.skip("use_wandb is not 'no'")

        config_files = list(generated_project.glob("configs/*.yaml"))
        assert len(config_files) >= 1, "No config files found"

        # Check that no config has WandbLogger
        for config_file in config_files:
            content = config_file.read_text()
            assert "WandbLogger" not in content, (
                f"WandbLogger found in {config_file.name} when use_wandb=no"
            )

    def test_dataporter_submodule_when_use_dataporter_yes(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """When use_dataporter=yes, DataPorter submodule should be configured."""
        if cookiecutter_options["use_dataporter"] != "yes":
            pytest.skip("use_dataporter is not 'yes'")

        gitmodules = generated_project / ".gitmodules"
        assert gitmodules.exists(), ".gitmodules not found"

        content = gitmodules.read_text()
        # Check for DataPorter submodule (flexible matching)
        assert "DataPorter" in content, "DataPorter not found in .gitmodules when use_dataporter=yes"

    def test_no_dataporter_submodule_when_use_dataporter_no(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """When use_dataporter=no, DataPorter submodule should not be configured."""
        if cookiecutter_options["use_dataporter"] != "no":
            pytest.skip("use_dataporter is not 'no'")

        gitmodules = generated_project / ".gitmodules"
        if not gitmodules.exists():
            # No gitmodules means no DataPorter - that's fine
            return

        content = gitmodules.read_text()
        assert "DataPorter" not in content, (
            "DataPorter found in .gitmodules when use_dataporter=no"
        )


class TestFeatureCombinations:
    """Test specific feature combinations and their interactions."""

    @pytest.mark.parametrize(
        "cookiecutter_options",
        [
            pytest.param(
                {"use_hpo": "yes", "use_wandb": "yes", "use_dataporter": "yes"},
                id="all-features",
            ),
        ],
        indirect=True,
    )
    def test_all_features_enabled(self, generated_project: Path):
        """When all features are enabled, all components should be present."""
        # HPO files
        assert any(generated_project.glob("scripts/*hpo*")), "Missing HPO script"
        assert any(generated_project.glob("**/hpo")), "Missing HPO directory"

        # WandB logger
        config_content = next(generated_project.glob("configs/*.yaml")).read_text()
        assert "WandbLogger" in config_content, "Missing WandB logger"

        # DataPorter submodule
        gitmodules = generated_project / ".gitmodules"
        assert "DataPorter" in gitmodules.read_text(), "Missing DataPorter submodule"

    @pytest.mark.parametrize(
        "cookiecutter_options",
        [
            pytest.param(
                {"use_hpo": "no", "use_wandb": "no", "use_dataporter": "no"},
                id="minimal",
            ),
        ],
        indirect=True,
    )
    def test_minimal_features(self, generated_project: Path):
        """When all optional features are disabled, only core components should exist."""
        # No HPO files
        assert not any(generated_project.glob("scripts/*hpo*")), "Found HPO script in minimal"
        assert not any(generated_project.glob("test_ml_project/hpo")), "Found HPO dir in minimal"

        # No WandB logger
        config_content = next(generated_project.glob("configs/*.yaml")).read_text()
        assert "WandbLogger" not in config_content, "Found WandB logger in minimal"

        # No DataPorter submodule
        gitmodules = generated_project / ".gitmodules"
        assert "DataPorter" not in gitmodules.read_text(), "Found DataPorter in minimal"

        # But should still have LightningReflow (always required)
        assert "LightningReflow" in gitmodules.read_text(), "Missing required LightningReflow"
