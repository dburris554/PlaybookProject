import pandas as pd
from colosseum import FormationEnv
from formations import *

pairs = []
turret = [1,2,3,4]
formations = [Ant3, Marching3, V3]
df = pd.DataFrame(columns = ["Missile Count",  "Formation Used",  "Turret Count",  "Missiles Survived"])
for f in formations:
    for t in turret:
        pairs.append((f,t))
for p in pairs:
    env = FormationEnv(p[0], turret_count=p[1], ep_count=100)
    obs = env.reset()

    while True:
        action = 0
        obs, reward, done, info = env.step(action)
        #env.render(mode="human")

        if done:
            data = info["data"]
            #print(data)
            df = df.merge(data, how = "outer")
            #print(data)
            break

df.to_csv('D:\School Projects\Project 2\json\hundred_test.csv')

env.close()
