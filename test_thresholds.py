import sys
sys.path.insert(0, '.')
from srd.predict import predict_url
import pickle
import numpy as np
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# Load TF-IDF and model
tfidf = pickle.load(open("model/tfidf.pkl", "rb"))
model = pickle.load(open("model/final_model.pkl", "rb"))

# Test URLs
test_urls = [
    "https://www.google.com",
    "https://www.amazon.com",
    "https://www.facebook.com",
    "http://example.com",
    "http://a.com",
    "http://phishing-site.com",
    "http://secure-bank-verify.com",
    "http://fake-paypal-login.com",
    "http://199.19.13.99",
    "http://tiny.cc/xyz",
]

# Extract features and get probabilities
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

print("URL Probabilities:")
print("=" * 70)
for url in test_urls:
    X_tfidf = tfidf.transform([url])
    url_feat = np.array([extract_url_features(url)])
    X_base = hstack([X_tfidf, url_feat])
    
    # Add visual feature (0 for now)
    visual_features = np.array([[0]])
    X_final = hstack([X_base, visual_features]).tocsr()
    
    # Align features
    expected = model.n_features_in_
    current = X_final.shape[1]
    if current < expected:
        diff = expected - current
        X_final = hstack([X_final, np.zeros((1, diff))]).tocsr()
    elif current > expected:
        X_final = X_final[:, :expected]
    
    proba = model.predict_proba(X_final)[0]
    prob_phishing = proba[1]
    
    print(f"{url:45} -> Phishing: {prob_phishing:.4f}")

print("\n" + "=" * 70)
print("Find a threshold that works for you based on the above probabilities")
