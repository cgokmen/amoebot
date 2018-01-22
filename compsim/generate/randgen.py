import numpy as np
import random

from compsim.simulate import Grid, ColoredParticle, NewSeparationSimulator
from compsim.io import BRIGHT_COLORS

def generate_random_grid(n_particles, simulator_type, weighted_particle_types, size=None):
    # weighted particle types is a list of particle types in (single-param initializer, weight) format

    if n_particles <= 0:
        raise ValueError("At least 1 particle needs to be generated.")

    if size is None:
        width_height = int(n_particles ** 0.5) * 4
        size = (width_height, width_height)

    grid = Grid(size)
    print "Initialized a grid of size %d, %d" % size

    total_weight = float(sum(wp[1] for wp in weighted_particle_types))

    # Choose the classes for our particles:
    particle_types = list(np.random.choice([wt[0] for wt in weighted_particle_types], n_particles, True, [wt[1] / total_weight for wt in weighted_particle_types]))

    # Manually add the first particle at the center
    p_init = particle_types.pop(0)
    particle = p_init((0, 0), 0)

    grid.add_particle(particle)

    try:
        simulator_type.validate_grid(grid)
    except:
        raise ValueError("The simulation should allow starting at the middle.")

    i = 1
    for particle_type in particle_types:
        while True:
            # Choose a random position for the particle
            coords = random.choice(grid.get_valid_empty_neighborhoods())

            particle = particle_type(coords, i)

            grid.add_particle(particle)

            try:
                simulator_type.validate_grid(grid)
            except:
                grid.remove_particle(particle)
                continue

            print "Successfully inserted %s #%d" % (type(particle).__name__, i)
            i += 1
            break

    print "Random grid generation successful"
    return grid

def generate_random_separation_grid(n_particles, n_classes, size=None, simulator_type=NewSeparationSimulator, base_class=ColoredParticle, colors=BRIGHT_COLORS):
    classes = [(type('ColoredParticle_%d' % index, (base_class,), {'COLOR': colors[index]}), 1.0 / n_classes) for index in xrange(n_classes)]

    return generate_random_grid(n_particles, simulator_type, classes, size)