# We're just being punny here, this is the same SeparationSimulator except it does not allow
# particles to disconnect with their original same-class neighbors.

from . import SeparationSimulator, ColoredParticle, ConnectivityRule

class WormParticle(ColoredParticle):
    def __init__(self, axial_coordinates, id):
        ColoredParticle.__init__(self, axial_coordinates, id)

        self.bound_to = set()


class WormTheorySimulator(SeparationSimulator):
    def __init__(self, grid, bias_lambda, bias_alpha):
        SeparationSimulator.__init__(self, grid, bias_lambda, bias_alpha, ConnectivityRule.Strict)

        # We want to bind the initial particles together.
        for particle in grid.get_all_particles():
            particle.bound_to = set(grid.get_neighbors(particle.axial_coordinates, type(particle)))

    def valid_move(self, particle, old_position, new_position, direction):
        # Check if the particle would still be connected to all of its neighbors in its new position
        neighborsOfPosition = set(self.grid.get_neighbors(new_position, type(particle))) - {particle}

        for nbr in particle.bound_to:
            if nbr not in neighborsOfPosition:
                return False

        #if neighborsOfPosition != particle.bound_to:
        #    return False

        return SeparationSimulator.valid_move(self, particle, old_position, new_position, direction)

    @staticmethod
    def validate_grid(grid, dont_care=None, dont_care2=None):
        SeparationSimulator.validate_grid(grid, ConnectivityRule.Strict, WormParticle)