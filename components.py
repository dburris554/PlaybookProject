import cv2

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