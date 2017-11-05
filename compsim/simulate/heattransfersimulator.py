from . import CompressionSimulator, Ant, Food, Direction

AMBIENT_TEMPERATURE = 0.25
AMBIENT_MASS = 0.1

DISSIPATION = 0.95

FOOD_TEMPERATURE = 5
FOOD_MASS = 10

class HeatTransferSimulator(CompressionSimulator):
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
        # Get neighbors of the particle for each direction
        neighbors = self.grid.get_neighbors(particle.axial_coordinates, None, True)

        neighborhood_temperature = 0.0
        divide_by = 0

        has_higher_temperature_neighbor = False

        for neighbor in neighbors:
            # If it's None
            if neighbor is None:
                #neighborhood_temperature += AMBIENT_TEMPERATURE * AMBIENT_MASS
                #divide_by += AMBIENT_MASS

                continue

            # If it's an ant
            if isinstance(neighbor, Ant):
                neighborhood_temperature += neighbor.bias
                if neighbor.bias > particle.bias:
                    has_higher_temperature_neighbor = True
                divide_by += 1
                continue

            # If it's food
            if isinstance(neighbor, Food):
                neighborhood_temperature += FOOD_TEMPERATURE * FOOD_MASS
                divide_by += FOOD_MASS
                continue

        new_temp = (neighborhood_temperature + particle.bias) / float(divide_by + 1)

        if not has_higher_temperature_neighbor:
            particle.bias =  (new_temp - AMBIENT_TEMPERATURE) * DISSIPATION + AMBIENT_TEMPERATURE
        else:
            particle.bias = new_temp

        #print("Particle %s went from T = %.2f to T = %.2f" % (particle.id, initial_temperature, particle.bias))

        return True

    def get_metrics(self, _=None):
        metrics = CompressionSimulator.get_metrics(self, Ant)

        # TODO: Add any necessary metrics

        return metrics
