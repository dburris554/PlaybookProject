from colosseum import FormationEnv
from formations import *

env = FormationEnv(Marching3, turret_count=2, ep_count=100)
obs = env.reset()

while True:
    action = 0
    obs, reward, done, info = env.step(action)
    env.render(mode="rgb_array")

    if done:
        data = info["data"]
        #print(data)
        break

env.close()
