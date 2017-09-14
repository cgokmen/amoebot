from grid import Grid
from particle import Particle
import numpy as np

LEGACY_MATRIX = np.array([[1, 0], [0, -1]])

def compression_simulator_grid_loader(filename, legacy=False, particle_type = Particle):
    f = open(filename, "r")

    size = np.array(map(int, f.readline().split()))
    print("Grid size: %d x %d" % (size[0], size[1]))
    grid = Grid(size)

    if np.any(size % 2 != 0):
        raise ValueError("Width and height need to be even.")

    num_particles = int(f.readline())

    for n in range(num_particles):
        position = np.array(map(int, f.readline().split()))

        if legacy:
            position -= size / 2
            position = LEGACY_MATRIX.dot(position)
            #position[1] = -position[0] - position[1]

        particle = particle_type(position, n)

        grid.add_particle(particle)

    print("Loaded %s successfully" % filename)

    return grid
