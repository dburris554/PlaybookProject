import unittest
from colosseum import FormationEnv
from components import Turret, has_collided, create_turret, create_rand_turret

class ComponentTester(unittest.TestCase):
    def test_collision(self):
        env_x = (0, 400)
        env_y = (0, 200)
        first = Turret("1", env_x[1], env_x[0], env_y[1], env_y[0])
        second = Turret("2", env_x[1], env_x[0], env_y[1], env_y[0])
        
        # Test no collision
        first.set_position(300, 0)
        second.set_position(0, 100)
        self.assertFalse(has_collided(first, second))
        self.assertFalse(has_collided(second, first))
        
        # Test collision
        first.set_position(100, 140)
        second.set_position(140, 100)
        self.assertTrue(has_collided(first, second))
        self.assertTrue(has_collided(second, first))

    def test_create_turret(self):
        t = create_turret(FormationEnv(), "id", 0, 0)
        self.assertTrue(isinstance(t, Turret))

    def test_create_rand_turret(self):
        t = create_rand_turret(FormationEnv(), "id", 0, 1, 0, 1)
        self.assertTrue(isinstance(t, Turret))
