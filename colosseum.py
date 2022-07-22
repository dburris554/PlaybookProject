import numpy as np 
import cv2
import random

from gym import Env, spaces
from components import Missile, Turret

font = cv2.FONT_HERSHEY_COMPLEX_SMALL

# This environment is based on the ChopperScape environment from this paper:
# https://blog.paperspace.com/creating-custom-environments-openai-gym/
class FormationEnv(Env):
    formations = ["V-formation", "Ant-trail"]

    def __init__(self, fps : int = 30, formation : str | None = "V-formation", ep_count : int = 5):
        super(FormationEnv, self).__init__()
        # Define metadata
        self.metadata = {"render_modes" : ["human", "rgb_array"], "render_fps" : fps, "tot_episodes" : ep_count}
        self.formation = formation
        self.episode = 1
        # Define a 2-D observation space
        self.observation_shape = (600, 800, 3)
        self.observation_space = spaces.Box(
            low=np.zeros(self.observation_shape),
            high=np.ones(self.observation_shape),
            dtype=np.float32
        )

        # Define an action space for straight
        self.action_space = spaces.Discrete(1)

        # Create a canvas to render the environment
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Initialize with empty dictionary for the current missile coordinates
        self.state = [{}]

        # Chopper boundaries
        self.y_min = 0
        self.x_min = 0
        self.y_max = self.observation_shape[0]
        self.x_max = self.observation_shape[1]
    
    def draw_elements_on_canvas(self):
        # Init the canvas
        self.canvas = np.ones(self.observation_shape, dtype=np.float32) * 1

        # Draw the helicopter on canvas
        for elem in self.elements:
            elem_shape = elem.icon.shape
            x,y = elem.x, elem.y
            self.canvas[y : y + elem_shape[1], x : x + elem_shape[0]] = elem.icon

        text = f'Episode: {self.episode} | Missiles Left: {len(self.state[0])}'

        # Put text on canvas
        self.canvas = cv2.putText(self.canvas, text, (10, 20), font, 0.8, (0,0,0), 1, cv2.LINE_AA)

    def reset(self):
        self.turret_count = 1
        self.elements = []

        # Initial formation location
        x = int(self.observation_shape[1] * 0.2)
        y = int(self.observation_shape[0] * 0.5)
        if self.formation == "V-formation":
            # Initialize the missiles
            missiles = [Missile("Missile_1", self.x_max, self.x_min, self.y_max, self.y_min),
                        Missile("Missile_2", self.x_max, self.x_min, self.y_max, self.y_min),
                        Missile("Missile_3", self.x_max, self.x_min, self.y_max, self.y_min)]
            missiles[0].set_position(x, y - 75)
            missiles[1].set_position(x + 100, y)
            missiles[2].set_position(x, y + 75)
        elif self.formation == "Ant-trail":
                # Initialize the missiles
            missiles = [Missile("Missile_1", self.x_max, self.x_min, self.y_max, self.y_min),
                        Missile("Missile_2", self.x_max, self.x_min, self.y_max, self.y_min),
                        Missile("Missile_3", self.x_max, self.x_min, self.y_max, self.y_min)]
            missiles[0].set_position(x - 75, y)
            missiles[1].set_position(x, y)
            missiles[2].set_position(x + 75, y)

        # Initialize turret
        spawned_turret = Turret(f"turret_{self.turret_count}", self.x_max, self.x_min, self.y_max, self.y_min)

        # Spawn a turret in a random location on the right-half of the screen
        turret_x = random.randrange(int(self.observation_shape[1] * 0.50), int(self.observation_shape[1]))
        turret_y = random.randrange(0, int(self.observation_shape[0]))
        spawned_turret.set_position(turret_x, turret_y)
        
        # Append the spawned turret to the elements currently present in Env. 
        self.elements.append(spawned_turret)
        
        # Store the elements
        self.missiles = missiles
        self.elements += self.missiles

        # Missile states
        self.state[0] = {missile.name : missile.get_position() for missile in self.missiles}

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
        # Flag that marks the termination of an episode
        done = False

        reward = 0

        [missile.move(3,0) for missile in self.missiles if missile in self.elements]

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
            if missile in self.elements:
                if missile.get_position()[0] + missile.icon_w >= self.x_max:
                    # TODO add Missile survived logic
                    self.elements.remove(missile)

        info = {"episode": self.episode, "state": self.state}

        # If all missiles are destroyed or reach the end of the screen, end the episode
        if len([elem for elem in self.elements if isinstance(elem, Missile)]) == 0:
            # If episode count is fulfilled, set done to True, else reset
            self.episode += 1
            info["episode"] += 1
            # Define default info object
            if self.episode > self.metadata["tot_episodes"]:
                done = True
                # Add data to info object
                info["data"] = None # FIXME add pandas dataframe
            else:
                self.reset()

        return self.canvas, reward, done, info
