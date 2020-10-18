"""
LearningMachine Abstract base class definition
"""

from typing import Any, NoReturn, Sequence
from nptyping import NDArray
from numpy import float32 as float32
import torch
from abc import abstractmethod, ABC
from torch import nn, optim
from torch.utils.data.dataloader import default_collate
from pathlib import Path
import os
from torchvision.transforms import ToTensor
from datasets import Sample

# Types
Prediction = NDArray[
    (
        Any,
        7,
    ),
    float32,
]

BASE_FOLDER = Path(os.path.dirname(os.path.abspath(__file__)))
TORCH_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class LearningMachine(ABC):
    """"""

    CHECKPOINTS_FOLDER = BASE_FOLDER / "weights"

    def __init__(self) -> None:
        self._model = None
        self._weights = None
        self._transformer = self._set_transformer()

    @staticmethod
    def _set_transformer():
        """Default transformer: always convert an image to a torch tensor!"""
        return ToTensor()

    @property
    def model(self):
        if self._model is None:
            self._model = self._load_model()
            # Move model instance to the target memory location
            self._model = self._model.to(TORCH_DEVICE)
        return self._model

    @property
    @abstractmethod
    def checkpoint(self):
        pass

    @property
    @abstractmethod
    def optimiser(self) -> optim.Optimizer:
        pass

    @property
    @abstractmethod
    def criterion(self) -> nn.Module:
        pass

    @property
    def weights(self):
        if self._weights is None:
            print(f"[INFO]: loading {self.checkpoint}")
            self._weights = torch.load(self.checkpoint, map_location=TORCH_DEVICE)
        return self._weights

    @abstractmethod
    def _load_model(self):
        raise NotImplementedError("You should not instantiate a Model explicitly.")

    def transform(self, sample: Sample) -> torch.Tensor:
        return self._transformer(sample.image)

    def predict(self, samples: Sequence[Sample], as_proba: bool = True) -> Prediction:
        """

        Parameters
        ----------
        samples : Sequence[Sample]
            The Sequence of sample instances to generate predictions for
        as_proba : bool (default True)
            If True, returns predictions as probabilities. Otherwise, just
            logits will be returned

        Returns
        -------
            Numpy Array of shape (n_samples x  n_emotions)
        """
        # transform samples into a batch of torch Tensors
        batch = default_collate(list(map(self.transform, iter(samples))))
        with torch.no_grad():
            self.model.eval()
            batch = batch.to(TORCH_DEVICE)
            outputs = self.model(batch)
            outputs = outputs.detach().numpy()
            if not as_proba:
                return outputs  # return logits
            probabilities = (outputs - outputs.min(axis=1, keepdims=True)) / (
                outputs.max(axis=1, keepdims=True) - outputs.min(axis=1, keepdims=True)
            )
            probabilities /= probabilities.sum(axis=1, keepdims=True)
            return probabilities

    def fit(self, samples: Sequence[Sample]) -> NoReturn:
        """"""
        # convert the input sequence of Samples into a batch
        # of torch Tensor
        batch = default_collate(list(map(self.transform, iter(samples))))
        labels = default_collate([s.emotion for s in iter(samples)])
        with torch.set_grad_enabled(True):
            self.model.train()
            # zero the gradient
            self.optimiser.zero_grad()
            # forward pass
            batch = batch.to(TORCH_DEVICE)
            labels = labels.to(TORCH_DEVICE)
            outputs = self.model(batch)
            loss = self.criterion(outputs, labels)
            # backward + optimize
            loss.backward()
            self.optimiser.step()

    def __call__(self, samples: Sequence[Sample]) -> Prediction:
        return self.predict(samples=samples)
