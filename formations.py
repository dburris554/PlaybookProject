from components import Missile

class Basic_Formation():
    def __init__(self, name : str, id : int, max_x : int, max_y : int, coords : list[tuple]):
        self.name = name
        self.id = id
        self.missile_lookup = {}
        self.missile_count = len(coords)
        for i in range(self.missile_count):
            m = Missile(f"Missile {i+1}", max_x, 0, max_y, 0)
            coord = coords[i]
            m.set_position(coord[0], coord[1])
            self.missile_lookup[m.name] = m
    
    def get_missiles(self):
        return self.missile_lookup.values()

    def move_forward(self):
        for missile in self.missile_lookup.values():
            if missile.alive:
                missile.move(10,0)

class V3(Basic_Formation):
    id = 1
    coordinates = [(160, 300-50), (160+75, 300), (160, 300+50)]
    def __init__(self, name="V3", id=id, max_x=800, max_y=600, coords=coordinates):
        super().__init__(name, id, max_x, max_y, coords)

class V4(Basic_Formation):
    id = 4
    coordinates = [(170, 300-25), (170, 300+25), (170-50, 300-75), (170-50, 300+75)]
    def __init__(self, name="V4", id=id, max_x=800, max_y=600, coords=coordinates):
        super().__init__(name, id, max_x, max_y, coords)

class Flock8(Basic_Formation):
    id = 8
    coordinates = [(160+50, 300), (160, 300-50), (160, 300+50), (160-25, 300), 
        (160-50, 300-30), (160-50, 300+30), (160-40, 300-75), (160-40, 300+75)]
    def __init__(self, name="Flock8", id=id, max_x=800, max_y=600, coords=coordinates):
        super().__init__(name, id, max_x, max_y, coords)
    
class Ant3(Basic_Formation):
    id = 2
    coordinates = [(160-75, 300), (160, 300), (160+75, 300)]
    def __init__(self, name="Ant3", id=id, max_x=800, max_y=600, coords=coordinates):
        super().__init__(name, id, max_x, max_y, coords)

class Marching2(Basic_Formation):
    id = 7
    coordinates = [(160, 300-40), (160, 300+35)]
    def __init__(self, name="Marching2", id=id, max_x=800, max_y=600, coords=coordinates):
        super().__init__(name, id, max_x, max_y, coords)

class Marching3(Basic_Formation):
    id = 3
    coordinates = [(160, 300-75), (160, 300), (160, 300+75)]
    def __init__(self, name="Marching3", id=id, max_x=800, max_y=600, coords=coordinates):
        super().__init__(name, id, max_x, max_y, coords)

class Marching4(Basic_Formation):
    id = 5
    coordinates = [(160, 300-75), (160, 300), (160, 300+75), (160, 300+150)]
    def __init__(self, name="Marching4", id=id, max_x=800, max_y=600, coords=coordinates):
        super().__init__(name, id, max_x, max_y, coords)

class Marching5(Basic_Formation):
    id = 6
    coordinates = [(160, 300-150), (160, 300-75), (160, 300), (160, 300+75), (160, 300+150)]
    def __init__(self, name="Marching5", id=id, max_x=800, max_y=600, coords=coordinates):
        super().__init__(name, id, max_x, max_y, coords)
