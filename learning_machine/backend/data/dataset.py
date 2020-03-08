"""
Export Torch Dataset to interact with Face/Emotion data.
"""
from pandas import read_csv as pd_read_csv
from torch.utils.data import Dataset
from os import path as os_path
import numpy as np
from dataclasses import dataclass

try:
    from transforms import Reshape, ToTorchTensor
except ImportError:
    from .transforms import Reshape, ToTorchTensor

DATA_FOLDER = os_path.join(os_path.abspath(os_path.dirname(__file__)))


# =================
# Sample Data Class
# =================


@dataclass
class Sample:
    EMOTION_MAP = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}

    pixels: str
    set: str
    emotion: int
    _array: np.ndarray = None

    @property
    def image(self):
        if self._array is None:
            self._array = np.fromstring(self.pixels, dtype=np.uint8, sep=' ')
        return self._array

    @image.setter
    def image(self, new_image: np.ndarray):
        self._array = new_image

    @property
    def emotion_label(self):
        return self.EMOTION_MAP[self.emotion]

    def to_json(self):
        return {'image': self.pixels, 'emotion': int(self.emotion),
                'emotion_label': self.emotion_label, 'set': self.set}

    def __str__(self):
        s_json = self.to_json()
        s_json['image'] = '... (len: {})'.format(len(self.pixels))
        return str(s_json)

    def __repr__(self):
        return self.__str__()


# ========
# Dataset
# ========

class KaggleDataset(Dataset):
    """Torch Dataset for the Kaggle
    Facial Emotion Recognition Challenge"""

    IMAGE_HEIGHT = 48
    IMAGE_WIDTH = 48

    def __init__(self, set=None, transform=None):
        """"""
        super(KaggleDataset, self).__init__()
        if set is not None and set not in ('training', 'validation', 'test'):
            set = None  # fall back to the default value
            # all data are returned, so the whole dataset!
        self._ds_mode = set
        self._transform = transform

        self._dataset_path = os_path.join(DATA_FOLDER, 'fer2013', 'fer2013', 'fer2013.csv')
        self._dataset_archive_path = os_path.join(DATA_FOLDER, 'fer2013', 'fer2013.tar.gz')
        self._data_df = self._load_data()

    def _load_data(self):
        if not os_path.exists(self._dataset_path):
            self._extract_tar_package()
        df = pd_read_csv(self._dataset_path)
        df['set'] = df.Usage.apply(
            lambda v: 'training' if v == 'Training' else 'validation' if v == 'PrivateTest' else 'test')
        if self._ds_mode:
            # filter the data frame based on the target "usage" subset
            target_df = df[df['set'] == self._ds_mode]
            target_df.reset_index(inplace=True)
            return target_df[['emotion', 'pixels', 'set']]
        return df[['emotion', 'pixels', 'set']]

    def _extract_tar_package(self):
        """"""
        import tarfile
        try:
            file = tarfile.open(self._dataset_archive_path, mode='r:gz')
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
        pixels = self._data_df.pixels[index]
        emotion = self._data_df.emotion[index]
        set = self._data_df.set[index]
        sample = Sample(pixels=pixels, emotion=emotion, set=set)
        if self._transform:
            sample = self._transform(sample)
        return sample


if __name__ == '__main__':
    from matplotlib import pyplot as plt
    from torch.utils.data import DataLoader

    from torchvision.transforms import Compose
    from functools import partial

    text_annotation = partial(plt.text, x=36, y=46, fontdict={'color': 'red', 'fontsize': 10, 'ha': 'center',
                                                              'va': 'center',
                                                              'bbox': dict(boxstyle="round", fc="white",
                                                                           ec="black", pad=0.2)})
    transformers_pipeline = Compose([
        Reshape(shape=(KaggleDataset.IMAGE_WIDTH, KaggleDataset.IMAGE_HEIGHT)),
        ToTorchTensor(), ]
    )
    dataset = KaggleDataset(set='validation', transform=transformers_pipeline)
    print('Nr. of Samples: ', len(dataset))

    kaggle_data_loader = DataLoader(dataset, batch_size=4, collate_fn=lambda b: b)
    dataiter = iter(kaggle_data_loader)
    for i, batch in enumerate(dataiter):
        for sample in batch:
            img, emotion = sample.image, sample.emotion
            plt.imshow(img[0, ...], interpolation='bilinear', cmap=plt.cm.get_cmap('gray'))
            text_annotation(s=sample.emotion_label)
            plt.axis('off')
            plt.show()
        if i > 2:
            break
