from . import HeatTransferSimulator, CompressionSimulator, Food, Ant, DiscoveredFood, UndiscoveredFood

class HeatTransferForagingSimulator(HeatTransferSimulator):

    def move(self, random_particle, random_direction, probability, classes_to_move=None):
        # For now, just activate the random particle
        HeatTransferSimulator.move(self, random_particle, random_direction, probability, classes_to_move)

        m = CompressionSimulator.move(self, random_particle, random_direction, probability, classes_to_move)

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

    def valid_move(self, particle, old_position, new_position, direction):
        if self.grid.neighbor_count(old_position, Food) > 0:
            # Adjacent to food? Don't move
            return False

        return self.grid.neighbor_count(old_position) < 5 and (
        self.property1(old_position, new_position, direction, Ant) or self.property2(old_position, new_position,
                                                                                     direction, Ant)) and (
               self.property1(old_position, new_position, direction, (Ant, DiscoveredFood)) or self.property2(
                   old_position, new_position, direction, (Ant, DiscoveredFood)))