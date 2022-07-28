from learning import RL_Env

print("This are random actions in the given environment.")
env = RL_Env()
episodes = 0
obs = env.reset()
while episodes < 2:
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)
    env.render(mode="human")

    if done:
        episodes += 1
        env.reset()

env.close()

print("Then an RL algorithm is trained in this environment")
from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy

expert = PPO(
    policy=MlpPolicy,
    env=RL_Env(),
    seed=0,
    batch_size=64,
    ent_coef=0.0,
    learning_rate=0.01, # Usually something like 0.003
    n_epochs=10,
    n_steps=64,
    verbose=1
)
expert = expert.learn(200)  # Note: set to 100000 to train a proficient expert

print("After training, this is how the algorithm acts in the environment")
env = RL_Env()
episodes = 0
obs = env.reset()
while episodes < 5:
    action = expert.policy.predict(obs)[0]
    obs, reward, done, info = env.step(action)
    env.render(mode="human")
    
    if done:
        episodes += 1
        env.reset()

env.close()
