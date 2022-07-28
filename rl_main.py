from learning import RL_Env

env = RL_Env(fps=10)
obs = env.reset()

episodes = 0
while episodes < 5:
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)
    env.render(mode="human")
    print(info)

    if done:
        episodes += 1
        env.reset()

env.close()

# from stable_baselines3 import PPO
# from stable_baselines3.ppo import MlpPolicy

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
