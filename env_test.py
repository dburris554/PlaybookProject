import unittest
from stable_baselines3.common.env_checker import check_env
from colosseum import FormationEnv
from learning import RL_Env

class EnvTester(unittest.TestCase):
    def test_envs_conforms_to_api(self):
        check_env(FormationEnv())
        check_env(RL_Env())