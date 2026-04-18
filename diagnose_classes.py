import pickle
import numpy as np
from scipy.sparse import hstack
from sklearn.ensemble import RandomForestClassifier

# Load the new model
model = pickle.load(open('model/final_model.pkl', 'rb'))

# Load test data
X_base_test = pickle.load(open('model/X_base_test.pkl', 'rb'))
y_test = pickle.load(open('model/y_test.pkl', 'rb'))
full_visual = np.zeros((X_base_test.shape[0], 1))
X_test = hstack([X_base_test, full_visual])

# Get predictions
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)

# Check which class the model predicts for class 0 and class 1 examples
class0_examples_pred = y_pred[y_test == 0]
class1_examples_pred = y_pred[y_test == 1]

print(f"When y_test=0 (Legitimate), model predicts:")
print(f"  Class 0: {np.sum(class0_examples_pred == 0)} ({np.sum(class0_examples_pred == 0)/len(class0_examples_pred)*100:.1f}%)")
print(f"  Class 1: {np.sum(class0_examples_pred == 1)} ({np.sum(class0_examples_pred == 1)/len(class0_examples_pred)*100:.1f}%)")

print(f"\nWhen y_test=1 (Phishing), model predicts:")
print(f"  Class 0: {np.sum(class1_examples_pred == 0)} ({np.sum(class1_examples_pred == 0)/len(class1_examples_pred)*100:.1f}%)")
print(f"  Class 1: {np.sum(class1_examples_pred == 1)} ({np.sum(class1_examples_pred == 1)/len(class1_examples_pred)*100:.1f}%)")

print(f"\nConclusion:")
print(f"If model predicts class 0 most of the time for legitimate (y_test=0),")
print(f"then class 0 = Legitimate and class 1 = Phishing (correct)")
print(f"\nIf model predicts class 1 most of the time for legitimate (y_test=0),")
print(f"then classes are INVERTED and we should flip the labels")
