# ============================================================
# churn_api.py — Flask API for McD Sentiment Analysis
# FINAL VERSION — MATCHES main.py WORDCLOUD PIPELINE
# ============================================================

import os
import traceback
from typing import List, Dict, Any

from flask import Flask, request, jsonify
from flask_cors import CORS
from joblib import load
import re
import base64
from io import BytesIO

# WordCloud
from wordcloud import WordCloud

# --------------------------
# STOPWORDS 
# --------------------------
def get_custom_stopwords():
    sw = set(WordCloud().stopwords)
    sw.update([...])
    keep_words = {...}
    sw = sw.difference(keep_words)
    return sw

# --------------------------
# FLASK APP
# --------------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.environ.get("MODEL_DIR", os.path.join(BASE_DIR, "models"))

MODEL_FILES = {
    "SVM (Linear)":             "svm_bin_final.pkl",
    "Logistic Regression":      "logreg_bin_final.pkl",
    "Naive Bayes (Complement)": "nb_bin_final.pkl",
}

MODELS: Dict[str, Any] = {}


# --------------------------
# CLEANING FUNCTION
# --------------------------
def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip()
    s = s.lower()
    s = re.sub(r'(https?://\S+|www\.\S+)', ' ', s)
    s = re.sub(r'[@#]\w+', ' ', s)
    s = re.sub(r'\S+@\S+\.\S+', ' ', s)
    s = re.sub(r"[^0-9a-zA-Záàâäãåçéèêëíìîïñóòôöõúùûü’'\.\,\!\?\s]", " ", s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


# --------------------------
# WORDCLOUD GENERATOR 
# --------------------------
def generate_wordcloud_base64(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    wc = WordCloud(
        width=600,
        height=400,
        background_color="#fff8e1",
        collocations=False,
        stopwords=set() 
    ).generate(text)

    buf = BytesIO()
    wc.to_image().save(buf, format="PNG")
    buf.seek(0)

    return base64.b64encode(buf.read()).decode("utf-8")


# --------------------------
# LOAD MODELS
# --------------------------
def load_models() -> None:
    global MODELS
    MODELS = {}

    print(f"[INFO] Loading models from: {MODEL_DIR}")
    for name, filename in MODEL_FILES.items():
        path = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(path):
            print(f"[WARN] Model missing: {path}")
            continue

        try:
            print(f"[LOAD] {name}")
            MODELS[name] = load(path)
        except Exception as e:
            print(f"[ERR] Failed to load {name}: {e}")

    print(f"[SUMMARY] Loaded models: {list(MODELS.keys())}")


load_models()


# --------------------------
# PREDICT SAFE
# --------------------------
def predict_safe(pipe, texts: List[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        preds = pipe.predict(texts)
        out["preds"] = [str(p) for p in preds]

        if hasattr(pipe, "predict_proba"):
            probas = pipe.predict_proba(texts)
            out["probs"] = [
                {"neg": float(p[0]), "pos": float(p[1])}
                for p in probas
            ]
        else:
            out["probs"] = [None] * len(texts)

    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"
        out["trace"] = "".join(traceback.format_exc()[-800:])

    return out


# --------------------------
# ROUTES
# --------------------------
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "McD Sentiment API (SVM, LR, NB)",
        "WordCloud": "Synced with main.py",
        "endpoints": ["/", "/health", "/predict", "/selftest"]
    })


@app.route("/health", methods=["GET"])
def health():
    from sklearn import __version__ as skl_version
    return jsonify({
        "status": "ok" if MODELS else "error",
        "models_loaded": list(MODELS.keys()),
        "sklearn_version": skl_version,
        "wordcloud_stopwords": len(get_custom_stopwords()),
    })


@app.route("/predict", methods=["POST"])
def predict():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json(silent=True) or {}
    texts_raw = []

    if isinstance(data.get("text"), str):
        raw = data["text"].strip()
        if raw:
            texts_raw = [raw]

    elif isinstance(data.get("texts"), list):
        texts_raw = [t.strip() for t in data["texts"] if isinstance(t, str) and t.strip()]

    else:
        return jsonify({"error": "Invalid JSON. Use 'text' or 'texts'."}), 400

    if not texts_raw:
        return jsonify({"error": "Text must not be empty."}), 400

    if not MODELS:
        return jsonify({"error": "No models loaded."}), 503

    # CLEAN INPUT
    texts_clean = [clean_text(t) for t in texts_raw]

    responses = []
    for i, raw in enumerate(texts_raw):
        t_clean = texts_clean[i]
        per_model = []

        # Predict from all models
        for model_name, pipe in MODELS.items():
            r = predict_safe(pipe, [t_clean])
            per_model.append({
                "model": model_name,
                "pred_label": r["preds"][0] if r.get("preds") else None,
                "probs": r["probs"][0] if r.get("probs") else None
            })

        # WordCloud pakai STOPWORDS main.py
        wc_b64 = generate_wordcloud_base64(t_clean)

        responses.append({
            "input_text": raw,
            "clean_text": t_clean,
            "wordcloud": wc_b64,
            "per_model": per_model
        })

    return jsonify({
        "n_inputs": len(texts_raw),
        "results": responses
    })


@app.route("/selftest", methods=["GET"])
def selftest():
    sample = [
        "the chicken is not good, the fries are cold",
        "the service is friendly and fast"
    ]

    clean = [clean_text(s) for s in sample]
    report = {}

    for name, pipe in MODELS.items():
        report[name] = predict_safe(pipe, clean)

    return jsonify({
        "sample_raw": sample,
        "sample_clean": clean,
        "report": report
    })


# --------------------------
# MAIN ENTRY
# --------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
