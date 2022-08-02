from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics

df = pd.read_csv('Missile All.csv')
opt = [5]
flt_df = df[df["Missile Count"].isin(opt)]
#print(df)

features = flt_df[["Missile Count","Formation Used", "Turret Count"]]
label = flt_df.pop("Missiles Survived")

# Split Data
X_train, X_test, y_train, y_test = train_test_split(features, label, test_size=0.3)
#print ("X Train:", X_train)
#print ("Y Train:", y_train)
#print ("X Test:", X_test)
#print ("Y Test:", y_test)

# Create Classifier
gnb = GaussianNB()

# Train model
gnb.fit(X_train, y_train)

# Predict missile survivability
y_pred = gnb.predict(X_test)

def oracle(gnb : GaussianNB, n_missiles : int, n_turrets : int) -> str :
    # GNB Predictions
    print(gnb.classes_)
    predicted = gnb.predict_proba([[5,10,3]])
    print("The gods tell me", predicted, "missiles will survive")

    #n = 8.99284722486562e-02 
    #converted_number = float(("%.17f" % n).rstrip('0').rstrip('.'))
    #print(round(converted_number*100,2),"%")