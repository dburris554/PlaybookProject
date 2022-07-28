import cv2
import random

class Point(object):
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

def has_collided(elem1, elem2):
    x_col = False
    y_col = False

    elem1_x, elem1_y = elem1.get_position()
    elem2_x, elem2_y = elem2.get_position()

    if elem1_x <= elem2_x:
        if elem1_x + elem1.icon_w - 1 >= elem2_x:
            x_col = True
    elif elem1_x > elem2_x:
        if elem2_x + elem2.icon_w - 1 >= elem1_x:
            x_col = True

    if elem1_y <= elem2_y:
        if elem1_y + elem1.icon_h - 1 >= elem2_y:
            y_col = True
    elif elem1_y > elem2_y:
        if elem2_y + elem2.icon_h - 1 >= elem1_y:
            y_col = True
        
    if x_col and y_col:
        return True

    return False

class Missile(Point):
    def __init__(self, name, x_max, x_min, y_max, y_min):
        super().__init__(name, x_max, x_min, y_max, y_min)
        self.icon = cv2.imread('Missile.png') / 255.0
        self.icon_w = 64
        self.icon_h = 12
        self.icon = cv2.resize(self.icon, (self.icon_w, self.icon_h))
        self.alive = True

    def kill(self):
        self.alive = False

class Turret(Point):
    def __init__(self, name, x_max, x_min, y_max, y_min):
        super().__init__(name, x_max, x_min, y_max, y_min)
        self.icon = cv2.imread("Turret.png") / 255.0
        self.icon_w = 64
        self.icon_h = 64
        self.icon = cv2.resize(self.icon, (self.icon_w, self.icon_h))

def create_turret(env, id, x, y):
    # Initialize turret
    spawned_turret = Turret(f"turret_{id}", env.x_max, env.x_min, env.y_max, env.y_min)

    # Set turret position
    spawned_turret.set_position(x, y)

    return spawned_turret

def create_rand_turret(env, id, x_minp, x_maxp, y_minp, y_maxp):
    # Initialize turret
    spawned_turret = Turret(f"turret_{id}", env.x_max, env.x_min, env.y_max, env.y_min)

    # Spawn a turret in a random location on the right-half of the screen
    turret_x = random.randrange(int(env.observation_shape[1] * x_minp), int(env.observation_shape[1] * x_maxp))
    turret_y = random.randrange(int(env.observation_shape[0] * y_minp), int(env.observation_shape[0] * y_maxp))
    spawned_turret.set_position(turret_x, turret_y)

    return spawned_turret

class Target(Point):
    def __init__(self, name, x_max, x_min, y_max, y_min):
        super().__init__(name, x_max, x_min, y_max, y_min)
        self.icon = cv2.imread("target.png") / 255.0
        self.icon_w = 40
        self.icon_h = 600
        self.icon = cv2.resize(self.icon, (self.icon_w, self.icon_h))
        self.x = 760
        self.y = 0