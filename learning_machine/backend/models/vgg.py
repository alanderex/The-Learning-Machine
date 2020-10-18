from typing import Any

import torch
from torch import nn
from torch import optim
from torchvision.models import vgg13
from torchvision.transforms import Compose, Lambda, ToTensor
from .learning_machine import LearningMachine


class VGGNet(nn.Module):
    """Custom VGG13 model architecture"""

    def __init__(
        self, freeze: bool = False, pretrained: bool = False, n_classes: int = 7
    ):
        super(VGGNet, self).__init__()
        vgg13_architecture = vgg13(pretrained=pretrained, progress=pretrained)
        self.features = vgg13_architecture.features
        self.avgpool = vgg13_architecture.avgpool
        if freeze:
            for param in self.features.parameters():
                param.requires_grad = False
        self.classifier = nn.Sequential(
            nn.Linear(7 * 7 * 512, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 1024),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(1024, n_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

    def __call__(self, *args, **kwargs) -> Any:
        return super().__call__(*args, **kwargs)


class VGG(LearningMachine):
    """VGG-based Learning Machine"""

    def __init__(self) -> None:
        super(VGG, self).__init__()

    @staticmethod
    def _set_transformer():
        return Compose([Lambda(lambda img: img.convert("RGB")), ToTensor()])

    @property
    def checkpoint(self):
        return self.CHECKPOINTS_FOLDER / "vgg_learning_machine_overfitting.pt"

    @property
    def optimiser(self) -> optim.Optimizer:
        return optim.SGD(self.model.parameters(), lr=0.001, momentum=0.9)

    @property
    def criterion(self) -> nn.Module:
        return nn.CrossEntropyLoss()

    def _load_model(self) -> nn.Module:
        model = VGGNet(pretrained=False, freeze=False)
        model.load_state_dict(self.weights)
        return model
