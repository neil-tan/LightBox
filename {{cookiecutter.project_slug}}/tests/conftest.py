"""Pytest fixtures for {{cookiecutter.project_name}}."""

import os
import pytest
import torch


@pytest.fixture(scope="session", autouse=True)
def setup_torch():
    """Configure PyTorch for deterministic testing.

    This fixture runs once per test session and ensures:
    - CUDNN determinism
    - Fixed random seeds
    """
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)


@pytest.fixture
def device():
    """Provide appropriate device for testing."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@pytest.fixture
def deterministic_env(tmp_path):
    """Temporary deterministic environment.

    Creates a temporary output directory and sets environment variables
    to use it. Cleans up after the test.
    """
    old_env = os.environ.copy()
    os.environ["{{cookiecutter.package_name.upper()}}_OUTPUT_DIR"] = str(tmp_path)
    yield tmp_path
    os.environ.clear()
    os.environ.update(old_env)


@pytest.fixture
def small_batch_config():
    """Configuration for small batch unit tests."""
    return {
        "batch_size": 4,
        "num_workers": 0,
    }


@pytest.fixture
def realistic_batch_config():
    """Configuration for integration tests with realistic batches."""
    return {
        "batch_size": 32,
        "num_workers": 2,
    }
