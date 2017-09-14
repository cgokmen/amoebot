import numpy as np
from grid import Direction
import datetime

class CompressionSimulator(object):
    def __init__(self, grid, bias):
        self.grid = grid
        self.bias = float(bias)
        self.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.rounds = 0
        self.movements = 0
        self.visited = {}

        self.property1_count = 0
        self.property2_count = 0

        self.pass1 = 0
        self.pass2 = 0

        self.iterations_run = 0

    def run_iterations(self, iterations, classes_to_move = None):
        particles = self.grid.get_all_particles(classes_to_move)
        particle_choices = np.random.choice(particles, iterations)
        direction_choices = np.random.choice([Direction.N, Direction.NW, Direction.SW, Direction.S, Direction.SE, Direction.NE], iterations)
        probabilities = np.random.sample(iterations)
        for n in xrange(iterations):
            self.move(particle_choices[n], direction_choices[n], probabilities[n])
            self.iterations_run += 1

    def get_bias(self, particle):
        return self.bias

    def move(self, random_particle, random_direction, probability, classes_to_move = None):
        # Check if new location is empty
        current_location = random_particle.axial_coordinates
        new_location = self.grid.get_position_in_direction(current_location, random_direction)

        if not self.grid.is_position_in_bounds(new_location):
            # New location out of board bounds
            #print("Bounds")
            return

        if self.grid.get_particle(new_location) is not None:
            # There already is a particle at this new position
            #print("Existing", current_location, random_direction, new_location)
            return

        if not self.valid_move(current_location, new_location, random_direction): # TODO: Check classes to move?
            #print("Invalid")
            return

        current_neighbors = self.grid.neighbor_count(current_location) # TODO: Check classes to move?
        new_neighbors = self.grid.neighbor_count(new_location) - 1 # TODO: Check classes to move?

        prob_move = self.get_bias(random_particle) ** (new_neighbors - current_neighbors)

        self.pass1 += 1

        if not probability < prob_move:  # Choose with probability
            #print probability
            return

        self.pass2 += 1

        self.grid.move_particle(current_location, new_location)

        # Movement counting
        self.movements += 1

        # Round checking
        self.visited[random_particle] = True
        for particle in self.grid.get_all_particles(classes_to_move):
            if not self.visited.get(particle, False):
                return

        # If this point is reached, a round has completed
        self.rounds += 1
        self.visited = {}

    def valid_move(self, old_position, new_position, direction):
        a = self.grid.neighbor_count(old_position) < 5
        b = self.property1(old_position, new_position, direction)
        c = self.property2(old_position, new_position, direction)

        if b:
            self.property1_count += 1
        if c:
            self.property2_count += 1

        return a and (b or c)

    def property1(self, old_position, new_position, direction, classes_to_consider=None):
        if self.grid.get_neighbor_in_direction(old_position, direction.shift_counterclockwise_by(5), classes_to_consider) is not None or self.grid.get_neighbor_in_direction(old_position, direction.shift_counterclockwise_by(1), classes_to_consider) is not None:
            neighbors1 = []
            neighbors2 = []

            for i in xrange(5):
                neighbors1.append(self.grid.get_neighbor_in_direction(old_position, direction.shift_counterclockwise_by(i + 1), classes_to_consider) is not None)
                neighbors2.append(self.grid.get_neighbor_in_direction(new_position, direction.shift_counterclockwise_by(i + 4), classes_to_consider) is not None)

            changes1 = 0
            changes2 = 0

            for n in xrange(4):
                if neighbors1[n] != neighbors1[n + 1]:
                    changes1 += 1

                if neighbors2[n] != neighbors2[n + 1]:
                    changes2 += 1

            return (changes1 < 3) and (changes2 < 3)
        else:
            return False

    def property2(self, old_position, new_position, direction, classes_to_consider = None):
        s1 = self.grid.get_neighbor_in_direction(old_position, direction.shift_counterclockwise_by(5), classes_to_consider)
        s2 = self.grid.get_neighbor_in_direction(old_position, direction.shift_counterclockwise_by(1), classes_to_consider)

        if s1 is None and s2 is None:
            if self.grid.neighbor_count(new_position, classes_to_consider) <= 1:
                return False

            if (self.grid.get_neighbor_in_direction(old_position, direction.shift_counterclockwise_by(2), classes_to_consider) is not None
                ) and (
                self.grid.get_neighbor_in_direction(old_position, direction.shift_counterclockwise_by(3), classes_to_consider) is None
                ) and (
                self.grid.get_neighbor_in_direction(old_position, direction.shift_counterclockwise_by(4), classes_to_consider) is not None
            ):
                return False

            if (self.grid.get_neighbor_in_direction(new_position, direction.shift_counterclockwise_by(1), classes_to_consider) is not None
                ) and (
                self.grid.get_neighbor_in_direction(new_position, direction.shift_counterclockwise_by(0), classes_to_consider) is None
                ) and (
                self.grid.get_neighbor_in_direction(new_position, direction.shift_counterclockwise_by(5), classes_to_consider) is not None
            ):
                return False

            return True
        else:
            return False

    def get_metrics(self, classes_to_move = None):
        metrics = []

        metrics.append("Bias: %.2f" % self.bias)
        metrics.append("Iterations: %d" % self.iterations_run)
        metrics.append("Movements made: %d" % self.movements)
        metrics.append("Property 1: %d" % self.property1_count)
        metrics.append("Property 2: %d" % self.property2_count)
        metrics.append("Pass1: %d" % self.pass1)
        metrics.append("Pass2: %d" % self.pass2)
        metrics.append("Rounds completed: %d" % self.rounds)
        metrics.append("Perimeter: %d" % self.grid.calculate_perimeter(classes_to_move))
        metrics.append("Center of mass: x = %.2f, y = %.2f" % tuple(self.grid.find_center_of_mass(classes_to_move)))

        return metrics
