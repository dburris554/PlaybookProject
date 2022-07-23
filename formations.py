from components import Missile

class Basic_Formation():
    def __init__(self, name : str, max_x : int, max_y : int, coords : list[tuple]):
        self.name = name
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
                missile.move(5,0)

class V_formation(Basic_Formation):
    coordinates = [(160, 300-75), (160+100, 300), (160, 300+75)]
    def __init__(self, name="V_formation", max_x=800, max_y=600, coords=coordinates):
        super().__init__(name, max_x, max_y, coords)
    
class Ant_trail(Basic_Formation):
    coordinates = [(160-75, 300), (160, 300), (160+75, 300)]
    def __init__(self, name="Ant_trail", max_x=800, max_y=600, coords=coordinates):
        super().__init__(name, max_x, max_y, coords)
