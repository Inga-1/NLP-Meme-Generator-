import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
import os

# Dynamically gets the path to the current folder and returns pandas dataframe
# when given the name of the .txt file
def loadDf(fileDir):
    basePath = os.path.dirname(os.path.abspath(__file__))
    fullPath = os.path.join(basePath, fileDir)
    return pd.read_csv(fullPath, sep = ";", names = ["text", "label"])

# Getting the train, validation and test sets
# Note: the validation set is used in the model as an addition to the training set.
# The reasoning behind this decision will be more clear later in the code

dfTrain = loadDf("train.txt")
dfVal = loadDf("val.txt")
dfTest = loadDf("test.txt")

# Finalizing the pre-processing of the dataset to be used in the model.
# The test set remains untouched, train and val pandas frameworks are merged
X_train = pd.concat([dfTrain["text"], dfVal["text"]])
Y_train = pd.concat([dfTrain["label"], dfVal["label"]])
X_test = dfTest["text"]
Y_test = dfTest["label"]

# Defining the pipline for the model:
# TfidfVectorizer - converts text into a sparse TF-IDF feature matrix
#   -max_features=10000 - restricts vocabulary to the top 10k terms to reduce overfitting
#   -ngram_range=(1,3) - captures unigrams, bigrams, and trigrams to encode local word patterns
#   -sublinear_tf=True - applies logarithmic scaling to term frequencies to reduce the impact of very frequent terms
#   -min_df=2 - ignores terms that appear in less than 2 documents to filter out noise
# LogisticRegression - chosen for its efficiency on sparse high-dimensional data compared to other tested models
#   -max_iter=1000 - sufficient for the current dataset
#   -class_weight="balanced" - helps to balance the overrepresented and underrepresented classes
pipe = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1,3), sublinear_tf=True, min_df=2)),
    ("clf", LogisticRegression(max_iter=1000, class_weight="balanced"))
])

# Defining 'C' values:
# Logistic regression uses a regularization parameter 'C' to control model complexity.
# The lower the value of 'C' is, the stronger is regularization, the simpler the model.
# The higher the value of 'C', the weaker is regularization and more complex is the model.
# We are trying to test a logarithmic range of values to find the optimal balance between overfitting
# and underfitting
params = {
    "clf__C": [0.01, 0.1, 1, 10, 100]
}

# Hyperparameter tuning:
# GridSearchCV evaluates all 5 C values using 5-fold cross validation (cv=5).
# At each turn, the training set is split into smaller train/validation partitions.
# The scoring metric is chosen to be 'f1_macro', since it averages F1-scores across all
# classes equally, which is important to minimize the class imbalance.
# In the end, the best model configuration is selected based on the factors 
# outlined above.

grid = GridSearchCV(pipe, params, cv = 5, scoring = "f1_macro")
grid.fit(X_train, Y_train)

# Printing results:
# After the best-performing model is extracted,its performance is evaluated on
# the untouched testing set (which in this case replaces/simulates user input).
# The classification report gives precision, recall, and F1-score for each emotion class,
# allowing inspection of which emotions are better (or worse) detected by the model.
bestModel = grid.best_estimator_
print(f"\nBest C: {grid.best_params_['clf__C']}")
print("\nTest Set Performance:")
print(classification_report(Y_test, bestModel.predict(X_test)))

# The model is then saved as a pkl file for later use in the project
# using joblib's dump function.
output = os.path.join(os.path.dirname(__file__), "processing_model.pkl")
joblib.dump(bestModel, output)

