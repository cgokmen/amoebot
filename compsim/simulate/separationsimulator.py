import numpy as np
from enum import Enum

from . import CompressionSimulator, Direction, Particle, Grid

class ConnectivityRule(Enum):
    Strict = 0
    Interclass = 1
    Intraclass = 2
    Free = 3

class ColoredParticle(Particle):
    COLOR = (0, 0, 0)

    def get_color(self):
        return self.COLOR


class SeparationSimulator(CompressionSimulator):
    # bias_lambda is the overall compression bias as in the compressionsim
    # bias_alpha is the bias for homogeneous grouping: > 1 wants homogeneity
    def __init__(self, grid, bias_lambda, bias_alpha, connectivity_rule):
        CompressionSimulator.__init__(self, grid, bias_lambda)
        self.bias_alpha = bias_alpha
        self.connectivity_rule = connectivity_rule

        self.validate_grid(grid, self.connectivity_rule)

    @staticmethod
    def validate_grid(grid, connectivity_rule=ConnectivityRule.Free, particle_class=ColoredParticle):
        if len(grid.get_all_particles(particle_class)) != len(grid.get_all_particles()):
            raise ValueError("The configuration contains particles unsupported by SeparationSimulator")

        if connectivity_rule is ConnectivityRule.Strict or connectivity_rule is ConnectivityRule.Interclass:
            if not grid.particles_connected() or not grid.particle_holes():
                raise ValueError("The configuration does not satisfy the system-wide connectivity rules")

        if connectivity_rule is ConnectivityRule.Strict or connectivity_rule is ConnectivityRule.Intraclass:
            for sc in particle_class.__subclasses__():
                if not grid.particles_connected(sc) or not grid.particle_holes(sc):
                    raise ValueError("The configuration does not satisfy the class connectivity rules")

    def get_bias(self, particle):
        raise ValueError("No single bias in the Separation Simulator")

    def get_move_probability(self, particle, current_location, new_location):
        current_neighbors = set(self.grid.get_neighbors(current_location))
        new_neighbors = set(self.grid.get_neighbors(new_location)) - {particle}
        increase_neighbors = len(new_neighbors) - len(current_neighbors)

        current_homogeneous = sum(type(n) is type(particle) for n in current_neighbors)
        new_homogeneous = sum(type(n) is type(particle) for n in new_neighbors)
        increase_homogeneous = new_homogeneous - current_homogeneous

        return (self.bias ** increase_neighbors) * (self.bias_alpha ** increase_homogeneous)

    def valid_move(self, particle, old_position, new_position, direction):
        r = True

        if self.connectivity_rule is ConnectivityRule.Strict or self.connectivity_rule is ConnectivityRule.Interclass:
            a = self.grid.neighbor_count(old_position) < 5
            b = self.property1(old_position, new_position, direction)
            c = self.property2(old_position, new_position, direction)

            r = r and (a and (b or c))

        if self.connectivity_rule is ConnectivityRule.Strict or self.connectivity_rule is ConnectivityRule.Intraclass:
            ptype = type(particle)

            a1 = self.grid.neighbor_count(old_position, ptype) < 5
            b1 = self.property1(old_position, new_position, direction, ptype)
            c1 = self.property2(old_position, new_position, direction, ptype)

            r = r and (a1 and (b1 or c1))

        return r

    def get_metrics(self, classes_to_move=None):
        metrics = []

        metrics.append(("Lambda bias", "%.2f", self.bias))
        metrics.append(("Alpha bias", "%.2f", self.bias_alpha))
        metrics.append(("Connectivity rule", "%s", self.connectivity_rule.name))
        metrics.append(("Iterations", "%d", self.iterations_run))
        metrics.append(("Movements made", "%d", self.movements))
        metrics.append(("Rounds completed:", "%d", self.rounds))
        #metrics.append(("Perimeter", "%%d", self.grid.calculate_perimeter(classes_to_move)))
        metrics.append(("Center of mass", "x = %.2f, y = %.2f", tuple(self.grid.find_center_of_mass(ColoredParticle))))
        #metrics.append(("Red center of mass", "x = %.2f, y = %.2f", tuple(self.grid.find_center_of_mass(RedParticle))))
        #metrics.append(("Blue center of mass", "x = %.2f, y = %.2f", tuple(self.grid.find_center_of_mass(BlueParticle))))
        #metrics.append(("Green center of mass", "x = %.2f, y = %.2f", tuple(self.grid.find_center_of_mass(GreenParticle))))

        neighborhoods = self.grid.count_neighborhoods()
        heterogeneous_neighborhoods = self.grid.count_heterogeneous_neighborhoods()
        homogeneous_neighborhoods = neighborhoods - heterogeneous_neighborhoods

        metrics.append(("Total neighborhoods", "%d", neighborhoods))
        metrics.append(("Homogeneous neighborhoods", "%d", homogeneous_neighborhoods))
        metrics.append(("Heterogeneous neighborhoods", "%d", heterogeneous_neighborhoods))

        return metrics
