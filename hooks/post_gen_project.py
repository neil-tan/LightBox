#!/usr/bin/env python
"""Post-generation hook to setup git and submodules."""

import subprocess
import shutil
from pathlib import Path

USE_HPO = "{{cookiecutter.use_hpo}}" == "yes"
USE_WANDB = "{{cookiecutter.use_wandb}}" == "yes"
USE_DATAPORTER = "{{cookiecutter.use_dataporter}}" == "yes"

# Hardcoded submodule URLs (update these to match your organization)
SUBMODULE_URLS = {
    "LightningReflow": "https://github.com/robotic-ai-core/Reflow.git",
    "LightningTune": "https://github.com/robotic-ai-core/LightningTune.git",
    "DataPorter": "https://github.com/robotic-ai-core/DataPorter.git",
}


def run(cmd, check=True):
    """Run a shell command and print it."""
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, capture_output=True, text=True)
    if result.returncode != 0 and result.stderr:
        print(f"  Warning: {result.stderr}")
    return result


def main():
    print("\n" + "=" * 60)
    print("Setting up {{cookiecutter.project_name}}...")
    print("=" * 60)

    # Initialize git repository
    print("\nInitializing git repository...")
    run(["git", "init"])

    # Add submodules
    print("\nAdding git submodules...")

    # LightningReflow is always required
    run(["git", "submodule", "add", SUBMODULE_URLS["LightningReflow"], "external/LightningReflow"])

    if USE_HPO:
        run(["git", "submodule", "add", SUBMODULE_URLS["LightningTune"], "external/LightningTune"])

    if USE_DATAPORTER:
        run(["git", "submodule", "add", SUBMODULE_URLS["DataPorter"], "external/DataPorter"])

    # Remove HPO-related files if not using HPO
    if not USE_HPO:
        print("\nRemoving HPO files (use_hpo=no)...")
        hpo_script = Path("scripts/{{cookiecutter.model_name}}_hpo.py")
        if hpo_script.exists():
            hpo_script.unlink()
            print(f"  Removed {hpo_script}")

        hpo_dir = Path("{{cookiecutter.package_name}}/hpo")
        if hpo_dir.exists():
            shutil.rmtree(hpo_dir)
            print(f"  Removed {hpo_dir}")

        helpers_dir = Path("tests/helpers")
        if helpers_dir.exists():
            shutil.rmtree(helpers_dir)
            print(f"  Removed {helpers_dir}")

        hpo_test = Path("tests/test_hpo_search_space.py")
        if hpo_test.exists():
            hpo_test.unlink()
            print(f"  Removed {hpo_test}")

    # Note about WandB
    if not USE_WANDB:
        print("\nNote: WandB logging disabled. Logger section removed from config.")

    # Create initial commit
    print("\nCreating initial commit...")
    run(["git", "add", "."])
    run(["git", "commit", "-m", "Initial commit from LightBox template"])

    # Print success message
    print("\n" + "=" * 60)
    print("{{cookiecutter.project_name}} is ready!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. cd {{cookiecutter.project_slug}}")
    print("  2. pip install -e .")
    print("  3. Implement your model in {{cookiecutter.package_name}}/models/base.py")
    print("  4. Implement your datamodule in {{cookiecutter.package_name}}/data/datamodule.py")
    print("  5. Update configs/{{cookiecutter.model_name}}.yaml with your settings")
    print("  6. Run training:")
    print("     python scripts/train_{{cookiecutter.model_name}}.py fit --config configs/{{cookiecutter.model_name}}.yaml")
    if USE_HPO:
        print("  7. Run HPO:")
        print("     python scripts/{{cookiecutter.model_name}}_hpo.py --config configs/{{cookiecutter.model_name}}.yaml --n-trials 50")
    print()


if __name__ == "__main__":
    main()
