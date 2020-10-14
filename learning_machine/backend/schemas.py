"""Schema definitions for ReSTful APIs based on `pydantic`"""

from pydantic import BaseModel
from typing import List


class EmotionLinks(BaseModel):
    angry: float
    disgust: float
    fear: float
    happy: float
    sad: float
    surprise: float
    neutral: float


class Image(BaseModel):
    id: str
    data: str
    links: EmotionLinks


class BackendResponse(BaseModel):
    session_id: str
    nodes: List[Image]


class Annotation(BaseModel):
    image_id: str
    label: str
