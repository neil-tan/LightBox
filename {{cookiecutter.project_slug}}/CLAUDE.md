# CLAUDE.md

This file provides guidance to Claude Code when working with this LightBox-generated project.

## Project Overview

{{cookiecutter.project_name}} is a Lightning-based ML project using:
- **LightningReflow** (`external/LightningReflow`) - Pause/resume training
- **LightningTune** (`external/LightningTune`) - HPO with Optuna{% if cookiecutter.use_dataporter == "yes" %}
- **DataPorter** (`external/DataPorter`) - Multi-dataset loading{% endif %}

## Commands

### Training
```bash
python scripts/train_{{cookiecutter.model_name}}.py fit --config configs/{{cookiecutter.model_name}}.yaml
python scripts/train_{{cookiecutter.model_name}}.py resume --checkpoint-path pause_checkpoints/<file>.ckpt
```
{% if cookiecutter.use_hpo == "yes" %}
### HPO
```bash
python scripts/{{cookiecutter.model_name}}_hpo.py --config configs/{{cookiecutter.model_name}}.yaml --n-trials 100
python scripts/{{cookiecutter.model_name}}_hpo.py --config configs/{{cookiecutter.model_name}}.yaml --resume-from tmp/hpo_checkpoints
```
{% endif %}
### Testing
```bash
pytest                      # All tests
pytest --cov={{cookiecutter.package_name}}  # With coverage
pytest -k "test_name"       # Specific test
pytest -m gpu               # GPU tests only
```

### Formatting
```bash
black {{cookiecutter.package_name}} scripts tests
isort {{cookiecutter.package_name}} scripts tests
```

## Architecture

- `{{cookiecutter.package_name}}/models/base.py` - Base LightningModule
- `{{cookiecutter.package_name}}/data/datamodule.py` - Base LightningDataModule
- `{{cookiecutter.package_name}}/hpo/config.py` - HPO configuration
- `{{cookiecutter.package_name}}/paths.py` - Centralized path management
- `configs/{{cookiecutter.model_name}}.yaml` - Main configuration
- `.claude/skills/lightbox/SKILL.md` - LightBox integration skill

## LightBox Integration

For detailed guidance on LightningReflow, LightningTune, and DataPorter integration patterns, pitfalls, and solutions, use the `/lightbox` skill:

```
/lightbox
```

This covers:
- TorchCompileCallback configuration (critical memory leak avoidance)
- HPO search space patterns
- DataPorter MultiDatasetModule setup
- Common pitfalls and debugging tips

## Test Markers

- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.gpu` - GPU-required tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.unit` - Unit tests

## Code Style

- Line length: 100 (black/isort configured in pyproject.toml)
- Python {{cookiecutter.python_version}}+
- Exclude `external/`, `tmp/` from formatting
