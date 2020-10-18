""""""
from io import BytesIO
from typing import Sequence, List
import uvicorn
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from datasets import Sample, get_dataset
from models import get_model
from models.learning_machine import Prediction
from schemas import Node, EmotionLink, BackendResponse, Annotation
from settings import LEARNING_MACHINE_MODEL, DATASET_NAME

learning_machine_backend = FastAPI()


origins = [
    "http://localhost",
    "http://localhost:8282",
    "http://localhost:8000",
    "http://127.0.0.1:8282",
    "http://127.0.0.1:8000",
    "http://localhost:63342",
]

learning_machine_backend.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def make_nodes(
    samples: Sequence[Sample], emotions: Prediction, classes: Sequence[str]
) -> List[Node]:
    nodes = list()
    for sample, emotion in zip(samples, emotions):
        emotion_map = {c: p for c, p in zip(classes, emotion)}
        emotion_map.pop("neutral")
        norm = sum(emotion_map.values())
        emotion_map = {c: v / norm for c, v in emotion_map.items()}
        links = [
            EmotionLink(source=sample.uuid, value=prob, target=emotion)
            for emotion, prob in emotion_map.items()
        ]
        node = Node(
            id=sample.uuid,
            image=f"http://localhost:8000/faces/image/{sample.uuid}",
            links=links,
        )
        nodes.append(node)
    return nodes


@learning_machine_backend.get("/faces/{number_of_faces}/")
async def faces(number_of_faces: int = 25):
    machine = get_model(LEARNING_MACHINE_MODEL)
    dataset = get_dataset(DATASET_NAME)
    samples = dataset.get_random_samples(k=number_of_faces)
    emotions = machine.predict(samples=samples)
    nodes = make_nodes(samples, emotions, dataset.emotions)
    response = BackendResponse(nodes=nodes)
    return response.dict()


@learning_machine_backend.get("/faces/image/{image_id}")
async def get_emotion_face(image_id: str):
    dataset = get_dataset(DATASET_NAME)
    sample = dataset[image_id]
    image = sample.image
    buffer = BytesIO()
    image.save(buffer, format="png")
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="image/png",
    )


@learning_machine_backend.post("/faces/annotate/")
async def annotate(annotation: Annotation):
    dataset = get_dataset(DATASET_NAME)
    machine = get_model(LEARNING_MACHINE_MODEL)
    annotated_sample = dataset[annotation.image_id]
    # TODO: this should go in the DB too!!
    annotated_sample.emotion = dataset.emotion_index(annotation.label)
    other_samples = [dataset[nid] for nid in annotation.current_nodes]
    other_samples += dataset.get_random_samples(k=annotation.new_nodes)
    machine.fit((annotated_sample,))
    updated_emotions = machine.predict(samples=other_samples)
    nodes = make_nodes(other_samples, updated_emotions, dataset.emotions)
    response = BackendResponse(nodes=nodes)
    return response.dict()


if __name__ == "__main__":
    uvicorn.run(learning_machine_backend, host="127.0.0.1", port=8000)
