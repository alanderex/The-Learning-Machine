""""""
from models import get_model
from settings import MODEL_NAME
from torchvision.transforms import Compose, ToTensor, Lambda
from schemas import Image, EmotionLinks
from random import choices, sample
from datasets import FER
import numpy as np
from models import load_vgg
import torch
from fastapi import FastAPI
from io import BytesIO
from fastapi.responses import StreamingResponse, RedirectResponse
from dataclasses import dataclass
from PIL.Image import Image as PILImage
import json

from fastapi.middleware.cors import CORSMiddleware


learning_machine_backend = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8282",
    "http://127.0.0.1:8282",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

learning_machine_backend.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fer_train = FER(root=".", download=True, split="train")
fer_validation = FER(root=".", download=True, split="validation")

datasets = {"train": fer_train, "valid": fer_validation}


@dataclass
class ImageData:
    img_id: str
    emotion: int
    image: PILImage  # PIL Image


# @learning_machine_backend.get("/faces/")
# async def faces():
#     return RedirectResponse("/faces/25")


@learning_machine_backend.get("/faces/{number_of_faces}/")
async def faces(number_of_faces: int = 25):
    model = get_model(MODEL_NAME)
    images = list()
    for _ in range(number_of_faces):
        dataset_choice = choices(list(datasets.keys()), k=1)[0]
        dataset = datasets[dataset_choice]
        img_index = sample(range(len(dataset)), k=1)[0]
        image_id = f"{dataset_choice}_{img_index}"
        image, emotion = dataset[img_index]
        img_data = ImageData(img_id=image_id, emotion=emotion, image=image)
        images.append(img_data)
    transformer = Compose([Lambda(lambda img: img.convert("RGB")), ToTensor()])
    returned_images = list()
    classes = datasets["train"].classes
    with torch.no_grad():
        model.eval()
        pred_emotions = list()
        for img_data in images:
            image = transformer(img_data.image)
            image = torch.unsqueeze(image, 0)
            pred = model(image)
            pred = pred.detach().numpy()[0]
            preds_dict = {k: v for k, v in zip(classes, pred)}
            print(preds_dict)
            emotion_links = EmotionLinks(**preds_dict)
            pred_emotions.append(emotion_links)
    for image, prediction in zip(images, pred_emotions):
        img_url = f"/faces/image/{image.img_id}"
        json_image = Image(id=image.img_id, data=img_url, links=prediction)
        returned_images.append(json_image.dict())
    return json.dumps(returned_images)


@learning_machine_backend.get("/faces/image/{image_id}")
def get_emotion_face(image_id: str):
    # TODO: adapt to image_id
    dst, index = image_id.split("_")
    dataset = datasets[dst]
    print(image_id, dst, index)
    image, _ = dataset[int(index)]
    buffer = BytesIO()
    image.save(buffer, format="png")
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="image/png",
    )


# @learning_machine_backend.post("")
# def update_emotions():
#     model = get_model(MODEL_NAME)
