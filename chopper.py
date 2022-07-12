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
class ChopperScape(Env):
    def __init__(self):
        super(ChopperScape, self).__init__()
        # Define metadata
        self.metadata = {"render_modes" : ["human", "rgb_array"], "render_fps" : 4}

        # Define a 2-D observation space
        self.observation_shape = (600, 800, 3)
        self.observation_space = spaces.Box(
            low=np.zeros(self.observation_shape),
            high=np.ones(self.observation_shape),
            dtype=np.float32
        )

        # Define an action space ranging from 0 to 4
        self.action_space = spaces.Discrete(5) # TODO change to 3

        # Create a canvas to render the environment
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Maximum fuel chopper can have
        self.max_fuel = 1000

        # TODO
        self.state = None # current coodinate, distance to target, movement distance as heading Left(2,3), right(2,-3)
        self.target = None

        # Chopper boundaries
        self.y_min = int(self.observation_shape[0] * 0.1)
        self.x_min = 0
        self.y_max = int(self.observation_shape[0] * 0.9)
        self.x_max = self.observation_shape[1]
    
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

        # Counts # TODO convert birds to turrents and remove fuel
        self.bird_count = 0
        self.fuel_count = 0

        # Initial chopper location TODO Derandomize missle locations when using formations
        x = random.randrange(int(self.observation_shape[0] * 0.05), int(self.observation_shape[0] * 0.10))
        y = random.randrange(int(self.observation_shape[1] * 0.15), int(self.observation_shape[1] * 0.20))

        # Initialize the chopper
        self.chopper = Chopper("Chopper", self.x_max, self.x_min, self.y_max, self.y_min)
        self.chopper.set_position(x, y)

        # Initialize the elements
        self.elements = [self.chopper]

        # Reset the canvas
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Draw canvas elements
        self.draw_elements_on_canvas()

        # Return initial observation TODO have other rendering mode to return this
        return self.canvas

    def render(self, mode = "human"): # TODO later default mode will be different
        assert mode in ["human", "rgb_array"], "Invalid mode, must be either \"human\" or \"rgb_array\""
        if mode == "human":
            cv2.imshow("Game", self.canvas)
            cv2.waitKey(20) # TODO convert to FPS calculation
        
        elif mode == "rgb_array":
            return self.canvas
    
    def close(self):
        cv2.destroyAllWindows()

    def get_action_meanings(self):
        return {0: "Right", 1: "Left", 2: "Down", 3: "Up", 4: "Do Nothing"} # TODO change to left, straight, right

    def has_collided(self, elem1, elem2): # TODO reread and redo collizion code
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
        # Flag that marks the termination of an episode
        done = False

        # Assert that it is a valid action # TODO David doesn't like it...so we must change it to an exception code...all hail David
        assert self.action_space.contains(action), "Invalid Action"

        # Decrease the fuel
        self.fuel_left -= 1

        # Timestep reward # TODO change to the state of the missle moving toward the target and positive reward for closer/negative for further
        reward = 1

        # apply the action to the chopper # TODO convert to top down 2-D for missles. Adjust move coordinates for each move action
        if action == 0:
            self.chopper.move(0,5)
        elif action == 1:
            self.chopper.move(0,-5)
        elif action == 2:
            self.chopper.move(5,0)
        elif action == 3:
            self.chopper.move(-5,0)
        elif action == 4:
            self.chopper.move(0,0)

        # Spawn a bird at the right edge with prob 0.01 # TODO take away random probability of spawning
        if random.random() < 0.01:
        
            # Spawn a bird #TODO convert to turrent
            spawned_bird = Bird(f"bird_{self.bird_count + 1}", self.x_max, self.x_min, self.y_max, self.y_min)
            self.bird_count += 1 #TODO set amount of turrents

            # Compute the x,y co-ordinates of the position from where the bird has to be spawned
            # Horizontally, the position is on the right edge and vertically, the height is randomly 
            # sampled from the set of permissible values #TODO convert logic for random x & y coord.
            bird_x = self.x_max 
            bird_y = random.randrange(self.y_min, self.y_max)
            spawned_bird.set_position(bird_x, bird_y)
            
            # Append the spawned bird to the elements currently present in Env. 
            self.elements.append(spawned_bird)

        # Spawn a fuel at the bottom edge with prob 0.01 #TODO remove fuel
        if random.random() < 0.01:
            # Spawn a fuel tank
            spawned_fuel = Fuel(f"fuel_{self.fuel_count + 1}", self.x_max, self.x_min, self.y_max, self.y_min)
            self.fuel_count += 1
            
            # Compute the x,y co-ordinates of the position from where the fuel tank has to be spawned
            # Horizontally, the position is randomly chosen from the list of permissible values and 
            # vertically, the position is on the bottom edge
            fuel_x = random.randrange(self.x_min, self.x_max)
            fuel_y = self.y_max
            spawned_fuel.set_position(fuel_x, fuel_y)
            
            # Append the spawned fuel tank to the elemetns currently present in the Env.
            self.elements.append(spawned_fuel)

        for elem in self.elements: #TODO remove birds moving out of the screen
            if isinstance(elem, Bird):
                # If the bird has reached the left edge, remove it from the Env
                if elem.get_position()[0] <= self.x_min:
                    self.elements.remove(elem)
                else:
                    # Move the bird left by 5 pts.
                    elem.move(-5,0)
                
                # If the bird has collided. 
                if self.has_collided(self.chopper, elem): #TODO set kill zone and conclude game when all missle are destoried
                    # Conclude the episode and remove the chopper from the Env.
                    done = True
                    reward = -10
                    self.elements.remove(self.chopper)

            if isinstance(elem, Fuel): #TODO removed fuel spawning, this is irrelevent
                # If the fuel tank has reached the top, remove it from the Env
                if elem.get_position()[1] <= self.y_min:
                    self.elements.remove(elem)
                else:
                    # Move the Tank up by 5 pts.
                    elem.move(0, -5)
                    
                # If the fuel tank has collided with the chopper. #TODO removed fuel spawning, this is irrelevent
                if self.has_collided(self.chopper, elem):
                    # Remove the fuel tank from the env.
                    self.elements.remove(elem)
                    
                    # Fill the fuel tank of the chopper to full. #TODO removed fuel spawning, this is irrelevent
                    self.fuel_left = self.max_fuel
        
        # Increment the episodic return #TODO change only true when done so user can choose how many episodes to run
        self.ep_return += 1

        # Draw elements on the canvas
        self.draw_elements_on_canvas()

        # If out of fuel, end the episode. #TODO of all missles or when all missles are destoried
        if self.fuel_left == 0:
            done = True

        #TODO add a check to add remaining fuel to reward
        #TODO convert info object to something meaniful...like cake.
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
class Chopper(Point):
    def __init__(self, name, x_max, x_min, y_max, y_min):
        super(Chopper, self).__init__(name, x_max, x_min, y_max, y_min)
        self.icon = cv2.imread('chopper.png') / 255.0
        self.icon_w = 64
        self.icon_h = 64
        self.icon = cv2.resize(self.icon, (self.icon_h, self.icon_w))

class Bird(Point):
    def __init__(self, name, x_max, x_min, y_max, y_min):
        super(Bird, self).__init__(name, x_max, x_min, y_max, y_min)
        self.icon = cv2.imread("bird.png") / 255.0
        self.icon_w = 32
        self.icon_h = 32
        self.icon = cv2.resize(self.icon, (self.icon_h, self.icon_w))
    
class Fuel(Point): #TODO  probably don't need
    def __init__(self, name, x_max, x_min, y_max, y_min):
        super(Fuel, self).__init__(name, x_max, x_min, y_max, y_min)
        self.icon = cv2.imread("fuel.png") / 255.0
        self.icon_w = 32
        self.icon_h = 32
        self.icon = cv2.resize(self.icon, (self.icon_h, self.icon_w))