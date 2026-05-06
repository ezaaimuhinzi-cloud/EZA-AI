import os
import json
import threading
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

from database import init_db
from routers import auth, scan, diseases, subscription, admin

# ── AI model (kept here for /predict — HF Space compatibility) ────

model = None
class_names = {}
_loading = False
_load_error = None


def _do_load():
    global model, class_names, _loading, _load_error
    model_path = "eza_ai_model.h5"
    if not os.path.exists(model_path):
        _loading = False
        return  # No model file — running as pure API backend

    try:
        with open("class_names.json") as f:
            class_names = {int(k): v for k, v in json.load(f).items()}

        import tensorflow as tf

        class _CompatInputLayer(tf.keras.layers.InputLayer):
            @classmethod
            def from_config(cls, config):
                config = config.copy()
                if "batch_shape" in config:
                    config["batch_input_shape"] = config.pop("batch_shape")
                config.pop("optional", None)
                return super().from_config(config)

        tf.config.set_visible_devices([], "GPU")
        m = tf.keras.models.load_model(
            model_path, compile=False,
            custom_objects={"InputLayer": _CompatInputLayer},
        )
        m.predict(np.zeros((1, 224, 224, 3), dtype=np.float32), verbose=0)
        model = m
        print(f"✅ Model ready. Classes: {len(class_names)}")
    except Exception as e:
        _load_error = str(e)
        print(f"❌ Model load failed: {e}")
    finally:
        _loading = False


_CROP_CLASSES = {
    "Corn": [0, 1, 2, 3],
    "Pepper": [4, 5],
    "Potato": [6, 7, 8],
    "Tomato": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
}


# ── App lifecycle ─────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Init DB tables
    await init_db()
    # Load AI model in background if file present
    global _loading
    _loading = True
    threading.Thread(target=_do_load, daemon=True).start()
    yield


app = FastAPI(
    title="EZA AI Backend",
    description="Rwanda's AI plant disease detection platform API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers (all under /api/v1) ───────────────────────────────────

PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(scan.router, prefix=PREFIX)
app.include_router(diseases.router, prefix=PREFIX)
app.include_router(subscription.router, prefix=PREFIX)
app.include_router(admin.router, prefix=PREFIX)


# ── Root / Health ─────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "EZA AI Backend",
        "version": "1.0.0",
        "status": "running",
        "model_loaded": model is not None,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"ok": True, "model_loaded": model is not None,
            "loading": _loading, "error": _load_error}


# ── /predict — kept for HF Space compatibility ────────────────────

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    crop_filter: Optional[str] = Form(None),
):
    if model is None:
        if _loading:
            raise HTTPException(503, "Model loading, please retry in 30 seconds")
        elif _load_error:
            raise HTTPException(500, f"Model failed to load: {_load_error}")
        else:
            raise HTTPException(503, "Model not ready — no model file on this instance")

    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB").resize((224, 224))
    arr = (np.array(img, dtype=np.float32) / 127.5) - 1.0
    arr = np.expand_dims(arr, 0)

    preds = model.predict(arr, verbose=0)[0]
    if crop_filter and crop_filter in _CROP_CLASSES:
        masked = np.full(len(preds), -np.inf)
        for i in _CROP_CLASSES[crop_filter]:
            masked[i] = preds[i]
        idx = int(np.argmax(masked))
    else:
        idx = int(np.argmax(preds))

    confidence = float(preds[idx])
    label = class_names.get(idx, "Unknown")
    parts = label.split("___")
    crop_raw = parts[0]
    disease_raw = parts[1] if len(parts) > 1 else "healthy"
    is_healthy = "healthy" in disease_raw.lower()

    return {
        "label": label,
        "confidence": confidence,
        "cropRaw": crop_raw,
        "diseaseRaw": disease_raw,
        "isHealthy": is_healthy,
    }
