"""Centralized path management for {{cookiecutter.project_name}}.

This module provides standardized paths for outputs, logs, and checkpoints.
All paths can be overridden via the {{cookiecutter.package_name.upper()}}_OUTPUT_DIR environment variable.
"""

import os
from pathlib import Path

# Allow override via environment variable
OUTPUT_ROOT = Path(os.environ.get("{{cookiecutter.package_name.upper()}}_OUTPUT_DIR", "./tmp"))

# Standard output directories
LIGHTNING_LOGS = OUTPUT_ROOT / "lightning_logs"
WANDB_LOGS = OUTPUT_ROOT / "wandb_logs"
WANDB_DIR = OUTPUT_ROOT / "wandb"
PAUSE_CHECKPOINTS = OUTPUT_ROOT / "pause_checkpoints"
HPO_CHECKPOINTS = OUTPUT_ROOT / "hpo_checkpoints"
LOGS = OUTPUT_ROOT / "logs"

ALL_DIRS = [LIGHTNING_LOGS, WANDB_LOGS, WANDB_DIR, PAUSE_CHECKPOINTS, HPO_CHECKPOINTS, LOGS]


def ensure_dirs():
    """Create all output directories if they don't exist."""
    for d in ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)


def setup_environment():
    """Setup environment variables for external libraries."""
    ensure_dirs()
    os.environ.setdefault("WANDB_DIR", str(WANDB_DIR))


# Auto-setup on import
setup_environment()
