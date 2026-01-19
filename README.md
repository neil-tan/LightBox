# LightBox

A cookiecutter template for Lightning-based ML projects with built-in support for:
- **LightningReflow** - Pause/resume training with deterministic checkpoints
- **LightningTune** - Hyperparameter optimization with Optuna (optional)
- **DataPorter** - Data loading utilities (optional)
- **WandB** - Experiment tracking (optional)
- **pyenv virtualenv** - Automatic virtual environment setup (optional)

## Prerequisites

### Required
- **Python 3.9+**
- **cookiecutter**: `pip install cookiecutter`
- **git**: For repository initialization and submodules

### Optional (for automatic virtualenv creation)
- **pyenv**: [Installation guide](https://github.com/pyenv/pyenv#installation)
- **pyenv-virtualenv**: [Installation guide](https://github.com/pyenv/pyenv-virtualenv#installation)

Verify your setup:
```bash
pyenv --version        # pyenv 2.x.x
pyenv virtualenv --help  # Should show help, not error
```

## Quick Start

```bash
# Generate a new project
cookiecutter gh:neil-tan/LightBox
```

You'll be prompted for configuration options. Here's an example session:

```
project_name [My ML Project]: Video Prediction
project_slug [video-prediction]:
package_name [video_prediction]:
model_name [model]: vidpred
description [A Lightning-based ML project]: Video prediction with diffusion
author [Your Name]: Jane Doe
author_email [your.email@example.com]: jane@example.com
python_version [3.10]: 3.11
Select use_wandb:
1 - yes
2 - no
Choose from 1, 2 [1]: 1
Select use_hpo:
1 - yes
2 - no
Choose from 1, 2 [1]: 1
Select use_dataporter:
1 - no
2 - yes
Choose from 1, 2 [1]: 1
Select create_virtualenv:
1 - yes
2 - no
Choose from 1, 2 [1]: 1
```

If you selected `create_virtualenv: yes`, you'll then see:

```
Setting up pyenv virtualenv...

  Available Python versions:
    1. 3.12.1
    2. 3.11.7
    3. 3.10.14

  Select Python version [1-3]: 2

  Creating virtualenv 'video-prediction' with Python 3.11.7...
  Running: pyenv virtualenv 3.11.7 video-prediction
  Created .python-version for auto-activation
```

Finally:

```
  Installing project in virtualenv...
  Running: pyenv exec pip install -e .
  Project installed successfully

============================================================
Video Prediction is ready!
============================================================

Virtualenv 'video-prediction' created and will auto-activate in this directory.

Next steps:
  1. cd video-prediction
     # virtualenv auto-activates, project already installed
  2. Implement your model in video_prediction/models/base.py
  3. Implement your datamodule in video_prediction/data/datamodule.py
  4. Update configs/vidpred.yaml with your settings
  5. Run training:
     python scripts/train_vidpred.py fit --config configs/vidpred.yaml
  6. Run HPO:
     python scripts/vidpred_hpo.py --config configs/vidpred.yaml --n-trials 50
```

## Minimal Example (Non-Interactive)

```bash
cookiecutter gh:neil-tan/LightBox --no-input \
  project_name="My Model" \
  use_hpo=no \
  use_wandb=no \
  create_virtualenv=no
```

## Template Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `project_name` | Human-readable project name | "My ML Project" |
| `project_slug` | Directory name (auto-generated) | my-ml-project |
| `package_name` | Python package name (auto-generated) | my_ml_project |
| `model_name` | Base name for scripts/configs | "model" |
| `description` | Project description | "A Lightning-based ML project" |
| `author` | Author name | "Your Name" |
| `author_email` | Author email | "your.email@example.com" |
| `python_version` | Minimum Python version for pyproject.toml | "3.10" |
| `use_wandb` | Enable WandB logging | "yes" |
| `use_hpo` | Include HPO script and LightningTune | "yes" |
| `use_dataporter` | Include DataPorter submodule | "no" |
| `create_virtualenv` | Create pyenv virtualenv with auto-activation | "yes" |
| `pytest_workers` | Parallel pytest workers ("auto", "0", or number) | "auto" |

## Generated Project Structure

```
my-project/
├── my_project/               # Main Python package
│   ├── __init__.py
│   ├── paths.py              # Centralized path management
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py           # Skeleton LightningModule
│   ├── data/
│   │   ├── __init__.py
│   │   └── datamodule.py     # Skeleton LightningDataModule
│   └── hpo/                  # (if use_hpo=yes)
│       ├── __init__.py
│       └── config.py         # HPO constants
├── scripts/
│   ├── train_model.py        # Training script with LightningReflowCLI
│   └── model_hpo.py          # HPO script (if use_hpo=yes)
├── configs/
│   └── model.yaml            # Base configuration
├── tests/
│   ├── conftest.py           # Pytest fixtures
│   ├── helpers/
│   │   └── hpo_utils.py      # MockTrial for testing
│   └── test_hpo_search_space.py
├── external/                 # Git submodules (populated by hook)
│   ├── LightningReflow/
│   ├── LightningTune/        # (if use_hpo=yes)
│   └── DataPorter/           # (if use_dataporter=yes)
├── .gitignore
├── .python-version           # (if create_virtualenv=yes)
├── pyproject.toml
├── setup.py
├── requirements.txt
├── pytest.ini
└── README.md
```

## After Generation

The post-generation hook automatically:
1. Initializes a git repository
2. Adds submodules (LightningReflow, and optionally LightningTune/DataPorter)
3. Creates a pyenv virtualenv (if requested) with your chosen Python version
4. Writes `.python-version` for auto-activation on `cd`
5. Installs the project with `pip install -e .` (if virtualenv created)
6. Creates an initial commit

## Pytest Configuration

The `pytest_workers` option configures parallel test execution using `pytest-xdist`:

| Value | Behavior |
|-------|----------|
| `"auto"` | Automatically detect CPU count (recommended) |
| `"0"` or `""` | Disable parallel execution (run sequentially) |
| `"4"` | Use exactly 4 workers |

This is configured in `pytest.ini` as `-n <workers>`. Run tests with:

```bash
pytest              # Uses configured workers
pytest -n 0         # Override: run sequentially
pytest -n 8         # Override: use 8 workers
```

## Usage After Generation

```bash
cd my-project
# If virtualenv was created, it auto-activates here

pip install -e .

# Implement your model and datamodule, then train:
python scripts/train_model.py fit --config configs/model.yaml

# Run HPO (if enabled):
python scripts/model_hpo.py --config configs/model.yaml --n-trials 100
```

## Customizing Submodule URLs

Edit the `SUBMODULE_URLS` dict in `hooks/post_gen_project.py` to point to your organization's repositories:

```python
SUBMODULE_URLS = {
    "LightningReflow": "https://github.com/your-org/Reflow.git",
    "LightningTune": "https://github.com/your-org/LightningTune.git",
    "DataPorter": "https://github.com/your-org/DataPorter.git",
}
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install cookiecutter pytest

# Run e2e tests
pytest tests/ -v
```

### Test Template Locally

```bash
cookiecutter . --no-input -o /tmp/test-output
cd /tmp/test-output/my-ml-project
pip install -e .
pytest
```

## License

MIT
