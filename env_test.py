import unittest
from stable_baselines3.common.env_checker import check_env
from chopper import MissileEnv

class EnvTester(unittest.TestCase):
    def test_env_conforms_to_api(self):
        check_env(MissileEnv())