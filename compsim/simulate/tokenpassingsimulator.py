import numpy as np

from . import CompressionSimulator, Direction, Ant, Food

BIAS_LOW = 1
BIAS_HIGH = 5
LOG_BASE = 1.05
SHIFT = (np.log(BIAS_HIGH - BIAS_LOW) / np.log(LOG_BASE)) + 1


class Token(object):
    def __init__(self, is_food, direction):
        self.is_food = is_food
        self.direction = direction


class TokenPassingSimulator(CompressionSimulator):
    def __init__(self, grid):
        CompressionSimulator.__init__(self, grid, 0)

    def add_food(self, food):
        self.grid.add_particle(food)

    def remove_food(self, food):
        self.grid.remove_particle(food)

    def get_bias(self, particle):
        return particle.bias

    def run_iterations(self, iterations, _=None):
        return CompressionSimulator.run_iterations(self, iterations, Ant)

    def move(self, random_particle, random_direction, probability, classes_to_move=None):
        # For now, just activate the random particle
        return self.activate(random_particle)

    def activate(self, particle):
        # First, generate new tokens if needed
        food_nbrs = self.grid.get_neighbors(particle.axial_coordinates, Food)
        if particle.food_direction is None and len(food_nbrs) > 0:
            direction = Direction(next(i for i, j in enumerate(food_nbrs) if j is not None))

            particle.food_direction = direction
            particle.token = Token(True, direction)
            print("Food token generated")

        elif particle.food_direction is not None and len(food_nbrs) == 0:
            particle.token = Token(False, particle.food_direction)
            particle.food_direction = None
            print("Not food token generated")

        # If it has a not food token when adjacent to food, change it to a food token
        if particle.token is not None and (not particle.token.is_food) and len(food_nbrs) > 0:
            particle.token.is_food = True
            particle.token.direction = particle.token.direction.shift_counterclockwise_by(1) # Note that this differs from the pseudocode since the directions increase in the opposite direction here
            print("Not food token converted to food due to adjacency")

        # Now forward the token
        particle_nbrs = self.grid.get_neighbors(particle.axial_coordinates, Ant, True)
        if particle.token is not None and particle.token.is_food:
            particle.bias = 4.0
            d, nbr = self.get_next_neighbor(particle_nbrs, particle.token.direction, False)  # Look clockwise

            if nbr.token is None:
                particle.token.direction = d.shift_counterclockwise_by(3)
                nbr.token = particle.token
                print("%d, %d -F---> %d, %d (%s)" % (particle.axial_coordinates[0], particle.axial_coordinates[1],
                                                     nbr.axial_coordinates[0], nbr.axial_coordinates[1], d.name))
            else:
                print("%d, %d -F-/-> %d, %d (%s)" % (particle.axial_coordinates[0], particle.axial_coordinates[1],
                                                     nbr.axial_coordinates[0], nbr.axial_coordinates[1], d.name))
            particle.token = None

            return True

        if particle.token is not None and (not particle.token.is_food):
            particle.bias = 1.0
            d, nbr = self.get_next_neighbor(particle_nbrs, particle.token.direction,
                                              True)  # Look counterclockwise

            if nbr.token is None:
                particle.token.direction = d.shift_counterclockwise_by(3)
                nbr.token = particle.token
                print("%d, %d -NF---> %d, %d (%s)" % (particle.axial_coordinates[0], particle.axial_coordinates[1],
                                                     nbr.axial_coordinates[0], nbr.axial_coordinates[1], d.name))
            elif nbr.token is not None and nbr.token.is_food:
                particle.token.direction = d.shift_counterclockwise_by(3)
                nbr.token = particle.token
                print("%d, %d -NF--->F %d, %d (%s)" % (particle.axial_coordinates[0], particle.axial_coordinates[1],
                                                     nbr.axial_coordinates[0], nbr.axial_coordinates[1], d.name))
            else:
                print("%d, %d -NF-/-> %d, %d (%s)" % (particle.axial_coordinates[0], particle.axial_coordinates[1],
                                                      nbr.axial_coordinates[0], nbr.axial_coordinates[1], d.name))

            particle.token = None
            return True

        return False

    def get_next_neighbor(self, neighbors, direction, counterclockwise):
        add = 1 if counterclockwise else -1

        current_direction = direction

        while True:
            current_direction = current_direction.shift_counterclockwise_by(add)

            n = neighbors[current_direction.value]
            if n is not None:
                return current_direction, n

    def get_metrics(self, _=None):
        metrics = CompressionSimulator.get_metrics(self, Ant)

        # TODO: Add any necessary metrics

        return metrics
