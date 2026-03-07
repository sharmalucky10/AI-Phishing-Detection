"""
============================================================
  AI-Powered Phishing Detector - Model Training Script
  Capstone Project | BCA Final Year
  File: train_model.py
============================================================

This script:
  1. Loads the phishing email dataset
  2. Preprocesses the text using NLP techniques
  3. Extracts features using TF-IDF vectorization
  4. Trains and evaluates multiple ML models
  5. Selects the best model and saves it with pickle

Run: python train_model.py
"""

import pandas as pd
import numpy as np
import pickle
import os
import re
import string
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, roc_auc_score
)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: LOAD DATASET
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("  AI Phishing Detector - Model Training")
print("=" * 60)

# Path to dataset
DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'phishing_dataset.csv')

print("\n[1/6] Loading dataset...")
df = pd.read_csv(DATASET_PATH)
print(f"      Total samples loaded : {len(df)}")
print(f"      Phishing emails      : {len(df[df['label'] == 'phishing'])}")
print(f"      Safe emails          : {len(df[df['label'] == 'safe'])}")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: TEXT PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def preprocess_text(text):
    """
    Clean and normalize text for NLP processing.
    Steps:
      - Convert to lowercase
      - Remove URLs
      - Remove punctuation
      - Remove extra whitespace
      - Keep numbers (they are informative in phishing context)
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove URLs (but flag their presence is done via features)
    text = re.sub(r'http\S+|www\S+', ' urltoken ', text)
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


print("\n[2/6] Preprocessing text...")
df['cleaned_text'] = df['text'].apply(preprocess_text)
df['label_binary'] = df['label'].map({'phishing': 1, 'safe': 0})

print("      Sample preprocessed text:")
print(f"      BEFORE: {df['text'].iloc[0][:80]}...")
print(f"      AFTER : {df['cleaned_text'].iloc[0][:80]}...")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: FEATURE EXTRACTION (TF-IDF)
# ─────────────────────────────────────────────────────────────────────────────

print("\n[3/6] Extracting TF-IDF features...")

# TF-IDF Vectorizer
# - ngram_range=(1,2): captures both single words and 2-word phrases
# - max_features=5000 : top 5000 most informative terms
# - sublinear_tf=True : apply log normalization to term frequency
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=5000,
    sublinear_tf=True,
    stop_words='english'
)

X = vectorizer.fit_transform(df['cleaned_text'])
y = df['label_binary']

print(f"      Feature matrix shape : {X.shape}")
print(f"      Vocabulary size      : {len(vectorizer.vocabulary_)}")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: SPLIT DATA
# ─────────────────────────────────────────────────────────────────────────────

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print(f"\n      Training samples     : {X_train.shape[0]}")
print(f"      Testing samples      : {X_test.shape[0]}")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: TRAIN & COMPARE MODELS
# ─────────────────────────────────────────────────────────────────────────────

print("\n[4/6] Training and comparing multiple models...")
print("-" * 60)

models = {
    "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
    "Logistic Regression"    : LogisticRegression(C=1.0, max_iter=1000, random_state=42),
    "Random Forest"          : RandomForestClassifier(n_estimators=100, random_state=42),
    "Gradient Boosting"      : GradientBoostingClassifier(n_estimators=100, random_state=42),
}

results = {}

for name, model in models.items():
    # Train
    model.fit(X_train, y_train)
    
    # Predict
    y_pred = model.predict(X_test)
    
    # Metrics
    accuracy  = accuracy_score(y_test, y_pred)
    roc_auc   = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    
    results[name] = {
        'model'    : model,
        'accuracy' : accuracy,
        'roc_auc'  : roc_auc,
        'cv_mean'  : cv_scores.mean(),
        'cv_std'   : cv_scores.std(),
        'y_pred'   : y_pred,
    }
    
    print(f"\n  Model       : {name}")
    print(f"  Accuracy    : {accuracy * 100:.2f}%")
    print(f"  ROC-AUC     : {roc_auc:.4f}")
    print(f"  CV (5-fold) : {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 100:.2f}%)")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: SELECT BEST MODEL & DETAILED REPORT
# ─────────────────────────────────────────────────────────────────────────────

# Select best by ROC-AUC score
best_name = max(results, key=lambda k: results[k]['roc_auc'])
best      = results[best_name]

print("\n" + "=" * 60)
print(f"  Best Model: {best_name}")
print(f"  Accuracy  : {best['accuracy'] * 100:.2f}%")
print(f"  ROC-AUC   : {best['roc_auc']:.4f}")
print("=" * 60)

print(f"\n[5/6] Detailed report for best model ({best_name}):")
print("-" * 60)
print(classification_report(y_test, best['y_pred'], target_names=['Safe', 'Phishing']))

print("Confusion Matrix:")
cm = confusion_matrix(y_test, best['y_pred'])
print(f"  True Negatives  (Safe correctly identified)    : {cm[0][0]}")
print(f"  False Positives (Safe flagged as Phishing)     : {cm[0][1]}")
print(f"  False Negatives (Phishing missed)              : {cm[1][0]}")
print(f"  True Positives  (Phishing correctly detected)  : {cm[1][1]}")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: SAVE MODEL & VECTORIZER
# ─────────────────────────────────────────────────────────────────────────────

print("\n[6/6] Saving model and vectorizer...")

model_dir = os.path.dirname(__file__)
model_path      = os.path.join(model_dir, 'phishing_model.pkl')
vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')

with open(model_path, 'wb') as f:
    pickle.dump(best['model'], f)

with open(vectorizer_path, 'wb') as f:
    pickle.dump(vectorizer, f)

print(f"      Model saved      : {model_path}")
print(f"      Vectorizer saved : {vectorizer_path}")


# ─────────────────────────────────────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("  Quick Prediction Test")
print("=" * 60)

def predict(text, model, vectorizer):
    cleaned  = preprocess_text(text)
    features = vectorizer.transform([cleaned])
    pred     = model.predict(features)[0]
    proba    = model.predict_proba(features)[0]
    label    = "🚨 PHISHING" if pred == 1 else "✅ SAFE"
    confidence = proba[pred] * 100
    return label, confidence

test_cases = [
    "URGENT: Your account has been suspended! Verify at http://paypal-secure.xyz/verify now",
    "Hi John, please find the meeting notes attached. See you tomorrow at 10 AM.",
    "Congratulations! You won $10,000. Click http://prize-winner.tk/claim to collect",
    "Your Amazon order #112-3821928 has shipped. Track it at amazon.com/orders",
    "ALERT: Your bank account will be closed. Update details: http://bank-update.ml",
]

for text in test_cases:
    label, confidence = predict(text, best['model'], vectorizer)
    print(f"\n  Input : {text[:65]}...")
    print(f"  Result: {label} ({confidence:.1f}% confidence)")

print("\n" + "=" * 60)
print("  Training complete! Files saved in /model/ folder.")
print("  Next step: cd ../backend && python app.py")
print("=" * 60)
