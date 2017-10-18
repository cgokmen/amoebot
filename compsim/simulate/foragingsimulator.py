import numpy as np

from . import CompressionSimulator, Direction, Particle

BIAS_LOW = 1
BIAS_HIGH = 5
LOG_BASE = 1.05
SHIFT = (np.log(BIAS_HIGH - BIAS_LOW) / np.log(LOG_BASE)) + 1


class Ant(Particle):
    def __init__(self, axial_coordinates, id):
        Particle.__init__(self, axial_coordinates, id)

        self.token = None
        self.food_direction = None

        self.bias = 1

    def get_color(self):
        if self.token is not None:
            if self.token.is_food:
                return (128, 0, 128)
            else:
                return (0, 128, 128)

        clr = int((self.bias - 1) * 64 - 1)
        return 255 - clr, clr, 0


class Food(Particle):
    COLOR = (0, 0, 128)

    def __init__(self, axial_coordinates, id):
        Particle.__init__(self, axial_coordinates, id)

    def get_color(self):
        return Food.COLOR


class UndiscoveredFood(Food):
    def get_discovered(self):
        return DiscoveredFood(self.axial_coordinates, id)


class DiscoveredFood(Food):
    COLOR = (128, 128, 0)

    def get_color(self):
        return DiscoveredFood.COLOR


class ForagingSimulator(CompressionSimulator):
    def __init__(self, grid):
        CompressionSimulator.__init__(self, grid, 0)

        self._bias_array = np.full([self.grid.width + 1, self.grid.height + 1], BIAS_HIGH, dtype=float)
        self.food_found = False

    @staticmethod
    def is_grid_valid(grid):
        return grid.particles_connected(Ant) and grid.particle_holes()

    def add_food(self, food):
        self.grid.add_particle(food)
        self.recalculate_distances_to_food()

    def remove_food(self, food):
        self.grid.remove_particle(food)
        self.recalculate_distances_to_food()

    def recalculate_distances_to_food(self):
        food_positions = [p.axial_coordinates for p in self.grid.get_all_particles(Food)]

        if len(food_positions) == 0:
            self._bias_array = np.full([self.grid.width + 1, self.grid.height + 1], BIAS_HIGH, dtype=float)
            return

        # food_bias_arrays = []
        food_bias_arrays = np.full([len(food_positions), self.grid.width + 1, self.grid.height + 1], BIAS_LOW,
                                   dtype=float)

        for k in xrange(len(food_positions)):
            food_position = food_positions[k]
            food_bias_arrays[k, food_position[0] + self.grid.max[0], food_position[1] + self.grid.max[1]] = BIAS_HIGH

        current_radius = 0
        while True:
            current_radius += 1
            current_bias = np.power(LOG_BASE, - current_radius + SHIFT) + 1

            current_vector = np.array(
                Direction.SW.axial_vector()) * current_radius  # Start SW so that the first move is 0 (SE)

            noneInBounds = True

            for i in xrange(6):
                for j in xrange(current_radius):
                    for k in xrange(len(food_positions)):
                        food_position = food_positions[k]
                        current_position = food_position + current_vector

                        if self.grid.is_position_in_bounds(current_position):
                            # print(current_bias)
                            food_bias_arrays[
                                k, current_position[0] + self.grid.max[0], current_position[1] + self.grid.max[
                                    1]] = current_bias
                            noneInBounds = False

                    current_vector += np.array(Direction(i).axial_vector())

            if noneInBounds:
                break

        # for a in food_bias_arrays:
        #    self._bias_array = np.maximum(self._bias_array, a)

        self._bias_array = food_bias_arrays.max(axis=0)

    def get_bias(self, particle):
        particle_coords = particle.axial_coordinates

        # TODO: There ought to be a better way of doing this!
        bias = self._bias_array[particle_coords[0] + self.grid.max[0], particle_coords[1] + self.grid.max[1]]

        return bias if self.food_found else 6 - bias

    def run_iterations(self, iterations, _=None):
        # TODO: Maybe make food disappear here
        return CompressionSimulator.run_iterations(self, iterations, Ant)

    def move(self, random_particle, random_direction, probability, _=None):
        m = CompressionSimulator.move(self, random_particle, random_direction, probability, Ant)

        if m:
            neighbors = self.grid.get_neighbors(random_particle.axial_coordinates, UndiscoveredFood)
            if len(neighbors) > 0:
                # HOORAY, FOOD!
                print("Food has been discovered.")
                self.food_found = True

                for food in neighbors:
                    discovered_food = food.get_discovered()

                    self.grid.remove_particle(food)
                    self.grid.add_particle(discovered_food)

        return m

    def valid_move(self, old_position, new_position, direction):
        if self.grid.neighbor_count(old_position, Food) > 0:
            # Adjacent to food? Don't move
            return False

        return self.grid.neighbor_count(old_position) < 5 and (
        self.property1(old_position, new_position, direction, Ant) or self.property2(old_position, new_position,
                                                                                     direction, Ant)) and (
               self.property1(old_position, new_position, direction, (Ant, DiscoveredFood)) or self.property2(
                   old_position, new_position, direction, (Ant, DiscoveredFood)))

    def get_metrics(self, _=None):
        metrics = CompressionSimulator.get_metrics(self, Ant)

        # TODO: Add any necessary metrics

        return metrics
