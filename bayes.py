import pandas as pd
from sklearn.naive_bayes import GaussianNB
import formations as formations

class Oracle():
    def __init__(self, filename : str):
        self.df = pd.read_csv(filename)
    
    def get_answers(self, n_missiles : int, n_turrets : int) -> str :
        flt_df = self.df[self.df["Missile Count"].isin([n_missiles])]
        features = flt_df[["Missile Count", "Formation Used", "Turret Count"]]
        labels = flt_df.pop("Missiles Survived")

        # Create Classifier
        gnb = GaussianNB()

        # Train model
        gnb.fit(features.values, labels)

        # Determine which formations are in the data
        valid_formations = [(name, cls) for name, cls in formations.__dict__.items() if hasattr(cls, 'id')]
        formation_dict = {cls.id : name for name, cls in valid_formations}
        formation_ids = flt_df["Formation Used"].unique()

        # Collect predictions for each formation
        answers = []
        for id in formation_ids:
            # Find highest confidence class and confidence of that class
            survived = int(gnb.predict([[n_missiles, id, n_turrets]]))
            confidence = max(gnb.predict_proba([[n_missiles, id, n_turrets]])[0])
            # Convert confidence to percentage
            percentage = str(round(float(("%.17f" % confidence).rstrip('0').rstrip('.')) * 100, 1)) + "%"
            # Collect answer
            answer = f"{formation_dict[id]}: {survived} missiles will survive with {percentage} confidence"
            answers.append(answer)

        return '\n'.join(answers)
