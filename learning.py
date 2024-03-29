import numpy as np 
import cv2
import random

from gym import Env, spaces
from components import Missile, Turret, Target, has_collided, create_turret

font = cv2.FONT_HERSHEY_COMPLEX_SMALL

# This environment is based on the ChopperScape environment from this paper:
# https://blog.paperspace.com/creating-custom-environments-openai-gym/
class RL_Env(Env):
    def __init__(self, turret_count : int = 4, fps : int = 30):
        super().__init__()
        # Define metadata
        self.metadata = {"render_modes" : ["human", "rgb_array"], "render_fps" : fps}
        # Validate turret count
        if turret_count not in [1,2,3,4]:
            raise ValueError(f"turret count '{turret_count}' is not valid")
        self.turret_count = turret_count
        self.episode = 1
        # Define a 2-D observation space
        self.observation_shape = (600, 800, 3)
        self.observation_space = spaces.Box(
            low=np.zeros(self.observation_shape, dtype=np.float32),
            high=np.ones(self.observation_shape, dtype=np.float32),
            dtype=np.float32
        )

        # Define an action space for left, straight, and right
        self.action_space = spaces.Discrete(3)

        # Create a canvas to render the environment
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Maximum fuel missile can have
        self.max_fuel = 200

        # Initialize with empty dictionary for the current missile coordinates
        self.state = [{}]

        # Object boundaries
        self.y_min = 0
        self.x_min = 0
        self.y_max = self.observation_shape[0]
        self.x_max = self.observation_shape[1]

    def draw_elements_on_canvas(self):
        # Init the canvas
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Draw the objects on canvas
        for elem in self.elements:
            elem_shape = elem.icon.shape
            x,y = elem.x, elem.y
            self.canvas[y : y + elem_shape[0], x : x + elem_shape[1]] = elem.icon

        # Define text to be drawn
        text = f'Episode: {self.episode} | Fuel Remaining: {self.fuel_left}'

        # Put text on canvas
        self.canvas = cv2.putText(self.canvas, text, (10, 20), font, 0.8, (0,0,0), 1, cv2.LINE_AA)

    def reset(self):
        # Reset the fuel
        self.fuel_left = self.max_fuel

        # Reset the reward
        self.ep_reward = 0

        self.elements = []

        # Add target to elements
        self.target = Target("target", self.x_max, self.x_min, self.y_max, self.y_min)
        self.elements.append(self.target)

        # Spawn turrets in a static location
        if self.turret_count == 1:
            turret1 = create_turret(self, "1", int(self.observation_shape[1] * 0.75), int(self.observation_shape[0] * 0.5))
            self.elements.append(turret1)
        elif self.turret_count == 2:
            turret1 = create_turret(self, "1", int(self.observation_shape[1] * 0.75), int(self.observation_shape[0] * 0.3))
            self.elements.append(turret1)
            turret2 = create_turret(self, "2", int(self.observation_shape[1] * 0.5), int(self.observation_shape[0] * 0.5))
            self.elements.append(turret2)
        elif self.turret_count == 3:
            turret1 = create_turret(self, "1", int(self.observation_shape[1] * 0.75), int(self.observation_shape[0] * 0.2))
            self.elements.append(turret1)
            turret2 = create_turret(self, "2", int(self.observation_shape[1] * 0.5), int(self.observation_shape[0] * 0.4))
            self.elements.append(turret2)
            turret3 = create_turret(self, "3", int(self.observation_shape[1] * 0.6), int(self.observation_shape[0] * 0.7))
            self.elements.append(turret3)
        elif self.turret_count == 4:
            turret1 = create_turret(self, "1", int(self.observation_shape[1] * 0.75), int(self.observation_shape[0] * 0.1))
            self.elements.append(turret1)
            turret2 = create_turret(self, "2", int(self.observation_shape[1] * 0.5), int(self.observation_shape[0] * 0.4))
            self.elements.append(turret2)
            turret3 = create_turret(self, "3", int(self.observation_shape[1] * 0.75), int(self.observation_shape[0] * 0.6))
            self.elements.append(turret3)
            turret4 = create_turret(self, "4", int(self.observation_shape[1] * 0.6), int(self.observation_shape[0] * 0.8))
            self.elements.append(turret4)

        # Initial missile location
        x1 = random.randrange(int(self.observation_shape[1] * 0.05), int(self.observation_shape[1] * 0.3))
        y1 = random.randrange(int(self.observation_shape[0] * 0.05), int(self.observation_shape[0] * 0.95))

        # Initialize the missile
        missile = Missile("Missile_1", self.x_max, self.x_min, self.y_max, self.y_min)
        missile.set_position(x1, y1)
        self.missile = missile
        self.elements.append(self.missile)

        # Missile state
        self.state[0] = {self.missile.name : self.missile.get_position()}

        # Reset the canvas
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Draw canvas elements
        self.draw_elements_on_canvas()

        # Return initial observation
        return self.canvas

    def render(self, mode = "human"):
        # Validate render mode
        if mode not in ["human", "rgb_array"]:
            raise ValueError("Invalid mode, must be either \"human\" or \"rgb_array\"")
        
        if mode == "human":
            cv2.imshow("Game", self.canvas)
            cv2.waitKey(1000 // self.metadata["render_fps"])
        elif mode == "rgb_array":
            return self.canvas
    
    def close(self):
        cv2.destroyAllWindows()

    def get_action_meanings(self):
        return {0: "Left", 1: "Straight", 2: "Right"}

    def step(self, action):
        # Validate provided action
        if not self.action_space.contains(action):
            raise ValueError(f"Provided action '{action}' is not valid")
        # Flag that marks the termination of an episode
        done = False

        # Decrease the fuel
        self.fuel_left -= 1

        # Time step reward, but no reward if missile is hugging the walls
        y = self.missile.get_position()[1]
        if y > int(self.y_max * 0.1) and y < int(self.y_max * 0.9):
            reward = 2
        else:
            reward = 0

        # Apply the action to the missiles
        if action == 0:
            self.missile.move(5, -5)
        elif action == 1:
            self.missile.move(10, 0)
        elif action == 2:
            self.missile.move(5, 5)

        # Collision logic
        for elem in self.elements:
            if isinstance(elem, Turret):
                if self.missile.alive:
                    if has_collided(self.missile, elem):
                        reward -= 25
                        self.elements.remove(self.missile)
                        self.missile.kill()
            if isinstance(elem, Target):
                if self.missile.alive:
                    if has_collided(self.missile, elem):
                        y = self.missile.get_position()[1]
                        dist_to_center = abs(y - int(self.observation_shape[0] * 0.5))
                        reward += max(500 - (dist_to_center * 2), 0)
                        reward += self.fuel_left
                        self.elements.remove(self.missile)
                        self.missile.kill()
        
        # Missile states
        self.state[0] = {self.missile.name : self.missile.get_position()}

        # Increment the episodic reward
        self.ep_reward += reward

        # Draw elements on the canvas
        self.draw_elements_on_canvas()

        # If out of fuel, end the episode
        if self.fuel_left == 0:
            done = True

        # If all missiles are destroyed, end the episode
        if len([elem for elem in self.elements if isinstance(elem, Missile)]) == 0:
            done = True

        # Default info object
        info = {"episode_number": self.episode, "state": self.state, "ep_reward": self.ep_reward}

        if done:
            self.episode += 1

        return self.canvas, reward, done, info
