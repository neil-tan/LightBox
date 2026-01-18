# LightBox

A cookiecutter template for Lightning-based ML projects with built-in support for:
- **LightningReflow** - Pause/resume training with deterministic checkpoints
- **LightningTune** - Hyperparameter optimization with Optuna (optional)
- **DataPorter** - Data loading utilities (optional)
- **WandB** - Experiment tracking (optional)

## Quick Start

```bash
# Install cookiecutter
pip install cookiecutter

# Generate a new project (interactive)
cookiecutter gh:your-username/LightBox

# Or with defaults
cookiecutter gh:your-username/LightBox --no-input project_name="Video Prediction"
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
| `python_version` | Minimum Python version | "3.10" |
| `use_wandb` | Enable WandB logging | "yes" |
| `use_hpo` | Include HPO script and config | "yes" |
| `use_dataporter` | Include DataPorter submodule | "no" |

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
3. Creates an initial commit

## Usage After Generation

```bash
cd my-project
pip install -e .

# Implement your model and datamodule
# Then train:
python scripts/train_model.py fit --config configs/model.yaml

# Run HPO (if enabled):
python scripts/model_hpo.py --config configs/model.yaml --n-trials 100
```

## Customizing Submodule URLs

Edit the `SUBMODULE_URLS` dict in `hooks/post_gen_project.py` to point to your organization's repositories.

## Development

```bash
# Test template generation locally
cd LightBox
cookiecutter . --no-input -o /tmp/test-output

# Verify generated project
cd /tmp/test-output/my-ml-project
pip install -e .
pytest
```

## License

[Add your license here]
