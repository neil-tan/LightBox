"""Fixtures for LightBox cookiecutter template e2e tests.

Requirements:
    pip install cookiecutter pytest
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest

# Template directory (relative to this test file)
TEMPLATE_DIR = Path(__file__).parent.parent


# Option combinations for parameterized testing
# Note: create_virtualenv is always "no" in tests to avoid side effects
OPTION_COMBINATIONS = [
    pytest.param(
        {"use_hpo": "yes", "use_wandb": "yes", "use_dataporter": "yes", "create_virtualenv": "no", "pytest_workers": "auto"},
        id="hpo-wandb-dataporter",
    ),
    pytest.param(
        {"use_hpo": "yes", "use_wandb": "yes", "use_dataporter": "no", "create_virtualenv": "no", "pytest_workers": "auto"},
        id="hpo-wandb",
    ),
    pytest.param(
        {"use_hpo": "yes", "use_wandb": "no", "use_dataporter": "no", "create_virtualenv": "no", "pytest_workers": "4"},
        id="hpo-only",
    ),
    pytest.param(
        {"use_hpo": "no", "use_wandb": "yes", "use_dataporter": "no", "create_virtualenv": "no", "pytest_workers": "0"},
        id="wandb-only",
    ),
    pytest.param(
        {"use_hpo": "no", "use_wandb": "no", "use_dataporter": "no", "create_virtualenv": "no", "pytest_workers": "auto"},
        id="minimal",
    ),
]


def create_local_git_repo(path: Path, name: str) -> Path:
    """Create a minimal local git repo to serve as submodule source."""
    repo_path = path / name
    repo_path.mkdir(parents=True, exist_ok=True)

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create a minimal file and commit
    readme = repo_path / "README.md"
    readme.write_text(f"# {name}\nDummy submodule for testing.\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    return repo_path


@pytest.fixture(scope="session")
def local_submodule_repos(tmp_path_factory) -> dict[str, Path]:
    """Create local git repos to use as submodule sources (session-scoped)."""
    repos_dir = tmp_path_factory.mktemp("submodule_repos")

    repos = {}
    for name in ["LightningReflow", "LightningTune", "DataPorter"]:
        repos[name] = create_local_git_repo(repos_dir, name)

    return repos


@pytest.fixture
def patched_hook_with_local_repos(local_submodule_repos, tmp_path) -> Path:
    """
    Create a patched version of post_gen_project.py that uses local repos.

    Returns the path to the patched template directory.
    """
    # Copy the entire template to a temp location
    patched_template = tmp_path / "patched_template"
    shutil.copytree(TEMPLATE_DIR, patched_template)

    # Read and patch the hook file
    hook_path = patched_template / "hooks" / "post_gen_project.py"
    hook_content = hook_path.read_text()

    # Replace the URLs with local paths
    for name, repo_path in local_submodule_repos.items():
        old_url = f'"https://github.com/robotic-ai-core/{name.replace("Lightning", "")}.git"'
        if "Reflow" in name:
            old_url = '"https://github.com/robotic-ai-core/Reflow.git"'
        elif "Tune" in name:
            old_url = '"https://github.com/robotic-ai-core/LightningTune.git"'
        elif "DataPorter" in name:
            old_url = '"https://github.com/robotic-ai-core/DataPorter.git"'
        new_url = f'"{repo_path}"'
        hook_content = hook_content.replace(old_url, new_url)

    hook_path.write_text(hook_content)

    return patched_template


def generate_project(
    template_path: Path,
    output_dir: Path,
    options: dict,
) -> Path:
    """Generate a project from the template with given options."""
    # Import here to allow pytest.importorskip to handle the skip
    from cookiecutter.main import cookiecutter

    # Default context values
    context = {
        "project_name": "Test ML Project",
        "model_name": "testmodel",
        "description": "A test project",
        "author": "Test Author",
        "author_email": "test@example.com",
        "python_version": "3.10",
        **options,
    }

    # Generate the project
    project_path = cookiecutter(
        str(template_path),
        output_dir=str(output_dir),
        no_input=True,
        extra_context=context,
    )

    return Path(project_path)


@pytest.fixture
def generated_project(
    patched_hook_with_local_repos: Path,
    tmp_path: Path,
    cookiecutter_options: dict,
) -> Generator[Path, None, None]:
    """
    Generate a project with the given options.

    Requires the `cookiecutter_options` fixture to be provided via parametrization.
    """
    # Skip if cookiecutter is not installed
    pytest.importorskip("cookiecutter", reason="cookiecutter not installed")

    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Configure git user and allow file:// protocol for local submodules
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test User"
    env["GIT_AUTHOR_EMAIL"] = "test@example.com"
    env["GIT_COMMITTER_NAME"] = "Test User"
    env["GIT_COMMITTER_EMAIL"] = "test@example.com"
    # Allow file:// protocol for git submodule add with local repos
    # This is needed because git 2.38+ blocks file:// by default
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "protocol.file.allow"
    env["GIT_CONFIG_VALUE_0"] = "always"

    # Generate with the patched template
    with patch.dict(os.environ, env):
        project_path = generate_project(
            patched_hook_with_local_repos,
            output_dir,
            cookiecutter_options,
        )

    yield project_path

    # Cleanup is handled by pytest's tmp_path


@pytest.fixture
def cookiecutter_options(request) -> dict:
    """
    Fixture that returns cookiecutter options.

    Use with @pytest.mark.parametrize("cookiecutter_options", [...], indirect=True)
    """
    return request.param


def list_project_files(project_path: Path) -> list[Path]:
    """List all files in the generated project (excluding .git internals)."""
    files = []
    for f in project_path.rglob("*"):
        if f.is_file() and ".git" not in str(f.relative_to(project_path)).split(os.sep)[0:1]:
            files.append(f.relative_to(project_path))
    return files


def file_contains_pattern(project_path: Path, glob_pattern: str, text_pattern: str) -> bool:
    """Check if any file matching glob contains the text pattern."""
    for f in project_path.glob(glob_pattern):
        if f.is_file() and text_pattern in f.read_text():
            return True
    return False


def count_submodules(project_path: Path) -> int:
    """Count the number of submodules configured in .gitmodules."""
    gitmodules = project_path / ".gitmodules"
    if not gitmodules.exists():
        return 0
    content = gitmodules.read_text()
    return content.count("[submodule ")


def get_submodule_names(project_path: Path) -> list[str]:
    """Get list of configured submodule names from .gitmodules."""
    gitmodules = project_path / ".gitmodules"
    if not gitmodules.exists():
        return []

    content = gitmodules.read_text()
    names = []
    for line in content.splitlines():
        if line.strip().startswith("[submodule "):
            # Extract name from [submodule "external/Name"]
            name = line.split('"')[1].split("/")[-1]
            names.append(name)
    return names
