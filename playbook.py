import pandas as pd

missiles = input("Enter the number of missiles:\n")
turrets = input("Enter the number of turrets: \n")

print(f"Given {missiles} missiles and {turrets} turrets:\n")

# Use known statistics from Supervised Learning models
if missiles == 3 and turrets == 4: # TODO pull from bayes model
    print("V3: 2 missiles surviving with 39% Confidence")
    print("Ant3: 3 missiles surviving with 20% Confidence")
    print("Marching3: 2 missiles surviving with 35% Confidence")
    print("You must choose...wisely")
elif missiles == 4 and turrets == 2:  # TODO refine
    print("Use that formation")
else:
    print("Unknown answer")
