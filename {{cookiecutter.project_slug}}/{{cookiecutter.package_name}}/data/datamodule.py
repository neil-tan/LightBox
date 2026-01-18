"""Data module implementation for {{cookiecutter.project_name}}.

This module provides a skeleton LightningDataModule that you can extend
with your own data loading logic.
"""

from typing import Optional

import lightning as L
from torch.utils.data import DataLoader, Dataset


class BaseDataModule(L.LightningDataModule):
    """Base data module skeleton for {{cookiecutter.project_name}}.

    TODO: Implement your data loading by:
    1. Defining your dataset class or using an existing one
    2. Implementing setup() to create train/val/test datasets
    3. Implementing the dataloader methods
    """

    def __init__(
        self,
        batch_size: int = 128,
        num_workers: int = 4,
        # TODO: Add your data-specific parameters here
    ):
        """Initialize the data module.

        Args:
            batch_size: Batch size for dataloaders
            num_workers: Number of workers for data loading
        """
        super().__init__()
        self.save_hyperparameters()

        self.batch_size = batch_size
        self.num_workers = num_workers

        # Dataset placeholders
        self.train_dataset: Optional[Dataset] = None
        self.val_dataset: Optional[Dataset] = None
        self.test_dataset: Optional[Dataset] = None

    def setup(self, stage: Optional[str] = None):
        """Setup datasets for each stage.

        Args:
            stage: Current stage ('fit', 'validate', 'test', or 'predict')

        TODO: Implement dataset creation
        """
        if stage == "fit" or stage is None:
            # TODO: Create training dataset
            # self.train_dataset = YourDataset(split="train", ...)

            # TODO: Create validation dataset
            # self.val_dataset = YourDataset(split="val", ...)
            pass

        if stage == "test" or stage is None:
            # TODO: Create test dataset
            # self.test_dataset = YourDataset(split="test", ...)
            pass

    def train_dataloader(self) -> DataLoader:
        """Create training dataloader."""
        if self.train_dataset is None:
            raise RuntimeError("train_dataset not initialized. Call setup() first.")

        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=True,
            drop_last=True,
        )

    def val_dataloader(self) -> DataLoader:
        """Create validation dataloader."""
        if self.val_dataset is None:
            raise RuntimeError("val_dataset not initialized. Call setup() first.")

        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True,
        )

    def test_dataloader(self) -> DataLoader:
        """Create test dataloader."""
        if self.test_dataset is None:
            raise RuntimeError("test_dataset not initialized. Call setup() first.")

        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True,
        )
