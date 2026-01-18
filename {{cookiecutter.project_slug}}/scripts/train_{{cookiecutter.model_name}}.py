#!/usr/bin/env python
"""
{{cookiecutter.project_name}} Training Script using LightningReflowCLI.

This script provides pause/resume functionality and maintains deterministic training.

Usage:
    # Training with config
    python scripts/train_{{cookiecutter.model_name}}.py fit --config configs/{{cookiecutter.model_name}}.yaml

    # Override trainer settings
    python scripts/train_{{cookiecutter.model_name}}.py fit --config configs/{{cookiecutter.model_name}}.yaml --trainer.max_steps 1000

    # Resume from checkpoint
    python scripts/train_{{cookiecutter.model_name}}.py fit --config configs/{{cookiecutter.model_name}}.yaml --ckpt_path <path>

    # Resume from pause checkpoint
    python scripts/train_{{cookiecutter.model_name}}.py resume --checkpoint-path pause_checkpoints/<file>.ckpt
"""

import sys
from pathlib import Path

import torch

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lightning_reflow import LightningReflowCLI
from {{cookiecutter.package_name}}.models import BaseModel
from {{cookiecutter.package_name}}.data import BaseDataModule


def main():
    """Main training entry point using LightningReflowCLI."""
    # Set CUDNN settings for determinism (must be set BEFORE any CUDA operations)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # Initialize LightningReflowCLI
    # Seeding is handled by the CLI via config's seed_everything or seed_everything_default
    cli = LightningReflowCLI(
        BaseModel,
        BaseDataModule,
        auto_configure_optimizers=False,  # Model handles optimizer configuration
        seed_everything_default=42,  # Deterministic by default
        subclass_mode_model=True,  # Allow nested config instantiation
        subclass_mode_data=True,  # Allow nested config instantiation
        run=True,  # Start training immediately
    )


if __name__ == "__main__":
    main()
