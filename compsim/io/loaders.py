import colorsys

import numpy as np
import collections

from compsim.simulate import Grid, Particle, ColoredParticle

LEGACY_MATRIX = np.array([[1, 0], [0, -1]])

HUE_RANGE = (0, 300/float(360))

SOME_COLORS = [
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

def separation_simulator_grid_loader(filename, legacy=False):
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

        if legacy:
            position -= size / 2
            position = LEGACY_MATRIX.dot(position)
            # position[1] = -position[0] - position[1]

        particle_data.append((position, data[2]))
        particle_classes[data[2]] = True

    # Generate the classes!
    count_classes = len(particle_classes)
    HSV_tuples = [(x * 1.0 / count_classes, 0.5, 0.5) for x in range(count_classes)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    RGB_tuples = [tuple(int(x * 255) for x in rgb) for rgb in RGB_tuples]
    for index, id in enumerate(particle_classes.keys()):
        hue = HUE_RANGE[0] + (HUE_RANGE[1] - HUE_RANGE[0]) * (index / count_classes)
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)

        col = SOME_COLORS[index]

        subclass = type('ColoredParticle_%d' % id, (ColoredParticle,), {'COLOR': col})
        particle_classes[id] = subclass

    # Add the particles
    for key, item in enumerate(particle_data):
        grid.add_particle(particle_classes[item[1]](item[0], key))

    #print("Loaded %s successfully" % filename)

    return grid
