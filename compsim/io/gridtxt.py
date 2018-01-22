import colorsys

import numpy as np
import collections

from compsim.simulate import Grid, Particle, ColoredParticle

LEGACY_MATRIX = np.array([[1, 0], [0, -1]])

BRIGHT_COLORS = [
    (230, 25, 75),
    (60, 180, 75),
    (255, 225, 25),
    (0, 130, 200),
    (0, 0, 0),
    (145, 30, 180),
    (70, 240, 240),
    (240, 50, 230),
    (210, 245, 60),
    (250, 190, 190),
    (0, 128, 128),
    (230, 190, 255),
    (170, 110, 40),
    (255, 250, 200),
    (128, 0, 0),
    (170, 255, 195),
    (128, 128, 0),
    (255, 215, 180),
    (0, 0, 128),
    (128, 128, 128),
    (245, 130, 48)
]

GREYSCALE_COLORS = [
    (200, 200, 200),
    (0, 0, 0),
    (100, 100, 100)
]

def compression_simulator_grid_loader(filename, legacy=False, particle_types=(Particle,)):
    f = open(filename, "r")

    size = np.array(map(int, f.readline().split()))
    #print("Grid size: %d x %d" % (size[0], size[1]))
    grid = Grid(size)

    if np.any(size % 2 != 0):
        raise ValueError("Width and height need to be even.")

    num_particles = int(f.readline())

    for n in range(num_particles):
        datum = map(int, f.readline().split())

        position = np.array((datum[0], datum[1]))
        ptype = 0 if len(datum) < 3 else datum[2]

        if legacy:
            position -= size / 2
            position = LEGACY_MATRIX.dot(position)
            # position[1] = -position[0] - position[1]

        particle = particle_types[ptype](position, n)

        grid.add_particle(particle)

    #print("Loaded %s successfully" % filename)

    return grid

def separation_simulator_grid_loader(filename, base_class=ColoredParticle, colors=BRIGHT_COLORS):
    f = open(filename, "r")

    size = np.array(map(int, f.readline().split()))
    #print("Grid size: %d x %d" % (size[0], size[1]))
    grid = Grid(size)

    if np.any(size % 2 != 0):
        raise ValueError("Width and height need to be even.")

    num_particles = int(f.readline())

    particle_data = []
    particle_classes = {}

    for n in range(num_particles):
        data = map(int, f.readline().split())
        position = np.array([data[0], data[1]])

        particle_data.append((position, data[2]))
        particle_classes[data[2]] = True

    # Generate the classes!
    for index, id in enumerate(particle_classes.keys()):
        col = colors[index]

        subclass = type('ColoredParticle_%d' % id, (base_class,), {'COLOR': col})
        particle_classes[id] = subclass

    # Add the particles
    for key, item in enumerate(particle_data):
        grid.add_particle(particle_classes[item[1]](item[0], key))

    #print("Loaded %s successfully" % filename)

    return grid

def separation_simulator_grid_saver(filename, grid):
    with open(filename, 'w') as f:
        particles = grid.get_all_particles()
        classes_ids = dict()
        curr_id = 0

        f.write("%d %d\n" % tuple(grid.size))
        f.write("%d\n" % len(particles))

        for particle in particles:
            cls = type(particle)
            coords = particle.axial_coordinates

            if cls not in classes_ids:
                classes_ids[cls] = curr_id
                curr_id += 1

            f.write("%d %d %d\n" % (coords[0], coords[1], classes_ids[cls]))