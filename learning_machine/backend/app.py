"""
FastAPI Main App
"""
import uvicorn
from fastapi import FastAPI
from endpoints import faces, get_emotion_face, annotate
from fastapi.middleware.cors import CORSMiddleware

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

faces = learning_machine_backend.get("/faces/{number_of_faces}/")(faces)
get_emotion_face = learning_machine_backend.get("/faces/image/{image_id}")(
    get_emotion_face
)
annotate = learning_machine_backend.post("/faces/annotate/")(annotate)

if __name__ == "__main__":
    uvicorn.run(learning_machine_backend, host="127.0.0.1", port=8000)
