from contextlib import asynccontextmanager
from time import perf_counter
from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi import FastAPI
from pydantic import BaseModel, StringConstraints
from transformers import pipeline

MODEL_ID = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.classifier = pipeline(
        "text-classification",
        model=MODEL_ID,
        device=-1,
    )
    yield


app = FastAPI(
    title="AI Inference Infrastructure Lab",
    version="0.2.0",
    lifespan=lifespan,
)


class PredictionRequest(BaseModel):
    text: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=2000,
        ),
    ]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictionRequest):
    start = perf_counter()
    result = app.state.classifier(
        request.text,
        truncation=True,
        max_length=512,
    )[0]

    return {
        "label": result["label"],
        "score": result["score"],
        "inference_ms": round((perf_counter() - start) * 1000, 2),
        "model": MODEL_ID,
        "device": "cpu",
    }
  


@app.get("/ready")
def ready():
    model_loaded = getattr(app.state, "classifier", None) is not None
    return JSONResponse(
        status_code=200 if model_loaded else 503,
        content={
            "status": "ready" if model_loaded else "not_ready",
            "model_loaded": model_loaded,
        },
    )