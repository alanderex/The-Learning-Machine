"""
Export Torch Dataset to interact with Face/Emotion data.
"""

from pandas import read_csv as pd_read_csv
from torch.utils.data import Dataset
from torch import from_numpy
from os import path as os_path
import numpy as np

DATA_FOLDER = os_path.join(os_path.abspath(os_path.curdir), "data")


# =============
# Transformers
# =============


class Reshape:
    """Reshape the Image (as ndarray and raveled) into a H x W x C image"""

    def __init__(self, shape):
        if len(shape) == 2:
            # add channel
            shape = shape + (1,)
        self._shape = shape

    def __call__(self, sample):
        imgage, emotion = sample["image"], sample["emotion"]

        if imgage.ndim == 2:  # no channel is provided
            imgage = imgage[..., np.newaxis]
        imgage = imgage.reshape(self._shape)
        return {"image": imgage, "emotion": emotion}


class ToTensor:
    """Convert ndarrays in sample to Tensors."""

    def __call__(self, sample):
        image, emotion = sample["image"], sample["emotion"]

        # swap color axis because
        # numpy image: H x W x C
        # torch image: C X H X W
        image = image.transpose((2, 0, 1))
        return {"image": from_numpy(image), "emotion": emotion}


# ========
# Dataset
# ========


class KaggleDataset(Dataset):
    """Torch Dataset for the Kaggle
    Facial Emotion Recognition Challenge"""

    EMOTION_MAP = {
        0: "Angry",
        1: "Disgust",
        2: "Fear",
        3: "Happy",
        4: "Sad",
        5: "Surprise",
        6: "Neutral",
    }
    IMAGE_HEIGHT = 48
    IMAGE_WIDTH = 48

    def __init__(self, dataset="training", transform=None):
        """"""
        super(KaggleDataset, self).__init__()
        if dataset not in ("training", "validation", "test"):
            dataset = "training"  # fall back to the default value
        self._ds_mode = dataset
        self._transform = transform

        self._dataset_path = os_path.join(
            DATA_FOLDER, "fer2013", "fer2013", "fer2013.csv"
        )
        self._dataset_archive_path = os_path.join(
            DATA_FOLDER, "fer2013", "fer2013.tar.gz"
        )
        self._data_df = self._load_data()

    def _load_data(self):
        if not os_path.exists(self._dataset_path):
            self._extract_tar_package()
        df = pd_read_csv(self._dataset_path)
        df["set"] = df.Usage.apply(
            lambda v: "training"
            if v == "Training"
            else "validation"
            if v == "PrivateTest"
            else "test"
        )
        # filter the data frame based on the target "usage" subset
        target_df = df[df["set"] == self._ds_mode]
        target_df.reset_index(inplace=True)
        return target_df[["emotion", "pixels"]]

    def _extract_tar_package(self):
        """"""
        import tarfile

        try:
            file = tarfile.open(self._dataset_archive_path, mode="r:gz")
            try:
                file.extractall()
            finally:
                file.close()
        except FileNotFoundError as fnf_exp:
            raise fnf_exp
        else:
            file.close()

    def __len__(self):
        return len(self._data_df)

    def __getitem__(self, index):
        sample = self._data_df.pixels[index]
        emotion = self._data_df.emotion[index]
        img = np.fromstring(sample, dtype=np.uint8, sep=" ")
        sample = {"image": img, "emotion": emotion}
        if self._transform:
            sample = self._transform(sample)
        return sample


if __name__ == "__main__":

    from matplotlib import pyplot as plt
    from torch.utils.data import DataLoader
    from torchvision.transforms import Compose
    from functools import partial

    text_annotation = partial(
        plt.text,
        x=36,
        y=46,
        fontdict={
            "color": "red",
            "fontsize": 10,
            "ha": "center",
            "va": "center",
            "bbox": dict(boxstyle="round", fc="white", ec="black", pad=0.2),
        },
    )
    transformers_pipeline = Compose(
        [
            Reshape(shape=(KaggleDataset.IMAGE_WIDTH, KaggleDataset.IMAGE_HEIGHT)),
            ToTensor(),
        ]
    )
    dataset = KaggleDataset(dataset="validation", transform=transformers_pipeline)
    print("Nr. of Samples: ", len(dataset))

    kaggle_data_loader = DataLoader(dataset, batch_size=4)
    dataiter = iter(kaggle_data_loader)
    for i, batch in enumerate(dataiter):
        samples, labels = batch["image"], batch["emotion"]
        for img, emotion in zip(samples, labels):
            emotion = emotion.item()
            plt.imshow(img[0, ...], interpolation="bilinear", cmap=plt.cm.gray)
            text_annotation(s=KaggleDataset.EMOTION_MAP[emotion])
            plt.axis("off")
            plt.show()
        if i > 2:
            break
