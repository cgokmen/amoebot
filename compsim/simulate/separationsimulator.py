import numpy as np
from enum import Enum

from . import CompressionSimulator, Direction, Particle

class ConnectivityRule(Enum):
    Strict = 0
    Interclass = 1
    Intraclass = 2
    Free = 3

class ColoredParticle(Particle):
    pass


class RedParticle(ColoredParticle):
    def get_color(self):
        return 255, 0, 0


class GreenParticle(ColoredParticle):
    def get_color(self):
        return 0, 255, 0


class BlueParticle(ColoredParticle):
    def get_color(self):
        return 0, 0, 255


class SeparationSimulator(CompressionSimulator):
    # bias_lambda is the overall compression bias as in the compressionsim
    # bias_alpha is the bias for homogeneous grouping: > 1 wants homogeneity
    def __init__(self, grid, bias_lambda, bias_alpha, connectivity_rule):
        CompressionSimulator.__init__(self, grid, bias_lambda)
        self.bias_alpha = bias_alpha
        self.connectivity_rule = connectivity_rule
        self.bias_beta = 1.0 / bias_alpha

        if not self.is_grid_valid(grid, self.connectivity_rule):
            raise ValueError("This grid is not valid for this problem")

    @staticmethod
    def is_grid_valid(grid, connectivity_rule=ConnectivityRule.Free):
        if connectivity_rule is ConnectivityRule.Strict or connectivity_rule is ConnectivityRule.Interclass:
            if not grid.particles_connected() or not grid.particle_holes():
                return False

        if connectivity_rule is ConnectivityRule.Strict or connectivity_rule is ConnectivityRule.Intraclass:
            for sc in ColoredParticle.__subclasses__():
                if not grid.particles_connected(sc) or not grid.particle_holes(sc):
                    return False

        return True

    def get_bias(self, particle):
        raise ValueError("No single bias in the Separation Simulator")

    def get_move_probability(self, particle, current_location, new_location):
        current_neighbors = set(self.grid.get_neighbors(current_location))
        new_neighbors = set(self.grid.get_neighbors(new_location)) - {particle}
        increase_neighbors = len(new_neighbors) - len(current_neighbors)

        current_homogeneous = sum(type(n) is type(particle) for n in current_neighbors)
        current_heterogeneous = len(current_neighbors) - current_homogeneous

        new_homogeneous = sum(type(n) is type(particle) for n in new_neighbors)
        new_heterogeneous = len(new_neighbors) - new_homogeneous

        increase_homogeneous = new_homogeneous - current_homogeneous
        increase_heterogeneous = new_heterogeneous - current_heterogeneous

        return (self.bias ** increase_neighbors) * (self.bias_alpha ** increase_homogeneous) * (self.bias_beta ** increase_heterogeneous)

    def valid_move(self, old_position, new_position, direction):
        r = True

        if self.connectivity_rule is ConnectivityRule.Strict or self.connectivity_rule is ConnectivityRule.Interclass:
            a = self.grid.neighbor_count(old_position) < 5
            b = self.property1(old_position, new_position, direction)
            c = self.property2(old_position, new_position, direction)

            r = r and (a and (b or c))

        if self.connectivity_rule is ConnectivityRule.Strict or self.connectivity_rule is ConnectivityRule.Intraclass:
            p = self.grid.get_particle(old_position)
            ptype = type(p)

            a1 = self.grid.neighbor_count(old_position, ptype) < 5
            b1 = self.property1(old_position, new_position, direction, ptype)
            c1 = self.property2(old_position, new_position, direction, ptype)

            r = r and (a1 and (b1 or c1))

        return r

    def get_metrics(self, classes_to_move=None):
        metrics = []

        metrics.append(("Lambda bias", "%%.2f", self.bias))
        metrics.append(("Alpha bias", "%%.2f", self.bias_alpha))
        metrics.append(("Connectivity rule", "%%s", self.connectivity_rule.name))
        metrics.append(("Iterations", "%%d", self.iterations_run))
        metrics.append(("Movements made", "%%d", self.movements))
        metrics.append(("Rounds completed:", "%%d", self.rounds))
        metrics.append(("Perimeter", "%%d", self.grid.calculate_perimeter(classes_to_move)))
        metrics.append(("Center of mass", "x = %%.2f, y = %%.2f", tuple(self.grid.find_center_of_mass(classes_to_move))))

        return metrics
