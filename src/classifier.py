# src/classifier.py
# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: AI Model Integration — Teachable Machine Document Classifier
# Classifies uploaded document images before Groq analysis.
# ─────────────────────────────────────────────────────────────────────────────

import numpy as np
import io
from PIL import Image

FALLBACK_LABELS = [
    "Rental Agreement",
    "Employment Contract",
    "Terms of Service",
    "Other / Not a Document",
]

_model_cache = None
_labels_cache = None


def load_model(model_path: str = "model/keras_model.h5"):
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    try:
        import tensorflow as tf
        _model_cache = tf.keras.models.load_model(model_path, compile=False)
        return _model_cache
    except Exception:
        return None


def load_labels(labels_path: str = "model/labels.txt") -> list[str]:
    global _labels_cache
    if _labels_cache:
        return _labels_cache
    try:
        with open(labels_path, "r") as f:
            # Teachable Machine exports "0 ClassName" — strip the index
            _labels_cache = [line.strip().split(" ", 1)[-1] for line in f if line.strip()]
        return _labels_cache
    except Exception:
        return FALLBACK_LABELS


def preprocess_image(image_bytes: bytes, size: tuple = (224, 224)) -> np.ndarray:
    """Resize + normalize to [-1, 1] as Teachable Machine expects."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(size, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32)
    arr = (arr / 127.5) - 1.0
    return np.expand_dims(arr, axis=0)


def classify_document(image_bytes: bytes) -> dict:
    """
    Run the Teachable Machine model on an uploaded document image.
    Returns predicted class, confidence, and all class probabilities.
    Falls back gracefully if model is not installed.
    """
    model = load_model()
    labels = load_labels()

    if model is None:
        return {
            "predicted_class": "Model not installed",
            "confidence": 0.0,
            "all_predictions": [],
            "model_available": False,
        }

    try:
        inp = preprocess_image(image_bytes)
        preds = model.predict(inp, verbose=0)[0]
        idx = int(np.argmax(preds))

        all_preds = sorted(
            [{"label": labels[i] if i < len(labels) else f"Class {i}",
              "confidence": round(float(preds[i]) * 100, 1)}
             for i in range(len(preds))],
            key=lambda x: x["confidence"],
            reverse=True,
        )

        return {
            "predicted_class": labels[idx] if idx < len(labels) else "Unknown",
            "confidence": round(float(preds[idx]) * 100, 1),
            "all_predictions": all_preds,
            "model_available": True,
        }
    except Exception as e:
        return {
            "predicted_class": "Error",
            "confidence": 0.0,
            "all_predictions": [],
            "model_available": False,
            "error": str(e),
        }
