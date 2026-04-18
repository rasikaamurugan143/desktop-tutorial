import pickle
import numpy as np

# Load training labels
y_train = pickle.load(open('model/y_train.pkl', 'rb'))
y_test = pickle.load(open('model/y_test.pkl', 'rb'))
model = pickle.load(open('model/final_model.pkl', 'rb'))

print('Training labels:')
print(f'  Class 0: {np.sum(y_train == 0)}, Class 1: {np.sum(y_train == 1)}')
print(f'\nTest labels:')
print(f'  Class 0: {np.sum(y_test == 0)}, Class 1: {np.sum(y_test == 1)}')
print(f'\nModel classes: {model.classes_}')

# Let me also check by training a simple model on test data to see if it works
from sklearn.ensemble import RandomForestClassifier
from scipy.sparse import load_npz
import numpy as np

X_test = pickle.load(open('model/X_base_test.pkl', 'rb'))
full_visual = np.zeros((X_test.shape[0], 1))
from scipy.sparse import hstack
X_test_final = hstack([X_test, full_visual]).tocsr()

# Get a few predictions
y_pred = model.predict(X_test_final[:100])
y_actual = y_test[:100]

print(f'\nFirst 100 predictions vs actual (first 20):')
for i in range(20):
    print(f'  Actual: {y_actual[i]}, Predicted: {y_pred[i]}')
