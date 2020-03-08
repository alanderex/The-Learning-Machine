import numpy as np
from torch import from_numpy


# =============
# Transformers
# =============


class Reshape:
    """Reshape the Image (as ndarray and raveled) into a H x W x C image"""

    def __init__(self, shape=(48, 48)):
        self._shape = shape

    def __call__(self, sample):
        image = sample.image
        sample.image = image.reshape(self._shape)
        return sample


class ToTorchTensor:
    """Convert ndarrays in sample to torch Tensors."""

    def __call__(self, sample):
        # swap color axis because
        # numpy image: H x W x C
        # torch image: C X H X W
        image = sample.image
        if image.ndim == 2:  # no channel is provided
            image = image[np.newaxis, ...]  # channel first
        else:  # 3D
            if image.shape[0] != 1:  # it is not channel first yet.
                image = image.transpose((2, 0, 1))
        sample.image = from_numpy(image)
        return sample
