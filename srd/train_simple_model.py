import pickle
import numpy as np
from scipy.sparse import hstack
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

print("Loading data...")
X_base_train = pickle.load(open('model/X_base_train.pkl', 'rb'))
X_base_test = pickle.load(open('model/X_base_test.pkl', 'rb'))
y_train = pickle.load(open('model/y_train.pkl', 'rb'))
y_test = pickle.load(open('model/y_test.pkl', 'rb'))

# Add visual features (zeros)
full_visual_train = np.zeros((X_base_train.shape[0], 1))
full_visual_test = np.zeros((X_base_test.shape[0], 1))

X_train = hstack([X_base_train, full_visual_train])
X_test = hstack([X_base_test, full_visual_test])

print(f"Data shapes: Train {X_train.shape}, Test {X_test.shape}")
print(f"Train labels: Class 0={np.sum(y_train==0)}, Class 1={np.sum(y_train==1)}")
print(f"Test labels: Class 0={np.sum(y_test==0)}, Class 1={np.sum(y_test==1)}")

# Use simple RandomForest (more interpretable)
print("\nTraining RandomForest...")
rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    class_weight='balanced',
    n_jobs=-1,
    random_state=42
)
rf.fit(X_train, y_train)

# Test predictions
y_pred_train = rf.predict(X_train)
y_pred_test = rf.predict(X_test)
y_proba_test = rf.predict_proba(X_test)

train_acc = accuracy_score(y_train, y_pred_train)
test_acc = accuracy_score(y_test, y_pred_test)

print(f"\nTraining Accuracy: {train_acc:.4f}")
print(f"Test Accuracy: {test_acc:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred_test, target_names=['Legitimate (0)', 'Phishing (1)']))

print("\nSaving model...")
pickle.dump(rf, open('model/final_model.pkl', 'wb'))

print("✅ Simple Random Forest model trained and saved!")
