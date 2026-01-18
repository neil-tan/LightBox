"""HPO configuration constants for {{cookiecutter.project_name}}."""

from typing import Dict, Any, Set


class HPODefaults:
    """Default configuration values for HPO trials.

    Define model-specific defaults here that are used across HPO trials.
    These values ensure consistency and provide documentation of baseline settings.
    """
    # TODO: Define your model-specific defaults
    BATCH_SIZE = 128
    VAL_CHECK_INTERVAL = 500


# Parameters excluded from CLI command generation
# These are typically parameters that should be set differently for production training
EXCLUDED_CLI_PARAMS: Set[str] = {
    "data.init_args.batch_size",
    "trainer.val_check_interval",
}

# Production training defaults (for generating best config command)
# Override HPO trial settings with production-appropriate values
PRODUCTION_DEFAULTS: Dict[str, Any] = {
    "data.batch_size": 128,
    "data.num_workers": 16,
    "trainer.max_epochs": 2000,
}
