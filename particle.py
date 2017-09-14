import numpy as np

axial_to_pixel_mat = np.array([[3 / 2., 0], [np.sqrt(3) / 2.0, np.sqrt(3)]])

class Particle(object):
    COLOR = (0, 0, 0)

    def __init__(self, axial_coordinates, id):
        self.axial_coordinates = np.array(axial_coordinates).astype(int)
        self.id = id

    def get_color(self):
        return Particle.COLOR

    def move(self, new_axial_coordinates):
        self.axial_coordinates = np.array(new_axial_coordinates).astype(int)

class Ant(Particle):
    def __init__(self, axial_coordinates, id):
        Particle.__init__(self, axial_coordinates, id)

class Food(Particle):
    COLOR = (0, 128, 0)

    def __init__(self, axial_coordinates, id):
        Particle.__init__(self, axial_coordinates, id)

    def get_color(self):
        return Food.COLOR
