from main import data
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics

df = pd.DataFrame(data)
print(df)

features = df[["Missile Count","Formation Used", "Turret Count"]]
label = df["Missiles Survived"]

# Split Data
X_train, X_test, y_train, y_test = train_test_split(features, label, test_size=0.3,random_state=109)

# Create Classifier
gnb = GaussianNB()

# Train model
gnb.fit(X_train, y_train)

# Predict missile survivability
y_pred = gnb.predict(X_test)

# Testing Accuracy
print("Accuracy: ",metrics.accuracy_score(y_test, y_pred))