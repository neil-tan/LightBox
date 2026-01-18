"""Base model implementation for {{cookiecutter.project_name}}.

This module provides a skeleton LightningModule that you can extend
with your own architecture.
"""

from typing import Any, Dict

import lightning as L
import torch
import torch.nn as nn


class BaseModel(L.LightningModule):
    """Base model skeleton for {{cookiecutter.project_name}}.

    TODO: Implement your model architecture by:
    1. Adding layers in __init__
    2. Implementing forward()
    3. Implementing training_step() and validation_step()
    4. Optionally customizing configure_optimizers()
    """

    def __init__(
        self,
        learning_rate: float = 1e-4,
        weight_decay: float = 1e-5,
        # TODO: Add your model-specific parameters here
    ):
        """Initialize the model.

        Args:
            learning_rate: Learning rate for optimizer
            weight_decay: Weight decay for optimizer
        """
        super().__init__()
        self.save_hyperparameters()

        self.learning_rate = learning_rate
        self.weight_decay = weight_decay

        # TODO: Define your model layers here
        # Example:
        # self.encoder = nn.Sequential(...)
        # self.decoder = nn.Sequential(...)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Input tensor

        Returns:
            Model output tensor

        TODO: Implement your forward pass
        """
        raise NotImplementedError("Implement forward() in your model subclass")

    def training_step(self, batch: Any, batch_idx: int) -> torch.Tensor:
        """Training step.

        Args:
            batch: Batch of training data
            batch_idx: Index of the batch

        Returns:
            Training loss

        TODO: Implement your training logic
        """
        raise NotImplementedError("Implement training_step() in your model subclass")

    def validation_step(self, batch: Any, batch_idx: int) -> torch.Tensor:
        """Validation step.

        Args:
            batch: Batch of validation data
            batch_idx: Index of the batch

        Returns:
            Validation loss

        TODO: Implement your validation logic
        """
        raise NotImplementedError("Implement validation_step() in your model subclass")

    def configure_optimizers(self) -> Dict[str, Any]:
        """Configure optimizer and learning rate scheduler.

        Returns:
            Optimizer configuration dict
        """
        optimizer = torch.optim.AdamW(
            self.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay,
        )

        # TODO: Optionally add learning rate scheduler
        # scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)
        # return {"optimizer": optimizer, "lr_scheduler": scheduler}

        return {"optimizer": optimizer}
