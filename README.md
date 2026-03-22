# 🛡️ AI-Powered Phishing Detection System

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?style=flat-square&logo=scikit-learn)](https://scikit-learn.org)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-yellow?style=flat-square&logo=googlechrome)](https://developer.chrome.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> **BCA Final Year Capstone Project** — An AI-powered browser extension that detects phishing emails and messages in real time using Machine Learning trained on 82,486 real emails.

---

## 📊 Model Performance

| Model | Accuracy | ROC-AUC | CV (5-fold) |
|---|---|---|---|
| Multinomial Naive Bayes | 95.50% | 0.9947 | 90.51% |
| Logistic Regression | 98.12% | 0.9979 | 95.44% |
| **Random Forest ✅ (Selected)** | **98.58%** | **0.9987** | **94.20%** |
| Gradient Boosting | 94.27% | 0.9853 | 88.52% |

**Confusion Matrix (Random Forest on 20,622 test emails):**
```
True Negatives  (Safe correctly identified)    : 9,742
False Positives (Safe flagged as Phishing)     : 157
False Negatives (Phishing missed)              : 135
True Positives  (Phishing correctly detected)  : 10,588
```

**Classification Report:**
```
              precision    recall  f1-score   support
        Safe       0.99      0.98      0.99      9,899
    Phishing       0.99      0.99      0.99     10,723
    accuracy                           0.99     20,622
```

---

## 📌 What is this project?

Phishing is one of the biggest cybersecurity threats today — over **3.4 billion phishing emails** are sent every day. Traditional spam filters often miss new and clever phishing attacks.

This project solves that problem using **Artificial Intelligence**:

- Paste any suspicious email or message
- The AI instantly tells you if it's **PHISHING** or **SAFE**
- Shows confidence percentage and risk factors
- Works directly inside your Chrome browser

---

## 🎯 Features

- 🔍 **Text Analysis** — Paste any email, SMS or message and detect phishing instantly
- 🌐 **Page Scanner** — Scan any webpage for phishing content
- 📊 **Confidence Score** — See how confident the AI is (e.g. 93% phishing)
- ⚠️ **Risk Factors** — Shows WHY something is flagged (suspicious URL, urgency words etc.)
- 📋 **Scan History** — Keeps track of your last 10 scans
- 🟢 **API Status** — Live indicator showing if the backend is connected

---

## 🏗️ System Architecture

```
User pastes text in Extension
        ↓
popup.js sends HTTP POST to Flask API
        ↓
app.py preprocesses text (clean + TF-IDF)
        ↓
Random Forest model predicts (98.58% accuracy)
        ↓
Returns: phishing/safe + confidence % + risk factors
        ↓
Extension shows RED 🚨 or GREEN ✅ result
```

---

## 🤖 Machine Learning Pipeline

```
Raw Email Text
      ↓
Preprocessing (lowercase, remove URLs → urltoken, remove special chars)
      ↓
TF-IDF Vectorization (bigrams, 5000 features, sublinear TF)
      ↓
Random Forest Classifier (100 trees, n_jobs=-1)
      ↓
Prediction + Confidence Score
```

---

## 🗂️ Dataset

- **Size:** 82,486 labeled emails (42,891 phishing + 39,595 safe)
- **Source:** Phishing Email Dataset — Kaggle
- **Train/Test Split:** 75% train (61,864) / 25% test (20,622)

> 📥 **Download:** Get `phishing_email.csv` from Kaggle and place it in the `/dataset/` folder before running `train_model.py`
> The dataset file is not included in this repo due to GitHub's 100MB file size limit.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| ML Model | Python, scikit-learn, Random Forest |
| NLP | TF-IDF Vectorizer (bigrams, 5000 features) |
| Backend | Flask, flask-cors |
| Serialization | Pickle |
| Frontend | HTML, CSS, JavaScript |
| Browser | Chrome Extension API (Manifest V3) |

---

## 📁 Project Structure

```
AI-Phishing-Detection/
│
├── model/
│   └── train_model.py          # Train ML model and save as .pkl
│
├── backend/
│   ├── app.py                  # Flask REST API server
│   └── requirements.txt        # Python dependencies
│
├── extension/
│   ├── manifest.json           # Chrome extension config
│   ├── popup.html              # Extension UI
│   ├── popup.js                # Extension logic
│   ├── content.js              # Page scanner script
│   └── icons/                  # Extension icons
│
├── dataset/
│   └── phishing_email.csv      # ⚠️ Download from Kaggle (not in repo)
│
├── .gitignore
└── README.md
```

---

## ⚙️ How to Run

### Step 1 — Clone the repository
```bash
git clone https://github.com/sharmalucky10/AI-Phishing-Detection.git
cd AI-Phishing-Detection
```

### Step 2 — Download the dataset
Download `phishing_email.csv` from Kaggle and place it in the `/dataset/` folder.

### Step 3 — Install Python dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4 — Train the AI model
```bash
cd model
python train_model.py
```

Training takes ~15-20 minutes on first run. This generates:
- `model/phishing_model.pkl`
- `model/vectorizer.pkl`

### Step 5 — Start the Flask server
```bash
cd ../backend
python app.py
```

Server starts at: `http://127.0.0.1:5000`

### Step 6 — Load the Chrome Extension
1. Open Chrome → go to `chrome://extensions`
2. Enable **Developer Mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `extension/` folder
5. Click the 🛡️ shield icon in your toolbar

---

## 🧪 Test the Extension

**Phishing test** (should show 🚨 RED):
```
URGENT: Your account has been suspended! Verify immediately at http://paypal-secure.xyz/verify or your account will be deleted!
```

**Safe test** (should show ✅ GREEN):
```
Hi John, please find the meeting notes attached. See you tomorrow at 10 AM. Best regards, Sarah
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check — returns model status |
| POST | `/predict` | Predict phishing or safe |

**POST /predict — Request:**
```json
{
  "text": "URGENT: Your account is suspended!"
}
```

**POST /predict — Response:**
```json
{
  "prediction": "phishing",
  "confidence": 93.4,
  "risk_level": "HIGH",
  "risk_factors": ["Suspicious TLD detected", "Urgency language found"]
}
```

---

## 🔮 Future Improvements

- Deploy Flask API to cloud (AWS / Render) for public access
- Upgrade to BERT deep learning model for higher accuracy
- Gmail API integration for automatic inbox scanning
- Hindi and regional language phishing detection
- VirusTotal API integration for URL reputation checking
- Admin analytics dashboard

---

## 👤 Author

**Lucky Sharma**

- 📧 sharmalucky0581@gmail.com
- 🔗 [LinkedIn](https://linkedin.com/in/lucky-sharma-923523341/)
- 💻 [GitHub](https://github.com/sharmalucky10)

---

## 📜 License

This project is licensed under the MIT License.

---

> ⭐ If you found this project useful, please give it a star on GitHub!
