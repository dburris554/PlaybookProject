import numpy as np 
import cv2
import pandas as pd

from gym import Env, spaces
from components import Missile, Turret, has_collided, create_rand_turret
from formations import Basic_Formation, V3

font = cv2.FONT_HERSHEY_COMPLEX_SMALL

# This environment is based on the ChopperScape environment from this paper:
# https://blog.paperspace.com/creating-custom-environments-openai-gym/
class FormationEnv(Env):
    def __init__(self, formation_class : Basic_Formation = V3, turret_count : int = 3, fps : int = 30, ep_count : int = 5):
        super().__init__()
        # Define metadata
        self.metadata = {"render_modes" : ["human", "rgb_array"], "render_fps" : fps,
                         "tot_episodes" : ep_count, "formation_class" : formation_class}
        if turret_count not in [1,2,3,4]:
            raise ValueError(f"turret count '{turret_count}' is not valid")
        self.turret_count = turret_count
        self.episode = 1
        self.survived = 0
        # Define a 2-D observation space
        self.observation_shape = (600, 800, 3)
        self.observation_space = spaces.Box(
            low=np.zeros(self.observation_shape, dtype=np.float32),
            high=np.ones(self.observation_shape, dtype=np.float32),
            dtype=np.float32
        )

        # Define an action space for straight
        self.action_space = spaces.Discrete(1)

        # Create a canvas to render the environment
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Initialize with empty dictionary for the current missile coordinates
        self.state = [{}]

        # boundaries
        self.y_min = 0
        self.x_min = 0
        self.y_max = self.observation_shape[0]
        self.x_max = self.observation_shape[1]

        # Initialize formation
        self.formation = formation_class()

        # Intialize list for data
        self.data = []
    
    def draw_elements_on_canvas(self):
        # Init the canvas
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Draw the objects on canvas
        for elem in self.elements:
            elem_shape = elem.icon.shape
            x,y = elem.x, elem.y
            self.canvas[y : y + elem_shape[0], x : x + elem_shape[1]] = elem.icon

        remaining = len([missile for missile in self.formation.get_missiles() if missile.alive])
        text = f'Episode: {self.episode} | Missiles Left: {remaining}'

        # Put text on canvas
        self.canvas = cv2.putText(self.canvas, text, (10, 20), font, 0.8, (0,0,0), 1, cv2.LINE_AA)

    def reset(self):
        self.survived = 0
        self.elements = []

        if self.turret_count == 1:
            turret1 = create_rand_turret(self, "1", 0.5, 1, 0, 1)
            self.elements.append(turret1)
        elif self.turret_count == 2:
            turret1 = create_rand_turret(self, "1", 0.5, 1, 0, 0.6)
            self.elements.append(turret1)
            turret2 = create_rand_turret(self, "2", 0.5, 1, 0.4, 1)
            self.elements.append(turret2)
        elif self.turret_count == 3:
            turret1 = create_rand_turret(self, "1", 0.5, 1, 0, 0.4)
            self.elements.append(turret1)
            turret2 = create_rand_turret(self, "2", 0.5, 1, 0.3, 0.7)
            self.elements.append(turret2)
            turret3 = create_rand_turret(self, "3", 0.5, 1, 0.6, 1)
            self.elements.append(turret3)
        elif self.turret_count == 4:
            # Create turrets in quadrants
            turret1 = create_rand_turret(self, "1", 0.5, 0.75, 0, 0.6)
            self.elements.append(turret1)
            turret2 = create_rand_turret(self, "2", 0.75, 1, 0, 0.6)
            self.elements.append(turret2)
            turret3 = create_rand_turret(self, "3", 0.5, 0.75, 0.4, 1)
            self.elements.append(turret3)
            turret4 = create_rand_turret(self, "4", 0.75, 1, 0.4, 1)
            self.elements.append(turret4)
        
        # Reset and store the missiles
        self.formation = self.metadata["formation_class"]()
        self.elements += self.formation.get_missiles()

        # Missile states
        self.state[0] = {missile.name : missile.get_position() for missile in self.formation.get_missiles()}

        # Reset the canvas
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Draw canvas elements
        self.draw_elements_on_canvas()

        # Return initial observation
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
        return {0: "Straight"}

    def step(self, action):
        if not self.action_space.contains(action):
            raise ValueError(f"Provided action '{action}' is not valid")
        # Flag that marks the termination of an episode
        done = False

        reward = 0

        self.formation.move_forward()

        for elem in self.elements:
            if isinstance(elem, Turret):
                for alive_missile in [missile for missile in self.formation.get_missiles() if missile.alive]:
                    if has_collided(alive_missile, elem):
                        reward -= 10
                        self.elements.remove(alive_missile)
                        alive_missile.kill()

        # Missile states
        self.state[0] = {missile.name : missile.get_position() for missile in self.formation.get_missiles()}

        # Draw elements on the canvas
        self.draw_elements_on_canvas()

        # if missiles reach end of screen, end the episode
        alive_missiles = [missile for missile in self.formation.get_missiles() if missile.alive]
        for alive_missile in alive_missiles:
            if alive_missile.get_position()[0] + alive_missile.icon_w >= self.x_max:
                self.elements.remove(alive_missile)
                self.survived += 1
                alive_missile.kill()

        # Default info object
        info = {"episode_number": self.episode, "state": self.state}

        # If all missiles are destroyed or reach the end of the screen, end the episode
        if len([elem for elem in self.elements if isinstance(elem, Missile)]) == 0:
            # Collect data from this episode
            self.data.append([self.formation.missile_count, self.formation.id, self.turret_count, self.survived])
            # Increment episode counter
            self.episode += 1
            # If episode count is fulfilled, set done to True, else reset
            if self.episode > self.metadata["tot_episodes"]:
                done = True
                # Add collected data to info object
                info["data"] = pd.DataFrame(data=self.data, columns=['Missile Count', 'Formation Used', 'Turret Count', 'Missiles Survived'], dtype=int)
            else:
                self.reset()

        return self.canvas, reward, done, info
