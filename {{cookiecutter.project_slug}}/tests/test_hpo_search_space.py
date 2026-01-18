"""Tests for HPO search space configuration."""

import copy
import pytest
import yaml

from tests.helpers import MockTrial


class TestSearchSpace:
    """Tests for the HPO search space function."""

    @pytest.fixture
    def base_config(self):
        """Load base configuration for testing."""
        with open("configs/{{cookiecutter.model_name}}.yaml") as f:
            return yaml.safe_load(f)

    def test_search_space_returns_valid_config(self, base_config):
        """Test that search_space returns a valid configuration dict."""
        from scripts.{{cookiecutter.model_name}}_hpo import search_space

        trial = MockTrial()
        config = search_space(trial, base_config)

        # Verify structure
        assert "model" in config
        assert "data" in config
        assert "init_args" in config["model"]
        assert "init_args" in config["data"]

    def test_search_space_does_not_modify_base_config(self, base_config):
        """Test that search_space uses deepcopy and doesn't modify original."""
        from scripts.{{cookiecutter.model_name}}_hpo import search_space

        original_lr = base_config["model"]["init_args"]["learning_rate"]
        original_config = copy.deepcopy(base_config)

        trial = MockTrial()
        search_space(trial, base_config)

        # Base config should be unchanged
        assert base_config["model"]["init_args"]["learning_rate"] == original_lr
        assert base_config == original_config

    def test_search_space_applies_sampled_values(self, base_config):
        """Test that sampled values are applied to the config."""
        from scripts.{{cookiecutter.model_name}}_hpo import search_space

        trial = MockTrial()
        config = search_space(trial, base_config)

        # Verify sampled values are in the config
        model_args = config["model"]["init_args"]
        data_args = config["data"]["init_args"]

        # Check that at least some values were sampled
        assert len(trial.params) > 0

        # Check that sampled values match what's in config
        if "lr" in trial.params:
            assert model_args["learning_rate"] == trial.params["lr"]
        if "batch_size" in trial.params:
            assert data_args["batch_size"] == trial.params["batch_size"]
