import numpy as np 
import cv2 
import matplotlib.pyplot as plt
import PIL.Image as Image
import gym
import random

from gym import Env, spaces
import time

font = cv2.FONT_HERSHEY_COMPLEX_SMALL

# This environment is based on the ChopperScape environment from this paper:
# https://blog.paperspace.com/creating-custom-environments-openai-gym/
class MissileEnv(Env):
    formations = ["V-formation", "Ant-trail"]

    def __init__(self, fps : int = 10, formation : str | None = None):
        super(MissileEnv, self).__init__()
        # Define metadata
        self.metadata = {"render_modes" : ["human", "rgb_array"], "render_fps" : fps} # TODO Use fps somewhere
        self.formation = formation
        # Define a 2-D observation space
        self.observation_shape = (600, 800, 3)
        self.observation_space = spaces.Box(
            low=np.zeros(self.observation_shape),
            high=np.ones(self.observation_shape),
            dtype=np.float32
        )

        # Define an action space for left, straight, and right
        self.action_space = spaces.Discrete(3)

        # Create a canvas to render the environment
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Maximum fuel chopper can have
        self.max_fuel = 1000

        # TODO
        self.target = None
        self.state = [{}, None, None] # current coodinate, distance to target, movement distance as heading Left(2,3), right(2,-3)

        # Chopper boundaries
        self.y_min = int(self.observation_shape[0] * 0.1)
        self.x_min = 0
        self.y_max = int(self.observation_shape[0] * 0.9)
        self.x_max = self.observation_shape[1]

        if formation and formation in self.formations:
            self.autorun = True
    
    def draw_elements_on_canvas(self):
        # Init the canvas
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Draw the helicopter on canvas
        for elem in self.elements:
            elem_shape = elem.icon.shape
            x,y = elem.x, elem.y
            self.canvas[y : y + elem_shape[1], x : x + elem_shape[0]] = elem.icon

        # TODO remove or edit text
        text = f'Fuel Left: {self.fuel_left} | Rewards: {self.ep_return}'

        # Put text on canvas  TODO remove or edit
        self.canvas = cv2.putText(self.canvas, text, (10, 20), font, 0.8, (0,0,0), 1, cv2.LINE_AA)

    def reset(self):
        # Reset the fuel
        self.fuel_left = self.max_fuel

        # Reset the reward
        self.ep_return = 0

        # Turret count
        self.turret_count = 1

        self.elements = []

        if self.autorun:
            if self.formation == "V-formation":
                # Initial formation location
                x = int(self.observation_shape[0] * 0.2)
                y = int(self.observation_shape[1] * 0.5)

                # Initialize the missiles
                missiles = [Missile("Missile_1", self.x_max, self.x_min, self.y_max, self.y_min),
                            Missile("Missile_2", self.x_max, self.x_min, self.y_max, self.y_min),
                            Missile("Missile_3", self.x_max, self.x_min, self.y_max, self.y_min)]
                missiles[0].set_position(x, y - 75)
                missiles[1].set_position(x + 100, y)
                missiles[2].set_position(x, y + 75)
            # Spawn a turret
            spawned_turret = Turret(f"turret_{self.turret_count + 1}", self.x_max, self.x_min, self.y_max, self.y_min)
            self.turret_count += 1 #TODO set amount of turrents

            # Spawn a turret in a random location on the right-half of the screen
            turret_x = int(self.observation_shape[0] * 0.65)
            turret_y = int(self.observation_shape[1] * 0.5)
            spawned_turret.set_position(turret_x, turret_y)
            
            # Append the spawned turret to the elements currently present in Env. 
            self.elements.append(spawned_turret)
        else:
            # Initial missile locations # FIXME Make sure missiles spawn in different places
            x1 = random.randrange(int(self.observation_shape[0] * 0.05), int(self.observation_shape[0] * 0.2))
            y1 = random.randrange(int(self.observation_shape[1] * 0.05), int(self.observation_shape[1] * 0.95))
            x2 = random.randrange(int(self.observation_shape[0] * 0.05), int(self.observation_shape[0] * 0.2))
            y2 = random.randrange(int(self.observation_shape[1] * 0.05), int(self.observation_shape[1] * 0.95))
            x3 = random.randrange(int(self.observation_shape[0] * 0.05), int(self.observation_shape[0] * 0.2))
            y3 = random.randrange(int(self.observation_shape[1] * 0.05), int(self.observation_shape[1] * 0.95))

            # Initialize the missiles
            missiles = [Missile("Missile_1", self.x_max, self.x_min, self.y_max, self.y_min),
                        Missile("Missile_2", self.x_max, self.x_min, self.y_max, self.y_min),
                        Missile("Missile_3", self.x_max, self.x_min, self.y_max, self.y_min)]
            missiles[0].set_position(x1, y1)
            missiles[1].set_position(x2, y2)
            missiles[2].set_position(x3, y3)

        # Initialize the elements
        self.missiles = missiles
        self.elements += self.missiles

        # Missile states
        self.state[0] = {missile.name : missile.get_position() for missile in self.missiles}

        # Reset the canvas
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Draw canvas elements
        self.draw_elements_on_canvas()

        # Return initial observation TODO have other rendering mode to return game state
        return self.canvas

    def render(self, mode = "human"): # TODO later default mode will be different
        assert mode in ["human", "rgb_array"], "Invalid mode, must be either \"human\" or \"rgb_array\""
        if mode == "human":
            cv2.imshow("Game", self.canvas)
            cv2.waitKey(1000 // self.metadata["render_fps"])

        elif mode == "rgb_array":
            return self.canvas
    
    def close(self):
        cv2.destroyAllWindows()

    def get_action_meanings(self):
        return {0: "Left", 1: "Straight", 2: "Right"}

    def has_collided(self, elem1, elem2):
        x_col = False
        y_col = False

        elem1_x, elem1_y = elem1.get_position()
        elem2_x, elem2_y = elem2.get_position()

        if 2 * abs(elem1_x - elem2_x) <= (elem1.icon_w + elem2.icon_w):
            x_col = True

        if 2 * abs(elem1_y - elem2_y) <= (elem1.icon_h + elem2.icon_h):
            y_col = True

        if x_col and y_col:
            return True

        return False
    
    def step(self, action):
        if self.autorun:
            return self.autostep()

        # Flag that marks the termination of an episode
        done = False

        # Assert that it is a valid action # TODO David doesn't like it...so we must change it to an exception code...all hail David
        assert self.action_space.contains(action), "Invalid Action"

        # Decrease the fuel
        self.fuel_left -= 1

        # Timestep reward # TODO change to the state of the missle moving toward the target and positive reward for closer/negative for further
        reward = 1

        # apply the action to the missiles # TODO convert to top down 2-D for missles. Adjust move coordinates for each move action
        if action == 0: # FIXME Currently not logical action-taking
            [missile.move(0,5) for missile in self.missiles if missile in self.elements]
        elif action == 1:
            [missile.move(0,5) for missile in self.missiles if missile in self.elements]
        elif action == 2:
            [missile.move(0,5) for missile in self.missiles if missile in self.elements]

        # Spawn a turret
        spawned_turret = Turret(f"turret_{self.turret_count + 1}", self.x_max, self.x_min, self.y_max, self.y_min)
        self.turret_count += 1 #TODO set amount of turrents

        # Spawn a turret in a random location on the right-half of the screen
        turret_x = random.randrange(int(self.observation_shape[0] * 0.5), int(self.observation_shape[0] * 0.95)) 
        turret_y = random.randrange(int(self.observation_shape[1] * 0.05), int(self.observation_shape[1] * 0.95))
        spawned_turret.set_position(turret_x, turret_y)
        
        # Append the spawned turret to the elements currently present in Env. 
        self.elements.append(spawned_turret)

        for elem in self.elements:
            if isinstance(elem, Turret):
                # If the turret has collided with a missile
                for m_index in range(len(self.missiles)-1, -1, -1):
                    missile = self.missiles[m_index]
                    if self.has_collided(missile, elem): #TODO set kill zone and conclude game when all missiles are destroyed
                        reward = -10
                        self.elements.remove(missile)
        
        # Missile states
        self.state[0] = {missile.name : missile.get_position() for missile in self.missiles if missile in self.elements}

        # Increment the episodic return #TODO change only true when done so user can choose how many episodes to run
        self.ep_return += 1

        # Draw elements on the canvas
        self.draw_elements_on_canvas()

        # If out of fuel, end the episode. #TODO of all missles or when all missles are destoried
        if self.fuel_left == 0:
            done = True

        # If all missiles are destroyed, end the episode
        if len([elem for elem in self.elements if isinstance(elem, Missile)]) == 0:
            done = True

        #TODO add a check to add remaining fuel to reward
        #TODO convert info object to something meaningful...like cake.
        return self.canvas, reward, done, {"episode": "", "state" : self.state}

    def autostep(self):
        # Flag that marks the termination of an episode
        done = False

        [missile.move(5,0) for missile in self.missiles if missile in self.elements]

        for elem in self.elements:
            if isinstance(elem, Turret):
                # If the turret has collided with a missile
                for m_index in range(len(self.missiles)-1, -1, -1):
                    missile = self.missiles[m_index]
                    if missile in self.elements:
                        if self.has_collided(missile, elem): #TODO set kill zone and conclude game when all missiles are destroyed
                            reward = -10
                            self.elements.remove(missile)

        # Missile states
        self.state[0] = {missile.name : missile.get_position() for missile in self.missiles if missile in self.elements}

        # Draw elements on the canvas
        self.draw_elements_on_canvas()

        # if missiles reach end of screen, end the episode
        for missile in self.missiles:
            if missile.get_position()[0] + missile.icon_w >= self.x_max:
                # TODO add Missile survived logic
                self.elements.remove(missile)

        # If all missiles are destroyed or reach the end of the screen, end the episode
        if len([elem for elem in self.elements if isinstance(elem, Missile)]) == 0:
            done = True
        
        reward = 0

        return self.canvas, reward, done, {"episode": ""}
    
class Point(object): #TODO May not need it or parts of it
    def __init__(self, name, x_max, x_min, y_max, y_min):
        self.x = 0
        self.y = 0
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.name = name

    def set_position(self, x, y):
        self.x = self.clamp(x, self.x_min, self.x_max - self.icon_w)
        self.y = self.clamp(y, self.y_min, self.y_max - self.icon_h)
    
    def get_position(self):
        return (self.x, self.y)
    
    def move(self, del_x, del_y):
        self.x += del_x
        self.y += del_y
        
        self.x = self.clamp(self.x, self.x_min, self.x_max - self.icon_w)
        self.y = self.clamp(self.y, self.y_min, self.y_max - self.icon_h)

    def clamp(self, n, minn, maxn):
        return max(min(maxn, n), minn)

#TODO no depended on images
class Missile(Point):
    def __init__(self, name, x_max, x_min, y_max, y_min):
        super(Missile, self).__init__(name, x_max, x_min, y_max, y_min)
        self.icon = cv2.imread('chopper.png') / 255.0
        self.icon_w = 64
        self.icon_h = 64
        self.icon = cv2.resize(self.icon, (self.icon_h, self.icon_w))

class Turret(Point):
    def __init__(self, name, x_max, x_min, y_max, y_min):
        super(Turret, self).__init__(name, x_max, x_min, y_max, y_min)
        self.icon = cv2.imread("bird.png") / 255.0
        self.icon_w = 32
        self.icon_h = 32
        self.icon = cv2.resize(self.icon, (self.icon_h, self.icon_w))
