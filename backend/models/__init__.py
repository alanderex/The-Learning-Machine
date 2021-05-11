from .vgg import VGGMachine
from .unet import UNetMachine
from .learning_machine import LearningMachine

VGG_MODEL = "vgg"
UNET_MODEL = "unet"
MODELS_PROXY = {VGG_MODEL: VGGMachine(), UNET_MODEL: UNetMachine()}


def get_model(key: str) -> LearningMachine:
    """
    Instantiate a Learning Machine Model given a key for Models Proxy.

    Parameters
    ----------
    key : str
        A model proxy key

    Returns
    -------
    LearningMachine
        Instance of Machine subclass implementing the learning machine.
        This is basically a torch.nn.Module subclass, with unified API for an
        easier integration with ReSTful endpoints.

    Raises
    ------
    ValueError
        Raised if input key is not valid. No default fall-back model implemented.
    """
    try:
        net = MODELS_PROXY[key]
    except KeyError:
        raise ValueError(f"Invalid Model Key: {key}")
    else:
        return net
