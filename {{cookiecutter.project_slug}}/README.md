# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## Installation

```bash
# Clone with submodules
git clone --recursive <your-repo-url>
cd {{cookiecutter.project_slug}}

# Install in development mode
pip install -e .
```

## Project Structure

```
{{cookiecutter.project_slug}}/
├── {{cookiecutter.package_name}}/    # Main package
│   ├── models/                       # Model implementations
│   ├── data/                         # Data loading
│   ├── hpo/                          # HPO configuration{% if cookiecutter.use_hpo == "yes" %}{% endif %}
│   └── paths.py                      # Centralized path management
├── scripts/                          # Training and HPO scripts
├── configs/                          # YAML configuration files
├── tests/                            # Test suite
└── external/                         # Git submodules
```

## Quick Start

### 1. Implement Your Model

Edit `{{cookiecutter.package_name}}/models/base.py`:
- Add your model layers in `__init__`
- Implement `forward()`, `training_step()`, and `validation_step()`

### 2. Implement Your DataModule

Edit `{{cookiecutter.package_name}}/data/datamodule.py`:
- Create your dataset class or use an existing one
- Implement `setup()` to create train/val/test datasets

### 3. Update Configuration

Edit `configs/{{cookiecutter.model_name}}.yaml` with your settings.

### 4. Train

```bash
# Basic training
python scripts/train_{{cookiecutter.model_name}}.py fit --config configs/{{cookiecutter.model_name}}.yaml

# Override settings
python scripts/train_{{cookiecutter.model_name}}.py fit --config configs/{{cookiecutter.model_name}}.yaml --trainer.max_epochs 200

# Resume from pause checkpoint
python scripts/train_{{cookiecutter.model_name}}.py resume --checkpoint-path pause_checkpoints/<file>.ckpt
```

{% if cookiecutter.use_hpo == "yes" %}
### 5. Hyperparameter Optimization

```bash
# Run HPO
python scripts/{{cookiecutter.model_name}}_hpo.py --config configs/{{cookiecutter.model_name}}.yaml --n-trials 100

# Resume interrupted study
python scripts/{{cookiecutter.model_name}}_hpo.py --config configs/{{cookiecutter.model_name}}.yaml --resume-from tmp/hpo_checkpoints

# Quick test
python scripts/{{cookiecutter.model_name}}_hpo.py --config configs/{{cookiecutter.model_name}}.yaml --n-trials 3 --trial-steps 100 --test-mode
```
{% endif %}

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov={{cookiecutter.package_name}}
```

## Environment Variables

- `{{cookiecutter.package_name.upper()}}_OUTPUT_DIR`: Override default output directory (default: `./tmp`)

## License

[Add your license here]
