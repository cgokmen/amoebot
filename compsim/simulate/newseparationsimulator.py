# coding=utf-8

from . import CompressionSimulator, ColoredParticle, Directions


class NewSeparationSimulator(CompressionSimulator):
    # bias_lambda is the overall compression bias as in the compressionsim
    # bias_alpha is the bias for homogeneous grouping: > 1 wants homogeneity
    def __init__(self, grid, bias_lambda, bias_alpha, allow_swap=True):
        CompressionSimulator.__init__(self, grid, bias_lambda)
        self.bias_alpha = bias_alpha
        self.allow_swap = allow_swap

    @staticmethod
    def validate_grid(grid, particle_class=ColoredParticle):
        if len(list(grid.get_all_particles(particle_class))) != len(list(grid.get_all_particles())):
            raise ValueError("The configuration contains particles unsupported by NewSeparationSimulator")

        return CompressionSimulator.validate_grid(grid)

    def get_bias(self, particle):
        raise ValueError("No single bias in the NewSeparationSimulator")

    def get_move_probability(self, particle, current_location, new_location):
        current_neighbors = set(self.grid.get_neighbors(current_location))
        new_neighbors = set(self.grid.get_neighbors(new_location)) - {particle}
        increase_neighbors = len(new_neighbors) - len(current_neighbors)

        current_homogeneous = sum(type(n) is type(particle) for n in current_neighbors)
        new_homogeneous = sum(type(n) is type(particle) for n in new_neighbors)
        increase_homogeneous = new_homogeneous - current_homogeneous

        return (self.bias ** increase_neighbors) * (self.bias_alpha ** increase_homogeneous)

    def move(self, random_particle, random_direction, probability, classes_to_move=None):
        # Check if new location is empty
        current_location = random_particle.axial_coordinates
        new_location = self.grid.get_position_in_direction(current_location, random_direction)

        if not self.grid.is_position_in_bounds(new_location):
            # New location out of board bounds
            # print("Bounds")
            return False

        if not self.valid_move(random_particle, current_location, new_location,
                               random_direction):  # TODO: Check classes to move?
            # print("Invalid")
            return False

        prob_move = 1

        swap_particle = self.grid.get_particle(new_location)

        if swap_particle is not None:
            if not self.allow_swap:
                return False

            sp_type = type(swap_particle)

            if sp_type == type(random_particle):
                # We can only swap particles of different colors
                return False

            prob_move *= self.get_move_probability(swap_particle, new_location, current_location)

        prob_move *= self.get_move_probability(random_particle, current_location, new_location)
        # print("Prob: " + str(prob_move))
        self.probability_series.append(prob_move)

        if not probability < prob_move:  # Choose with probability
            # print probability
            return False

        # Empty the swap location if we're swapping
        if swap_particle is not None:
            self.grid.remove_particle(swap_particle)

        # Move the random particle
        self.grid.move_particle(current_location, new_location)

        # Move and reinsert the swap particle
        if swap_particle is not None:
            swap_particle.move(current_location)
            self.grid.add_particle(swap_particle)

        # Movement counting
        self.movements += 1

        # Round checking
        self.visited[random_particle] = True
        for particle in self.grid.get_all_particles(classes_to_move):
            if not self.visited.get(particle, False):
                return True

        # If this point is reached, a round has completed
        self.rounds += 1
        self.visited = {}

        return True

    #def valid_move(self, particle, old_position, new_position, direction):
    #    ptype = type(particle)

    #    n = self.grid.neighbor_count(old_position, ptype) < 5

    #    p1 = True #self.property1(old_position, new_position, direction, ptype)
    #    p2 = True #self.new_property2(old_position, new_position, direction, ptype)

    #    p3 = True self.property1(old_position, new_position, direction)
    #    p4 = True self.property2(old_position, new_position, direction)

    #    return n and (p1 or p2) and (p3 or p4)

    # def new_property2(self, old_position, new_position, direction, classes_to_consider=None):
    #     # This is the same property 2 as before, but the non-empty neighborhood
    #     # requirement is removed.
    #     s1 = self.grid.get_neighbor_in_direction(old_position, Directions.shift_counterclockwise_by(direction, 5),
    #                                              classes_to_consider)
    #     s2 = self.grid.get_neighbor_in_direction(old_position, Directions.shift_counterclockwise_by(direction, 1),
    #                                              classes_to_consider)
    #
    #     if s1 is None and s2 is None:
    #         if (self.grid.get_neighbor_in_direction(old_position, Directions.shift_counterclockwise_by(direction, 2),
    #                                                 classes_to_consider) is not None
    #             ) and (
    #                     self.grid.get_neighbor_in_direction(old_position, Directions.shift_counterclockwise_by(direction, 3),
    #                                                         classes_to_consider) is None
    #         ) and (
    #                     self.grid.get_neighbor_in_direction(old_position, Directions.shift_counterclockwise_by(direction, 4),
    #                                                         classes_to_consider) is not None
    #         ):
    #             return False
    #
    #         if (self.grid.get_neighbor_in_direction(new_position, Directions.shift_counterclockwise_by(direction, 1),
    #                                                 classes_to_consider) is not None
    #             ) and (
    #                     self.grid.get_neighbor_in_direction(new_position, Directions.shift_counterclockwise_by(direction, 0),
    #                                                         classes_to_consider) is None
    #         ) and (
    #                     self.grid.get_neighbor_in_direction(new_position, Directions.shift_counterclockwise_by(direction, 5),
    #                                                         classes_to_consider) is not None
    #         ):
    #             return False
    #
    #         return True
    #     else:
    #         return False

    def get_metrics(self, classes_to_move=None):
        neighborhoods = self.grid.count_neighborhoods()
        heterogeneous_neighborhoods = self.grid.count_heterogeneous_neighborhoods()
        homogeneous_neighborhoods = neighborhoods - heterogeneous_neighborhoods

        metrics = [("Lambda bias", "%.2f", self.bias),
                   ("Alpha bias", "%.2f", self.bias_alpha),
                   ("Iterations", "%d", self.iterations_run),
                   ("Movements made", "%d", self.movements),
                   ("Rounds completed:", "%d", self.rounds),
                   ("Center of mass", "x = %.2f, y = %.2f", tuple(self.grid.find_center_of_mass(ColoredParticle))),
                   ("Total neighborhoods", "%d", neighborhoods),
                   ("Homogeneous neighborhoods", "%d", homogeneous_neighborhoods),
                   ("Heterogeneous neighborhoods", "%d", heterogeneous_neighborhoods)]

        return metrics
