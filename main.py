from chopper import MissileEnv

env = MissileEnv(formation=MissileEnv.formations[0])
obs = env.reset()

while True:
    action = env.action_space.sample()
    obs, reward, done, _ = env.step(action)
    env.render()

    if done:
        break

env.close()

from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy

# import gym

# env = gym.make("CartPole-v1")
# expert = PPO(
#     policy=MlpPolicy,
#     env=env,
#     seed=0,
#     batch_size=64,
#     ent_coef=0.0,
#     learning_rate=0.0003,
#     n_epochs=10,
#     n_steps=64,
#     verbose=1
# )
# expert.learn(1000)  # Note: set to 100000 to train a proficient expert
# print(expert)
