from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
import formations as formations

class Oracle():
    def __init__(self, filename : str):
        self.df = pd.read_csv(filename)
    
    def get_answers(self, n_missiles : int, n_turrets : int) -> str :
        flt_df = self.df[self.df["Missile Count"].isin([n_missiles])]
        features = flt_df[["Missile Count", "Formation Used", "Turret Count"]]
        label = flt_df.pop("Missiles Survived")

        # Split Data
        X_train, _, y_train, _ = train_test_split(features, label, test_size=0)

        # Create Classifier
        gnb = GaussianNB()

        # Train model
        gnb.fit(X_train, y_train)

        # Determine which formations are in the data
        valid_formations = [c for c in formations if isinstance(c, formations.Basic_Formation)]
        formation_dict = {f.id : str(f) for f in valid_formations}
        formation_ids = flt_df["Formation Used"].unique()
        answers = []
        for id in formation_ids:
            # Find highest confidence class
            survived = int(gnb.predict([[n_missiles, id, n_turrets]]))
            # Find confidence of that class
            predicted = float(gnb.predict_proba([[n_missiles, id, n_turrets], survived]))
            # Convert confidence to percentage
            percentage = str(round(float(("%.17f" % predicted).rstrip('0').rstrip('.')) * 100, 2)) + "%"
            # Collect answer
            answer = f"{formation_dict[id]}: {survived} missiles surviving with {percentage} confidence"
            answers.append(answer)
        return '\n'.join(answers)
