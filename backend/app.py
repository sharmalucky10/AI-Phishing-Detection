"""
============================================================
  AI-Powered Phishing Detector - Flask Backend API
  Capstone Project | BCA Final Year
  File: app.py
============================================================

Endpoints:
  GET  /         - Health check
  POST /predict  - Predict if text is phishing or safe

Run: python app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
import os

# ─────────────────────────────────────────────────────────────────────────────
# INITIALIZE APP
# ─────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)  # Allow requests from Chrome extension

# ─────────────────────────────────────────────────────────────────────────────
# LOAD MODEL & VECTORIZER
# ─────────────────────────────────────────────────────────────────────────────

MODEL_PATH      = os.path.join(os.path.dirname(__file__), '..', 'model', 'phishing_model.pkl')
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'vectorizer.pkl')

print("[*] Loading ML model and vectorizer...")

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    print("[✓] Model loaded successfully!")
except FileNotFoundError:
    print("[✗] Model files not found!")
    print("    Please run: cd ../model && python train_model.py")
    model      = None
    vectorizer = None


# ─────────────────────────────────────────────────────────────────────────────
# TEXT PREPROCESSING (must match train_model.py)
# ─────────────────────────────────────────────────────────────────────────────

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', ' urltoken ', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_url_features(text):
    """Extract URL-based risk indicators from text."""
    text_lower = text.lower() if isinstance(text, str) else ""
    return {
        "has_url"              : bool(re.search(r'http[s]?://', text_lower)),
        "has_suspicious_tld"   : bool(re.search(r'\.(xyz|tk|ml|ga|cf|gq|pw|top|click|link)', text_lower)),
        "has_ip_url"           : bool(re.search(r'http[s]?://\d{1,3}\.\d{1,3}', text_lower)),
        "urgency_keywords"     : any(w in text_lower for w in [
            'urgent', 'immediately', 'expire', 'suspend', 'alert',
            'warning', 'verify', 'confirm', 'account', 'action required'
        ]),
        "money_keywords"       : any(w in text_lower for w in [
            'won', 'prize', 'reward', 'free', 'gift', 'claim', 'refund', 'approved', '$'
        ]),
        "exclamation_count"    : text.count('!'),
    }


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status"       : "running",
        "message"      : "AI Phishing Detector API is active",
        "model_loaded" : model is not None,
        "version"      : "1.0.0"
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint.
    
    Request body (JSON):
        { "text": "email or message text here" }
    
    Response (JSON):
        {
            "prediction"  : "phishing" | "safe",
            "confidence"  : 0.0 - 100.0,
            "risk_level"  : "HIGH" | "MEDIUM" | "LOW",
            "risk_factors": [...],
            "message"     : "human-readable result"
        }
    """
    # ── Validate model loaded ──
    if model is None or vectorizer is None:
        return jsonify({
            "error": "Model not loaded. Run train_model.py first."
        }), 500

    # ── Parse request ──
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({
            "error": "Missing 'text' field in request body."
        }), 400

    text = data.get('text', '').strip()
    if not text:
        return jsonify({
            "error": "Text cannot be empty."
        }), 400

    # ── Preprocess & predict ──
    cleaned   = preprocess_text(text)
    features  = vectorizer.transform([cleaned])
    
    prediction = model.predict(features)[0]
    proba      = model.predict_proba(features)[0]
    confidence = round(float(proba[prediction]) * 100, 2)

    # ── Determine risk level ──
    if prediction == 1:
        if confidence >= 80:
            risk_level = "HIGH"
        elif confidence >= 60:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
    else:
        risk_level = "SAFE"

    # ── Identify risk factors ──
    url_features = extract_url_features(text)
    risk_factors = []
    
    if url_features["has_url"]:
        risk_factors.append("Contains URL link")
    if url_features["has_suspicious_tld"]:
        risk_factors.append("Suspicious domain extension (.xyz, .tk, .ml, etc.)")
    if url_features["has_ip_url"]:
        risk_factors.append("URL contains raw IP address")
    if url_features["urgency_keywords"]:
        risk_factors.append("Uses urgency/threat language")
    if url_features["money_keywords"]:
        risk_factors.append("Contains money/reward bait")
    if url_features["exclamation_count"] > 1:
        risk_factors.append(f"Excessive exclamation marks ({url_features['exclamation_count']})")

    # ── Build response ──
    result_label = "phishing" if prediction == 1 else "safe"
    
    if prediction == 1:
        message = f"⚠️ PHISHING DETECTED — This message appears to be a phishing attempt. Do not click any links or provide personal information."
    else:
        message = f"✅ SAFE — This message appears to be legitimate."

    response = {
        "prediction"  : result_label,
        "confidence"  : confidence,
        "risk_level"  : risk_level,
        "risk_factors": risk_factors,
        "message"     : message,
        "text_length" : len(text)
    }

    print(f"[PREDICT] Result: {result_label.upper()} ({confidence}%) | Length: {len(text)} chars")
    return jsonify(response), 200


@app.route('/predict', methods=['OPTIONS'])
def predict_options():
    """Handle CORS preflight requests from Chrome extension."""
    return '', 200


# ─────────────────────────────────────────────────────────────────────────────
# RUN SERVER
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Phishing Detector API")
    print("  Running on: http://127.0.0.1:5000")
    print("  Press CTRL+C to stop")
    print("=" * 50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
