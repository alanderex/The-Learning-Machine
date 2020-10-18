"""
Specify Data sources used to proxy access to available Torch Datasets
"""

from dataclasses import dataclass
from torch.utils.data import Dataset, ConcatDataset
from datasets.fer import FER
from typing import Callable, Sequence, Union
from PIL.Image import Image as PILImage
from random import sample
from hashlib import sha256
from os import path

SECRET_SPICE = "supersecrectspiceonthebackend"


@dataclass
class Sample:
    index: int
    emotion: int
    image: PILImage

    @property
    def emotion_label(self):
        return FER.classes_map()[self.emotion]

    @property
    def uuid(self) -> str:
        encode_s = f"{SECRET_SPICE}_{self.emotion}"
        encode_b = sha256(bytes(encode_s, encoding="utf8")).hexdigest()
        ref = hex(self.index)[2:]  # getting rid of 0x
        uuid = f"{encode_b}_{ref}"
        return uuid

    def __hash__(self) -> int:
        return int(self.uuid, base=16)

    def __iter__(self):
        return iter((self,))

    @staticmethod
    def retrieve_index(uuid: str) -> int:
        try:
            _, ref = uuid.split("_")
            return int(ref, base=16)
        except ValueError:
            return -1


DatasetLoadFn = Callable[[], Dataset]


def default_load_fer_dataset() -> Dataset:
    default_root_folder = path.dirname(path.abspath(__file__))
    fer_train = FER(root=default_root_folder, download=True, split="train")
    fer_valid = FER(root=default_root_folder, download=True, split="validation")
    fer_test = FER(root=default_root_folder, download=True, split="test")
    return ConcatDataset([fer_train, fer_valid, fer_test])


def only_fer_training() -> Dataset:
    default_root_folder = path.dirname(path.abspath(__file__))
    return FER(root=default_root_folder, download=True, split="train")


class DataSource:
    def __init__(
        self,
        dataset_load_fn: DatasetLoadFn = default_load_fer_dataset,
        target_emotions: Sequence[str] = FER.classes,
    ) -> None:
        self._dataset = None  # Instantiated once via property
        self._ds_load_fn = dataset_load_fn
        self._items_sampled = set()  # implementing memory-map
        self._emotions = target_emotions

    @property
    def dataset(self) -> Dataset:
        if self._dataset is None:
            self._dataset = self._ds_load_fn()
        return self._dataset

    @property
    def emotions(self) -> Sequence[str]:
        return self._emotions

    def emotion_index(self, emotion_label: str) -> int:
        try:
            idx = self._emotions.index(emotion_label)
        except ValueError:
            idx = -1
        return idx

    def __getitem__(self, index: Union[str, int]) -> Sample:
        try:
            index = int(index)
        except ValueError:
            index = Sample.retrieve_index(str(index))
        image, label = self.dataset[index]
        return Sample(index=index, emotion=label, image=image)

    def get_random_samples(self, k: int) -> Sequence[Sample]:
        samples = list()
        pool = set(range(len(self.dataset))).difference(self._items_sampled)
        rnd_indices = sample(pool, k=k)
        for sample_idx in rnd_indices:
            samples.append(self[sample_idx])
            self._items_sampled.add(sample_idx)
        return samples


def load_fer_dataset_lazy() -> DataSource:
    """Instantiate a DataSource instance, proxying access to
    corresponding torch.Dataset.

    The DataSource lazy connects to the mapped dataset, holding
    reference to the database, and establishing actual connection
    only on the first instance access.
    """
    return DataSource()  # default load function


def load_fer_training_lazy() -> DataSource:
    """Instantiate a DataSource instance, proxying access to
    corresponding torch.Dataset.

    The DataSource lazy connects to the mapped dataset, holding
    reference to the database, and establishing actual connection
    only on the first instance access.
    """
    return DataSource(dataset_load_fn=only_fer_training)  # default load function
