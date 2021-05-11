"""
This package provides access to all the datasets available to the learning machine.
"""

from .fer import FER
from .sources import load_fer_dataset_lazy, load_fer_training_lazy
from .sources import DataSource, Sample


# Available Dataset Keys
FER_DATASET = "FER"
FER_TRAINING = "FER_TRAIN"

DATASETS_PROXY = {
    FER_DATASET: load_fer_dataset_lazy(),
    FER_TRAINING: load_fer_training_lazy(),
}


def get_dataset(key: str) -> DataSource:
    """
    Instantiate a DataSource object depending on the selected
    torch Dataset

    Parameters
    ----------
    key : str
        A key for the DataSource Proxy map

    Returns
    -------
    DataSource
        DataSource instance associated to the selected key.

    Raises
    ------
    ValueError
        Raised if the input key is not found in the DataSets proxy map.
    """
    try:
        data_source = DATASETS_PROXY[key]
    except KeyError:
        raise ValueError(f"Invalid Dataset Key: {key}")
    else:
        return data_source


__all__ = [
    "FER",
    "DataSource",
    "FER_DATASET",
    "DATASETS_PROXY",
    "get_dataset",
    "Sample",
]
