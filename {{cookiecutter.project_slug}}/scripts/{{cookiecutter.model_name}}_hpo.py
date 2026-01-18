#!/usr/bin/env python
"""
Hyperparameter Optimization for {{cookiecutter.project_name}} using LightningTune.

This script supports:
- Multiple hyperparameter search strategies (TPE, Random, CMA-ES)
- Pruning strategies (Median, Hyperband)
- Pause/resume from checkpoints
- WandB integration

Usage:
    # Start HPO
    python scripts/{{cookiecutter.model_name}}_hpo.py --config configs/{{cookiecutter.model_name}}.yaml --n-trials 100

    # With WandB logging
    python scripts/{{cookiecutter.model_name}}_hpo.py --config configs/{{cookiecutter.model_name}}.yaml --n-trials 100 --wandb my-project

    # Resume from checkpoint
    python scripts/{{cookiecutter.model_name}}_hpo.py --config configs/{{cookiecutter.model_name}}.yaml --resume-from latest

    # Quick test
    python scripts/{{cookiecutter.model_name}}_hpo.py --config configs/{{cookiecutter.model_name}}.yaml --n-trials 3 --trial-steps 100 --test-mode
"""

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import paths early to set environment variables (WANDB_DIR, etc.)
import {{cookiecutter.package_name}}.paths  # noqa: F401

from LightningTune import HPORunner
from {{cookiecutter.package_name}}.models import BaseModel
from {{cookiecutter.package_name}}.data import BaseDataModule
from {{cookiecutter.package_name}}.hpo import EXCLUDED_CLI_PARAMS, PRODUCTION_DEFAULTS


def search_space(trial, config):
    """Define the search space for {{cookiecutter.project_name}} HPO.

    This function modifies the config dict with sampled hyperparameters.

    Best practices (see LightningTune README for details):
    - Always use copy.deepcopy(config) at the start
    - Get references to nested dicts for clean assignment
    - Return the modified config

    Args:
        trial: Optuna trial object for sampling
        config: Base configuration dict (will be deep copied)

    Returns:
        Modified configuration dict with sampled hyperparameters
    """
    # CRITICAL: Deep copy to avoid side effects between trials
    config = copy.deepcopy(config)

    # Get references for clean assignment
    model = config["model"]["init_args"]
    data = config["data"]["init_args"]

    # =========================================================================
    # TODO: Define your search space below
    # =========================================================================

    # Example: Learning rate (log scale)
    model["learning_rate"] = trial.suggest_float("lr", 1e-5, 1e-3, log=True)

    # Example: Weight decay
    model["weight_decay"] = trial.suggest_float("weight_decay", 1e-6, 1e-3, log=True)

    # Example: Batch size (categorical)
    data["batch_size"] = trial.suggest_categorical("batch_size", [64, 128, 256])

    # Example: Architecture choice (uncomment and customize)
    # architecture = trial.suggest_categorical("architecture", ["small", "medium", "large"])
    # if architecture == "small":
    #     model["hidden_dim"] = 256
    # elif architecture == "medium":
    #     model["hidden_dim"] = 512
    # else:
    #     model["hidden_dim"] = 1024

    return config


# Initialize HPO Runner
runner = HPORunner(
    model_class=BaseModel,
    datamodule_class=BaseDataModule,
    search_space=search_space,
    require_config=True,
    default_study_name="{{cookiecutter.model_name}}_hpo",
)


if __name__ == "__main__":
    from {{cookiecutter.package_name}}.paths import HPO_CHECKPOINTS

    # Inject default --experiment-dir if not provided
    if "--experiment-dir" not in sys.argv:
        sys.argv.extend(["--experiment-dir", str(HPO_CHECKPOINTS)])

    # Disable Lightning checkpointing during HPO to avoid accumulating .ckpt files
    # (study.pkl for resume is still saved by LightningTune)
    if "--trainer.enable_checkpointing" not in " ".join(sys.argv):
        sys.argv.extend(["--trainer.enable_checkpointing", "false"])

    # Use MedianPruner by default (less aggressive, good for multi-architecture search)
    if "--pruner" not in sys.argv:
        sys.argv.extend(["--pruner", "median"])

    # Run HPO
    study = runner.run_from_cli()

    # Print results
    print("\n" + runner.format_results(study))
    print("\nTo train with best hyperparameters:")
    print("-" * 60)
    print(runner.generate_best_config_command(
        study,
        script="python scripts/train_{{cookiecutter.model_name}}.py fit",
        extra_args=PRODUCTION_DEFAULTS,
        excluded_params=EXCLUDED_CLI_PARAMS,
    ))

    # Print resume command
    config_file = next((sys.argv[i+1] for i, arg in enumerate(sys.argv)
                       if arg == "--config" and i+1 < len(sys.argv)), None)
    experiment_dir = next((sys.argv[i+1] for i, arg in enumerate(sys.argv)
                          if arg == "--experiment-dir" and i+1 < len(sys.argv)), None)

    if config_file and experiment_dir:
        print("\nTo resume this study:")
        print("-" * 60)
        print(f"python scripts/{{cookiecutter.model_name}}_hpo.py --config {config_file} --resume-from {experiment_dir}")
