#!/usr/bin/python

import csv
import pandas as pd
import numpy as np
from scipy.stats import randint
from sklearn.cross_validation import StratifiedKFold
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LinearRegression
from sklearn.grid_search import RandomizedSearchCV
from sklearn import metrics
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

# LOAD DATA
with open("featuresFactorized.npy/featuresFactorized.npy", "rb") as npy:
    X = np.load(npy)
# LOAD LABELS
with open("labels.npy", "rb") as npy:
    y = np.load(npy)

# SEPARATE DATA INTO TRAINING & HOLDOUT DATA
X_train, X_hold, y_train, y_hold = train_test_split(
     X, y, test_size=0.3, random_state=42)
y_train = y_train.astype(int)
y_hold = y_hold.astype(int)

# SPECIFY CROSS-VALIDATION SETTINGS
cv_call = StratifiedKFold(y_train,n_folds=10)
n_iter_search = 30

##### MODEL 1: LINEAR REGRESSION #####

# RUN RANDOMIZED SEARCH FOR HYPERPARAMETER OPTIMIZATION
clf = Pipeline([('reduce_dim', PCA()),
                ('model', LinearRegression())
 ])

param_dist = {"reduce_dim__n_components": randint(2, 50)}
# Random search for number of principal components

random_search = RandomizedSearchCV(clf, param_distributions=param_dist,
                                   n_iter=n_iter_search,cv=cv_call,
								   scoring='mean_squared_error')

random_search = random_search.fit(X_train, y_train)

# RETRIEVE OPTIMAL HYPERPARAMETER VALUES FROM RANDOM SEARCH
best_parameters, score, _ = max(random_search.grid_scores_, key=lambda x: x[1])
pca = PCA(n_components = best_parameters["reduce_dim__n_components"])
_ = pca.fit(X_train)
X_train_PCA = pca.fit_transform(X_train)
clf = LinearRegression()

# RUN MODEL WITH OPTIMIZED PARAMETERS
clf = clf.fit(X_train_PCA, y_train)


# MAKE PREDICTIONS ON HOLDOUT DATA
X_hold_PCA = pca.transform(X_hold)
y_hold_predict = clf.predict(X_hold_PCA)


# The mean square error
print("Residual sum of squares: %.2f"
      % np.mean((y_hold_predict - y_hold) ** 2))

