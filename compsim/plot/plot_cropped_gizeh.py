# coding=utf-8
import threading

import numpy as np
import os
import time
import imageio
import errno
import gizeh
import cairocffi as cairo

axial_to_pixel_mat = np.array([[3 / 2., 0], [np.sqrt(3) / 2.0, np.sqrt(3)]])

EMPTY_POSITION_RADIUS = 3
EMPTY_POSITION_COLOR = (0.75, 0.75, 0.75)

# Circles in 24x24 bounding boxes
CIRCLE_RADIUS = 12

# Circles 24 apart
CIRCLE_DIST = 24

# Circle stroke size
CIRCLE_STROKE = 2

# Edges 4px wide
EDGE_WIDTH = 4

# Text size as a multiple of the screen height
TEXT_FACTOR = 100.0

BORDER_COLOR = (0.1, 0.1, 0.1)

CORNER_PADDING = 2 * CIRCLE_DIST


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class PDFS(object):
    """Simple class to allow gizeh to create pdf figures"""

    def __init__(self, name, width, height):
        self.width = width
        self.height = height
        self._cairo_surface = cairo.PDFSurface(name, width, height)

    def get_new_context(self):
        """ Returns a new context for drawing on the surface."""
        return cairo.Context(self._cairo_surface)

    def flush(self):
        """Write the file"""
        self._cairo_surface.flush()

    def finish(self):
        """Close the surface"""
        self._cairo_surface.finish()


class CroppedVectorPlotter(object):
    def __init__(self, compression_simulator, path=None):
        self.compression_simulator = compression_simulator

        if path is None:
            path = os.path.join("output", type(self.compression_simulator).__name__, str(int(time.time())))

        if callable(path):
            self.path = path()
        else:
            self.path = path
        mkdir_p(self.path)

        self.closed = False

    @staticmethod
    def get_position_from_axial(axial_coordinates):
        return axial_to_pixel_mat.dot(axial_coordinates) * CIRCLE_DIST

    def draw_plot(self):
        if self.closed:
            raise ValueError("This plotter has been closed.")

        # surface = PDFS(name=path, width=self.size[0], height=self.size[1])
        objects = []

        # Here we populate the isometric grid
        for x in xrange(self.compression_simulator.grid.min[0] + 1,
                        self.compression_simulator.grid.max[0]):
            for y in xrange(self.compression_simulator.grid.min[1] + 1,
                            self.compression_simulator.grid.max[1]):
                axial_position = np.array([x, y])

                position = self.get_position_from_axial(axial_position)
                circle = gizeh.circle(r=EMPTY_POSITION_RADIUS, xy=position, fill=EMPTY_POSITION_COLOR)
                objects.append(circle)

        # boundary_positions = [tuple(self.get_position_from_axial(e)) for e in self.compression_simulator.grid.extrema]
        # boundary_positions.append(boundary_positions[0])

        # boundary = gizeh.polyline(points=boundary_positions, stroke_width=EDGE_WIDTH, stroke=BORDER_COLOR)
        # objects.append(boundary)

        drawn_particles = {}

        # Draw the particle links
        particles = list(self.compression_simulator.grid.get_all_particles())
        for particle in particles:
            position = self.get_position_from_axial(particle.axial_coordinates)

            # Draw lines to neighbors
            neighbors_positions = [self.get_position_from_axial(neighbor.axial_coordinates) for neighbor in
                                   self.compression_simulator.grid.get_neighbors(particle.axial_coordinates) if
                                   neighbor not in drawn_particles]

            tuple_position = tuple(position)

            for neighbor_position in neighbors_positions:
                line = gizeh.polyline(points=[tuple_position, tuple(neighbor_position)], stroke_width=EDGE_WIDTH,
                                      stroke=(0.4, 0.4, 0.4))
                objects.append(line)

            drawn_particles[particle] = True

        # Draw the particles themselves
        axials = np.array([p.axial_coordinates for p in particles])
        coords = np.array([self.get_position_from_axial(a) for a in axials])
        max_coords = np.amax(np.absolute(coords), axis=0)
        com_coords = self.get_position_from_axial(np.mean(axials, axis=0).astype(int))

        colors = (tuple([x / 255.0 for x in p.get_color()]) for p in particles)
        circles = [gizeh.circle(r=CIRCLE_RADIUS, xy=coord, fill=color,
                                stroke=(0, 0, 0), stroke_width=CIRCLE_STROKE) for coord, color in zip(coords, colors)]
        objects += circles

        group = gizeh.Group(objects)

        # Finally shift the group to the center of the field and return it
        return group.translate(xy=(-1 * com_coords)), max_coords[0], max_coords[1]

    def plot(self, filename):
        group, max_x_dist, max_y_dist = self.draw_plot()

        w, h = 2 * (max_x_dist + CORNER_PADDING), 2 * (max_y_dist + CORNER_PADDING)

        plt = PDFS(os.path.join(self.path, filename), w, h)
        group.translate(xy=(w / 2, h / 2)).draw(plt)
        plt.flush()
        plt.finish()

    def close(self):
        self.closed = True
