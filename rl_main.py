from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.common.env_util import make_vec_env
from learning import RL_Env

print("-------------These are randomly generated actions in the environment-------------")
env = RL_Env(fps=20)
episodes = 0
obs = env.reset()
while episodes < 5:
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)
    print(info)
    env.render()

    if done:
        episodes += 1
        env.reset()

env.close()

print("-------------Then an RL algorithm is trained in the environment-------------")
multi_env = make_vec_env(RL_Env, n_envs=4)

expert = PPO(
    policy=MlpPolicy,
    env=multi_env,
    learning_rate=0.003, # usually 0.0003
    n_steps=256,
    verbose=1
)
expert.learn(total_timesteps=1000)  # Note: set to 100_000 to train a proficient expert
expert.save("rl_alg")
# expert = PPO.load("rl_alg")

print("-------------These are a trained agent's actions in the environment-------------")
env = RL_Env(fps=100)
episodes = 0
obs = env.reset()
while episodes < 10:
    action = expert.predict(obs)[0]
    obs, reward, done, info = env.step(action)
    env.render()
    
    if done:
        episodes += 1
        env.reset()

env.close()
