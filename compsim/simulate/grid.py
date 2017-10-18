import numpy as np
from enum import Enum


class Particle(object):
    COLOR = (0, 0, 0)

    def __init__(self, axial_coordinates, id):
        self.axial_coordinates = np.array(axial_coordinates).astype(int)
        self.id = id

    def get_color(self):
        return Particle.COLOR

    def move(self, new_axial_coordinates):
        self.axial_coordinates = np.array(new_axial_coordinates).astype(int)


class Direction(Enum):
    SE = 0
    NE = 1
    N = 2
    NW = 3
    SW = 4
    S = 5

    __axial_vectors__ = (
        (1, 0),
        (1, -1),
        (0, -1),
        (-1, 0),
        (-1, 1),
        (0, 1)
    )

    def axial_vector(self):
        return Direction.__axial_vectors__[self.value]

    def shift_counterclockwise_by(self, by):
        return Direction((self.value + by) % 6)


class Grid(object):
    def __init__(self, size):
        self.size = np.array(size)
        self.width = size[0]
        self.height = size[1]

        self.min = self.size / -2
        self.max = self.size / 2

        self.extrema = [self.min, np.array([self.min[0], self.max[1]]), self.max, np.array([self.max[0], self.min[1]])]

        self.__neighbor_coordinates = np.empty([self.width + 1, self.height + 1, 6, 2], dtype=int)
        self.__neighbor_particles = np.empty([self.width + 1, self.height + 1, 6], dtype=object)

        for x in xrange(self.min[0], self.max[0] + 1):
            for y in xrange(self.min[1], self.max[1] + 1):
                axial_position = np.array([x, y])
                array_position = axial_position[0] + self.max[0], axial_position[1] + self.max[1]

                for i in xrange(len(Direction)):
                    d = Direction(i).axial_vector()

                    neighbor_position = axial_position[0] + d[0], axial_position[1] + d[1]

                    self.__neighbor_coordinates[(array_position[0], array_position[1], i)] = neighbor_position
                    self.__neighbor_particles[(array_position[0], array_position[1], i)] = None

        self._grid_dict = {}
        self._grid_array = np.empty((self.width + 1, self.height + 1), dtype=Particle)

        for x in xrange(self.width + 1):
            for y in xrange(self.height + 1):
                self._grid_array[(x, y)] = None

        self._particle_list = []

        self._particles_by_type = {}

    @staticmethod
    def is_position_between_positions(p, min_pos, max_pos):
        return not (p[0] <= min_pos[0] or p[1] <= min_pos[1] or p[0] >= max_pos[0] or p[1] >= max_pos[1])

    def is_position_in_bounds(self, axial_coordinates):
        return Grid.is_position_between_positions(axial_coordinates, self.min, self.max)

    def get_valid_coordinates(self):
        return [(a[0] - self.max[0], a[1] - self.max[1]) for a in np.ndindex(self._grid_array.shape)]

    def add_particle(self, particle):
        if not isinstance(particle, Particle):
            raise ValueError("Grid only supports subclasses of Particle")

        if particle in self._particle_list:
            raise ValueError("This particle already exists")

        if not self.is_position_in_bounds(particle.axial_coordinates):
            raise ValueError("Coordinates out of bounds")

        if self.get_particle(particle.axial_coordinates) is not None:
            raise ValueError("There already is a particle at this position")

        # self._hex_map[particle.axial_coordinates] = [particle]
        self._grid_array[
            particle.axial_coordinates[0] + self.max[0], particle.axial_coordinates[1] + self.max[1]] = particle
        # self._grid_dict[(particle.axial_coordinates[0], particle.axial_coordinates[1])] = particle
        self._particle_list.append(particle)

        particle_type = type(particle)

        if particle_type not in self._particles_by_type:
            self._particles_by_type[particle_type] = []

        self._particles_by_type[particle_type].append(particle)

        # Update neighbors

        for direction in Direction:
            v = direction.value
            d = direction.axial_vector()
            pos = particle.axial_coordinates[0] + d[0], particle.axial_coordinates[1] + d[1]

            if not self.is_position_in_bounds(pos):
                continue

            self.__neighbor_particles[
                pos[0] + self.max[0], pos[1] + self.max[1], direction.shift_counterclockwise_by(3).value] = particle

    def move_particle(self, old_position, new_position):
        particle = self.get_particle(old_position)

        if particle is None:
            return

        existing_particle = self.get_particle(new_position)
        if existing_particle is not None:
            return

        if not self.is_position_in_bounds(new_position):
            return

        self.remove_particle(particle)
        particle.move(new_position)
        self.add_particle(particle)

    def remove_particle(self, particle):
        particle_type = type(particle)
        array_coords = particle.axial_coordinates[0] + self.max[0], particle.axial_coordinates[1] + self.max[1]
        self._grid_array[array_coords] = None
        # del self._grid_dict[(particle.axial_coordinates[0], particle.axial_coordinates[1])]
        self._particles_by_type[particle_type].remove(particle)
        self._particle_list.remove(particle)

        for direction in Direction:
            v = direction.value
            d = direction.axial_vector()
            pos = particle.axial_coordinates[0] + d[0], particle.axial_coordinates[1] + d[1]

            if not self.is_position_in_bounds(pos):
                continue

            self.__neighbor_particles[
                pos[0] + self.max[0], pos[1] + self.max[1], direction.shift_counterclockwise_by(3).value] = None

    def get_particle(self, axial_coordinates, classes_to_consider=None):
        particle = self._grid_array[axial_coordinates[0] + self.max[0], axial_coordinates[1] + self.max[1]]
        # particle = self._grid_dict.get((axial_coordinates[0], axial_coordinates[1]), None)

        if particle is None:
            return None

        if classes_to_consider is None or isinstance(particle, classes_to_consider):
            return particle

        return None

    def get_all_particles(self, classes_to_consider=None):
        if classes_to_consider is None:
            return self._particle_list

        result = []
        for particle_type, particles in self._particles_by_type.iteritems():
            if issubclass(particle_type, classes_to_consider):
                result += particles

        return result

    def get_all_particles_by_direct_class(self, class_to_consider):
        particles = self._particles_by_type.get(class_to_consider, None)

        return particles if particles is not None else []

    def particles_connected(self, classes_to_consider=None):
        def has_eligible_particle(position):
            return (self.is_position_in_bounds(position)) and (
            self.get_particle(position, classes_to_consider) is not None)

        return self.check_connected(has_eligible_particle)

    def particle_holes(self, classes_to_consider=None):
        def is_empty(position):
            return (self.is_position_in_bounds(position)) and (
            self.get_particle(position, classes_to_consider) is None)

        return self.check_connected(is_empty)

    def check_connected(self, position_include_fn):
        def bfs(start):
            visited, queue = set(), [start]
            while queue:
                vertex = queue.pop(0)
                if vertex not in visited:
                    visited.add(vertex)

                    # We dont use the neighbor position method here - it doesn't support outside-the-box positions
                    next_set = set([tuple(c) for c in self.get_neighbor_positions(vertex) if position_include_fn(c)])
                    queue.extend(next_set - visited)

            return visited

        num_eligible = 0
        start_spot = None

        for axial_coordinates in self.get_valid_coordinates():
            if position_include_fn(axial_coordinates):
                num_eligible += 1
                start_spot = axial_coordinates

        # If no positions match the criteria
        if num_eligible == 0:
            return True

        # Does a breadth-first search reach all eligible particles?
        return len(bfs(tuple(start_spot))) == num_eligible

    def neighbor_count(self, axial_coordinates, classes_to_consider=None):
        return len(self.get_neighbors(axial_coordinates, classes_to_consider))

    def get_neighbors(self, axial_coordinates, classes_to_consider=None, include_none=False):
        # neighbors = [self.get_particle(neighbor_position, classes_to_consider) for neighbor_position in self.get_neighbor_positions(axial_coordinates)]
        neighbors = self.__neighbor_particles[axial_coordinates[0] + self.max[0], axial_coordinates[1] + self.max[1]]

        if include_none:
            result = []
            for n in neighbors:
                if n is None or classes_to_consider is None or isinstance(n, classes_to_consider):
                    result.append(n)
                elif classes_to_consider is not None and not isinstance(n, classes_to_consider):
                    result.append(None)
            return result
        else:
            return [n for n in neighbors if
                    n is not None and (classes_to_consider is None or isinstance(n, classes_to_consider))]

    def get_neighbor_in_direction(self, axial_coordinates, direction, classes_to_consider=None):
        neighbor = self.__neighbor_particles[
            axial_coordinates[0] + self.max[0], axial_coordinates[1] + self.max[1], direction.value]
        return neighbor if classes_to_consider is None or isinstance(neighbor, classes_to_consider) else None

    def is_neighbor(self, axial_coordinates, neighbor_axial):
        return np.linalg.norm(axial_coordinates[0] - neighbor_axial[0])

    def get_position_in_direction(self, axial_coordinates, direction):
        # return axial_coordinates + direction.axial_vector()
        return self.__neighbor_coordinates[
            axial_coordinates[0] + self.max[0], axial_coordinates[1] + self.max[1], direction.value]

    def get_neighbor_positions(self, axial_coordinates):
        # return [axial_coordinates + d.axial_vector() for d in Direction]
        return self.__neighbor_coordinates[axial_coordinates[0] + self.max[0], axial_coordinates[1] + self.max[1]]

    def calculate_perimeter(self, classes_to_consider=None):
        particles = self.get_all_particles(classes_to_consider)

        if len(particles) == 0:
            return 0

        def find_bottom_left_particle():
            for x in xrange(self.width):
                for y in xrange(self.height):
                    pos = self.min + np.array([x, y])
                    p = self.get_particle(pos, classes_to_consider)

                    if p is not None:
                        return p

        start_position = find_bottom_left_particle().axial_coordinates
        current_position = np.copy(start_position)
        direction = Direction.SW

        perimeter = 0

        while True:
            nbr = self.get_neighbor_in_direction(current_position, direction, classes_to_consider)

            if nbr is not None:
                current_position = nbr.axial_coordinates
                direction = direction.shift_counterclockwise_by(-1)
                perimeter += 1
            else:
                direction = direction.shift_counterclockwise_by(1)

            if np.all(current_position == start_position) and direction == Direction.SW:
                break

        return perimeter

    def find_center_of_mass(self, classes_to_consider=None):
        center_of_mass = np.array([0, 0])
        num_particles = 0

        for particle in self.get_all_particles(classes_to_consider):
            center_of_mass += particle.axial_coordinates
            num_particles += 1

        return center_of_mass if num_particles == 0 else center_of_mass / num_particles
