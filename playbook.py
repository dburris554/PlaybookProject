missiles = input("Enter the number of missiles:\n")
turrets = input("Enter the number of turrets: \n")

print(f"Given {missiles} missiles and {turrets} turrets:\n")

# Use known statistics from Supervised Learning models
if missiles == 3 and turrets == 4:
    print("Use this formation")
elif missiles == 4 and turrets == 2:
    print("Use that formation")
else:
    print("Unknown answer")