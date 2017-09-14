from compressionsimulator import CompressionSimulator
import numpy as np
from particle import Particle, Ant, Food
from grid import Direction

BIAS_LOW = 1
BIAS_HIGH = 5
LOG_BASE = 1.05
SHIFT = (np.log(BIAS_HIGH - BIAS_LOW) / np.log(LOG_BASE)) + 1

class ForagingSimulator(CompressionSimulator):
    def __init__(self, grid):
        CompressionSimulator.__init__(self, grid, 0)

        self._bias_array = np.full([self.grid.width + 1, self.grid.height + 1], BIAS_HIGH, dtype=float)

    def add_food(self, food):
        self.grid.add_particle(food)
        self.recalculate_distances_to_food()

    def remove_food(self, food):
        self.grid.remove_particle(food)
        self.recalculate_distances_to_food()

    def recalculate_distances_to_food(self):
        food_positions = [p.axial_coordinates for p in self.grid.get_all_particles_by_direct_class(Food)]

        if len(food_positions) == 0:
            self._bias_array = np.full([self.grid.width + 1, self.grid.height + 1], BIAS_HIGH, dtype=float)
            return

        food_bias_arrays = []

        for food_position in food_positions:
            food_bias_array = np.full([self.grid.width + 1, self.grid.height + 1], BIAS_LOW, dtype=float)
            food_bias_array[tuple(food_position + self.grid.max)] = BIAS_HIGH
            food_bias_arrays.append(food_bias_array)

        current_radius = 0
        while True:
            current_radius += 1
            current_bias = np.power(LOG_BASE, - current_radius + SHIFT) + 1

            current_vector = np.array(Direction.SW.axial_vector()) * current_radius  # Start SW so that the first move is 0 (SE)

            noneInBounds = True

            for i in xrange(6):
                for j in xrange(current_radius):
                    for k in xrange(len(food_positions)):
                        food_position = food_positions[k]
                        current_position = food_position + current_vector

                        if self.grid.is_position_in_bounds(current_position):
                            #print(current_bias)
                            food_bias_arrays[k][tuple(current_position + self.grid.max)] = current_bias
                            noneInBounds = False

                    current_vector += np.array(Direction(i).axial_vector())

            if noneInBounds:
                break

        for a in food_bias_arrays:
            self._bias_array = np.maximum(self._bias_array, a)

    def get_bias(self, particle):
        particle_coords = particle.axial_coordinates
        bias = self._bias_array[particle_coords[0] + self.grid.max[0], particle_coords[1] + self.grid.max[1]]
        return bias

    def run_iterations(self, iterations, _ = None):
        # TODO: Maybe make food disappear here
        return CompressionSimulator.run_iterations(self, iterations, Ant)

    def move(self, random_particle, random_direction, probability, _ = None):
        return CompressionSimulator.move(self, random_particle, random_direction, probability, Ant)

    def valid_move(self, old_position, new_position, direction):
        a = self.grid.neighbor_count(old_position) < 5

        b1 = self.property1(old_position, new_position, direction)
        c1 = self.property2(old_position, new_position, direction)

        b2 = self.property1(old_position, new_position, direction, Ant)
        c2 = self.property2(old_position, new_position, direction, Ant)

        if b1 and b2:
            self.property1_count += 1
        if c1 and c2:
            self.property2_count += 1

        return a and (b1 or c1) and (b2 or c2)

    def get_metrics(self, _ = None):
        metrics = CompressionSimulator.get_metrics(self, Ant)

        # TODO: Add any necessary metrics

        return metrics