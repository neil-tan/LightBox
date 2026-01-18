"""Tests for git initialization and submodule setup."""

import subprocess
from pathlib import Path

import pytest

from conftest import OPTION_COMBINATIONS, count_submodules, get_submodule_names


@pytest.mark.parametrize("cookiecutter_options", OPTION_COMBINATIONS, indirect=True)
class TestGitInitialization:
    """Test that git is properly initialized by the post-gen hook."""

    def test_git_repo_initialized(self, generated_project: Path):
        """Git repository should be initialized (.git exists)."""
        git_dir = generated_project / ".git"
        assert git_dir.exists(), ".git directory not found"
        assert git_dir.is_dir(), ".git is not a directory"

    def test_initial_commit_exists(self, generated_project: Path):
        """Initial commit should exist with expected message."""
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"git log failed: {result.stderr}"
        assert "Initial commit" in result.stdout, (
            f"Initial commit message not found. Got: {result.stdout}"
        )

    def test_working_tree_clean(self, generated_project: Path):
        """Working tree should be clean after generation."""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"git status failed: {result.stderr}"
        # Allow some untracked files (like external/ submodules)
        # but there should be no modified files
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        modified = [l for l in lines if l.startswith("M ")]
        assert len(modified) == 0, f"Modified files found: {modified}"


@pytest.mark.parametrize("cookiecutter_options", OPTION_COMBINATIONS, indirect=True)
class TestSubmoduleConfiguration:
    """Test that submodules are properly configured based on options."""

    def test_gitmodules_exists(self, generated_project: Path):
        """Project should have .gitmodules file."""
        gitmodules = generated_project / ".gitmodules"
        assert gitmodules.exists(), ".gitmodules not found"

    def test_lightning_reflow_always_present(self, generated_project: Path):
        """LightningReflow submodule should always be present (required)."""
        submodule_names = get_submodule_names(generated_project)
        assert "LightningReflow" in submodule_names, (
            f"Required LightningReflow submodule not found. Found: {submodule_names}"
        )

    def test_submodule_count_matches_options(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """Number of submodules should match enabled options."""
        # Base: LightningReflow is always included
        expected_count = 1

        # Add LightningTune if use_hpo=yes
        if cookiecutter_options.get("use_hpo") == "yes":
            expected_count += 1

        # Add DataPorter if use_dataporter=yes
        if cookiecutter_options.get("use_dataporter") == "yes":
            expected_count += 1

        actual_count = count_submodules(generated_project)
        assert actual_count == expected_count, (
            f"Expected {expected_count} submodules, found {actual_count}"
        )

    def test_lightning_tune_when_hpo_enabled(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """LightningTune should be present only when use_hpo=yes."""
        submodule_names = get_submodule_names(generated_project)
        use_hpo = cookiecutter_options.get("use_hpo") == "yes"

        if use_hpo:
            assert "LightningTune" in submodule_names, (
                "LightningTune submodule not found when use_hpo=yes"
            )
        else:
            assert "LightningTune" not in submodule_names, (
                "LightningTune submodule found when use_hpo=no"
            )

    def test_dataporter_when_enabled(
        self, generated_project: Path, cookiecutter_options: dict
    ):
        """DataPorter should be present only when use_dataporter=yes."""
        submodule_names = get_submodule_names(generated_project)
        use_dataporter = cookiecutter_options.get("use_dataporter") == "yes"

        if use_dataporter:
            assert "DataPorter" in submodule_names, (
                "DataPorter submodule not found when use_dataporter=yes"
            )
        else:
            assert "DataPorter" not in submodule_names, (
                "DataPorter submodule found when use_dataporter=no"
            )

    def test_submodules_in_external_directory(self, generated_project: Path):
        """All submodules should be configured in external/ directory."""
        gitmodules = generated_project / ".gitmodules"
        content = gitmodules.read_text()

        # Every submodule path should start with external/
        for line in content.splitlines():
            if line.strip().startswith("path = "):
                path = line.split("=")[1].strip()
                assert path.startswith("external/"), (
                    f"Submodule path {path} is not in external/"
                )


class TestGitSubmoduleStatus:
    """Test that submodules are properly initialized."""

    @pytest.mark.parametrize(
        "cookiecutter_options",
        [
            pytest.param(
                {"use_hpo": "yes", "use_wandb": "yes", "use_dataporter": "yes"},
                id="all-submodules",
            ),
        ],
        indirect=True,
    )
    def test_submodule_status(self, generated_project: Path):
        """git submodule status should show all configured submodules."""
        result = subprocess.run(
            ["git", "submodule", "status"],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"git submodule status failed: {result.stderr}"

        # Should have 3 submodules (Reflow, Tune, DataPorter)
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        assert len(lines) == 3, f"Expected 3 submodules, got: {lines}"

    @pytest.mark.parametrize(
        "cookiecutter_options",
        [
            pytest.param(
                {"use_hpo": "no", "use_wandb": "no", "use_dataporter": "no"},
                id="minimal-submodules",
            ),
        ],
        indirect=True,
    )
    def test_minimal_submodule_status(self, generated_project: Path):
        """Minimal setup should have only LightningReflow submodule."""
        result = subprocess.run(
            ["git", "submodule", "status"],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"git submodule status failed: {result.stderr}"

        # Should have only 1 submodule (Reflow)
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        assert len(lines) == 1, f"Expected 1 submodule, got: {lines}"
        assert "LightningReflow" in result.stdout, "LightningReflow not in submodule status"
