import pickle
import numpy as np
from scipy.sparse import hstack
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# CRITICAL: USE PRE-SPLIT DATA TO AVOID DATA LEAKAGE
# Load properly split train/test data (TF-IDF fitted ONLY on train)
print("Loading pre-split features (NO DATA LEAKAGE)...")

X_base_train = pickle.load(open(
    r"C:\Users\rasik\OneDrive\Desktop\phishing_project\model\X_base_train.pkl", "rb"))
X_base_test = pickle.load(open(
    r"C:\Users\rasik\OneDrive\Desktop\phishing_project\model\X_base_test.pkl", "rb"))

y_train = pickle.load(open(
    r"C:\Users\rasik\OneDrive\Desktop\phishing_project\model\y_train.pkl", "rb"))
y_test = pickle.load(open(
    r"C:\Users\rasik\OneDrive\Desktop\phishing_project\model\y_test.pkl", "rb"))

# Load visual scores (optional - may skip for now)
try:
    visual_scores = pickle.load(open(
        r"C:\Users\rasik\OneDrive\Desktop\phishing_project\model\visual_scores.pkl", "rb"))
    visual_scores = np.array(visual_scores)
    print(f"Visual scores loaded: {len(visual_scores)} scores for training data")
except:
    print("WARNING: visual_scores.pkl not found - skipping visual features")
    visual_scores = None

# ALIGN VISUAL SCORES (only if available)
if visual_scores is not None:
    print("Adding visual features...")
    # Visual scores are computed ONLY for training data
    full_visual_train = np.array(visual_scores).reshape(-1, 1)
    
    # Ensure alignment
    if len(full_visual_train) != X_base_train.shape[0]:
        print(f"Visual scores length ({len(full_visual_train)}) != Train data ({X_base_train.shape[0]}))")
        if len(full_visual_train) < X_base_train.shape[0]:
            pad_size = X_base_train.shape[0] - len(full_visual_train)
            full_visual_train = np.vstack([full_visual_train, np.zeros((pad_size, 1))])
        else:
            full_visual_train = full_visual_train[:X_base_train.shape[0]]
    
    # For test: use zeros (visual scores only for training)
    full_visual_test = np.zeros((X_base_test.shape[0], 1))
    
    X_train = hstack([X_base_train, full_visual_train])
    X_test = hstack([X_base_test, full_visual_test])
else:
    X_train = X_base_train
    X_test = X_base_test

print(f"Train Shape: {X_train.shape}, Test Shape: {X_test.shape}")
print(f"y_train: {y_train.shape}, y_test: {y_test.shape}")
print(f"   Train - Class 0: {np.sum(y_train==0)}, Class 1: {np.sum(y_train==1)}")
print(f"   Test  - Class 0: {np.sum(y_test==0)}, Class 1: {np.sum(y_test==1)}")

# -----------------------------
# MODELS (OPTIMIZED)
# -----------------------------
# RANDOM FOREST (FIXED)
# -----------------------------
rf = RandomForestClassifier(
    n_estimators=100,  # Reduced from 400 for speed
    max_depth=15,      # Reduced from 25 for speed
    class_weight='balanced',
    n_jobs=-1,
    random_state=42
)

# -----------------------------
# XGBOOST (FIXED)
# -----------------------------
xgb = XGBClassifier(
    n_estimators=100,  # Reduced from 500 for speed
    learning_rate=0.05,
    max_depth=5,       # Reduced from 7 for speed
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=1,
    eval_metric='logloss',
    random_state=42
)

# -----------------------------
# LIGHTGBM (GOOD ALREADY)
# -----------------------------
lgbm = LGBMClassifier(
    n_estimators=100,  # Reduced from 500 for speed
    learning_rate=0.05,
    max_depth=5,       # Reduced from 7 for speed
    num_leaves=40,     # Reduced from 60 for speed
    class_weight='balanced',
    random_state=42
)

# -----------------------------
# ENSEMBLE (SOFT VOTING )
# -----------------------------
ensemble = VotingClassifier(
    estimators=[
        ('rf', rf),
        ('xgb', xgb),
        ('lgbm', lgbm)
    ],
    voting='soft',
    weights=[1, 2, 2]   
)

# -----------------------------
# TRAIN MODEL
# -----------------------------
print("Training Ensemble Model...")
ensemble.fit(X_train, y_train)

# EVALUATION ON TEST SET (unseen data)
print("\n" + "="*70)
print("MODEL EVALUATION (TEST SET - Unseen Data)")
print("="*70)

y_pred_train = ensemble.predict(X_train)
y_pred_test = ensemble.predict(X_test)

accuracy_train = accuracy_score(y_train, y_pred_train)
accuracy_test = accuracy_score(y_test, y_pred_test)

print(f"\nTraining Accuracy:  {accuracy_train:.4f}")
print(f"Testing Accuracy:   {accuracy_test:.4f}")
print(f"   (If similar = no overfitting | If Test << Train = overfitting)")

print("\n" + "-"*70)
print("Classification Report (Test Set):")
print("-"*70)
print(classification_report(y_test, y_pred_test, target_names=['Legitimate (0)', 'Phishing (1)']))

print("\n" + "-"*70)
print("Confusion Matrix (Test Set):")
print("-"*70)
cm = confusion_matrix(y_test, y_pred_test)
print(cm)
print(f"True Negatives:  {cm[0,0]} (Correct Legitimate)")
print(f"False Positives: {cm[0,1]} (Legitimate -> Phishing) ERROR")
print(f"False Negatives: {cm[1,0]} (Phishing -> Legitimate) ERROR")
print(f"True Positives:  {cm[1,1]} (Correct Phishing)")

# -----------------------------
# SAVE MODEL
# -----------------------------
pickle.dump(ensemble, open(
    r"C:\Users\rasik\OneDrive\Desktop\phishing_project\model\final_model.pkl", "wb"))

print("\n Model saved at: model/final_model.pkl")