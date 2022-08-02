from bayes import Oracle

num_missiles = 0
while num_missiles < 2 or num_missiles > 5:
    num_missiles = int(input("Enter the number of missiles (2 to 5):\n"))
    
num_turrets = 0
while num_turrets < 1 or num_turrets > 4:
    num_turrets = int(input("Enter the number of turrets (1 to 4): \n"))

file = 'Missile All.csv'
oracle = Oracle(file)

print('\n' + oracle.get_answers(num_missiles, num_turrets))
