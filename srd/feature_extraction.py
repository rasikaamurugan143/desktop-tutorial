import pandas as pd
import numpy as np
import re
import pickle
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from scipy.sparse import hstack

# -----------------------------
# CREATE MODEL FOLDER IF NOT EXISTS
# -----------------------------
os.makedirs("model", exist_ok=True)

# -----------------------------
# LOAD DATASET
# -----------------------------
print("Loading dataset...")
df = pd.read_csv("C:/Users/rasik/OneDrive/Desktop/phishing_project/data/phishing_dataset.csv")
# Clean dataset
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

print("Dataset Loaded:", df.shape)

# PREVENT DATA LEAKAGE: Split BEFORE fitting TF-IDF
print("Splitting train/test (80/20)...")
df_train, df_test = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])
print(f"Train: {len(df_train)}, Test: {len(df_test)}")

# Save train URLs indices for visual similarity computation
train_indices = df_train.index.tolist()
test_indices = df_test.index.tolist()

# -----------------------------
# URL FEATURE EXTRACTION
# -----------------------------
def extract_url_features(url):
    return [
        len(url),
        url.count('.'),
        url.count('-'),
        url.count('@'),
        url.count('/'),
        url.count('?'),
        url.count('='),
        1 if "https" in url else 0,
        1 if re.match(r"\d+\.\d+\.\d+\.\d+", url) else 0,
        int(any(word in url.lower() for word in [
            "login", "verify", "bank", "secure", "account", "update"
        ]))
    ]

print("Extracting URL features...")

url_features_train = np.array([extract_url_features(u) for u in df_train['url']])
url_features_test = np.array([extract_url_features(u) for u in df_test['url']])

# ⚠️ FIT TFIDF ONLY ON TRAINING DATA (prevent data leakage)
print("Applying TF-IDF...")

tfidf = TfidfVectorizer(
    analyzer='char',
    ngram_range=(3, 5),
    max_features=5000
)

# FIT on train, TRANSFORM on train and test
X_tfidf_train = tfidf.fit_transform(df_train['url'])
X_tfidf_test = tfidf.transform(df_test['url'])

print(f"✅ TF-IDF Train shape: {X_tfidf_train.shape}, Test shape: {X_tfidf_test.shape}")

# ⚠️ COMBINE FEATURES - TRAIN AND TEST SEPARATELY
print("Combining features...")

X_base_train = hstack([X_tfidf_train, url_features_train])
X_base_test = hstack([X_tfidf_test, url_features_test])
y_train = df_train['label'].values
y_test = df_test['label'].values

print("✅ Train Feature shape:", X_base_train.shape)
print("✅ Test Feature shape:", X_base_test.shape)

# -----------------------------
# SAVE FILES
# -----------------------------
print("Saving feature files...")

with open("model/tfidf.pkl", "wb") as f:
    pickle.dump(tfidf, f)

# Save train/test split for proper model evaluation
with open("model/X_base_train.pkl", "wb") as f:
    pickle.dump(X_base_train, f)

with open("model/X_base_test.pkl", "wb") as f:
    pickle.dump(X_base_test, f)

with open("model/y_train.pkl", "wb") as f:
    pickle.dump(y_train, f)

with open("model/y_test.pkl", "wb") as f:
    pickle.dump(y_test, f)

# Save train URLs for visual similarity computation
with open("model/train_indices.pkl", "wb") as f:
    pickle.dump(train_indices, f)

with open("model/train_urls.pkl", "wb") as f:
    pickle.dump(df_train['url'].values, f)

print("Saved:")
print("   - model/tfidf.pkl")
print("   - model/X_base_train.pkl")
print("   - model/X_base_test.pkl")
print("   - model/y_train.pkl")
print("   - model/y_test.pkl")
print("   - model/train_indices.pkl")
print("   - model/train_urls.pkl")

print("Feature extraction completed successfully!")