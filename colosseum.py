import numpy as np 
import cv2
import random
import pandas as pd

from gym import Env, spaces
from components import Missile, Turret
from formations import Basic_Formation, V_formation, Ant_trail

font = cv2.FONT_HERSHEY_COMPLEX_SMALL

# This environment is based on the ChopperScape environment from this paper:
# https://blog.paperspace.com/creating-custom-environments-openai-gym/
class FormationEnv(Env):
    def __init__(self, fps : int = 30, formation_class : Basic_Formation = V_formation, ep_count : int = 5):
        super(FormationEnv, self).__init__()
        # Define metadata
        self.metadata = {"render_modes" : ["human", "rgb_array"], "render_fps" : fps,
                         "tot_episodes" : ep_count, "formation_class" : formation_class}
        self.episode = 1
        # Define a 2-D observation space
        self.observation_shape = (600, 800, 3)
        self.observation_space = spaces.Box(
            low=np.zeros(self.observation_shape, np.float32),
            high=np.ones(self.observation_shape, np.float32),
            dtype=np.float32
        )

        # Define an action space for straight
        self.action_space = spaces.Discrete(1)

        # Create a canvas to render the environment
        self.canvas = np.ones(self.observation_shape, np.float32) * 1

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
        self.canvas = np.ones(self.observation_shape, np.float32) * 1

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
        self.turret_count = 1
        self.elements = []

        # Initial formation location
        x = int(self.observation_shape[1] * 0.2)
        y = int(self.observation_shape[0] * 0.5)

        # Initialize turret
        spawned_turret = Turret(f"turret_{self.turret_count}", self.x_max, self.x_min, self.y_max, self.y_min)

        # Spawn a turret in a random location on the right-half of the screen
        turret_x = random.randrange(int(self.observation_shape[1] * 0.50), int(self.observation_shape[1] * 0.95))
        turret_y = random.randrange(int(self.observation_shape[0] * 0.05), int(self.observation_shape[0] * 0.95))
        spawned_turret.set_position(turret_x, turret_y)
        
        # Append the spawned turret to the elements currently present in Env. 
        self.elements.append(spawned_turret)
        
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

    #FIXME Only works on square shapes, not rectangles
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
        if not self.action_space.contains(action):
            raise ValueError(f"Provided action '{action}' is not valid")
        # Flag that marks the termination of an episode
        done = False

        reward = 0

        self.formation.move_forward()

        for elem in self.elements:
            if isinstance(elem, Turret):
                for alive_missile in [missile for missile in self.formation.get_missiles() if missile.alive]:
                    if self.has_collided(alive_missile, elem):
                        reward -= 10
                        self.elements.remove(alive_missile)
                        alive_missile.kill()

        # Missile states
        self.state[0] = {missile.name : missile.get_position() for missile in self.formation.get_missiles()}

        

        # Draw elements on the canvas
        self.draw_elements_on_canvas()

        # if missiles reach end of screen, end the episode
        survived = 0
        for alive_missile in [missile for missile in self.formation.get_missiles() if missile.alive]:
            if alive_missile.get_position()[0] + alive_missile.icon_w >= self.x_max:
                # TODO add Missile survived logic
                self.elements.remove(alive_missile)
                survived += 1
                alive_missile.kill()

        # Default info object
        info = {"episode": self.episode, "state": self.state}

        # If all missiles are destroyed or reach the end of the screen, end the episode
        if len([elem for elem in self.elements if isinstance(elem, Missile)]) == 0:
            # Collect data from this episode
            # TODO Make a numeric formation lookup
            self.data.append([self.formation.missile_count, 0, self.turret_count, survived])
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
