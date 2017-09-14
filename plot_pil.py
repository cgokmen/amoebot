import numpy as np
from particle import axial_to_pixel_mat
from PIL import Image, ImageDraw, ImageFont
import os
import threading

# Circles in 24x24 bounding boxes
CIRCLE_BOUNDING = np.array([24, 24])

# Circles 24 apart
CIRCLE_DIST = 24

# Edges 4px wide
EDGE_WIDTH = 4

# Text size as a multiple of the screen height
TEXT_FACTOR = 100.0

#FONT = ImageFont.truetype(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cmunorm.ttf"), int(CIRCLE_BOUNDING[1] * TEXT_FACTOR))

def save_plt(plot, filename):
    plot.save(filename)
    plot.close()

class Plotter(object):
    def __init__(self, compression_simulator):
        self.compression_simulator = compression_simulator

        self.min_pos = axial_to_pixel_mat.dot(compression_simulator.grid.min - np.array([1, 1])) * CIRCLE_DIST
        self.max_pos = axial_to_pixel_mat.dot(compression_simulator.grid.max + np.array([1, 1])) * CIRCLE_DIST

        self.size = (self.max_pos - self.min_pos).astype(int)
        self.center = self.size / 2
        #self.font = FONT
        self.font = ImageFont.truetype(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cmunorm.ttf"), int(self.size[1] / TEXT_FACTOR))

    def get_position_from_axial(self, axial_coordinates):
        return axial_to_pixel_mat.dot(axial_coordinates) * CIRCLE_DIST + self.center

    def plot(self, filename):
        plt = Image.new('RGB', tuple(self.size), (255, 255, 255))

        draw = ImageDraw.Draw(plt)

        drawn_hexagons = {}

        for key in xrange(len(self.compression_simulator.grid.extrema)):
            extremum = self.compression_simulator.grid.extrema[key]
            pos = self.get_position_from_axial(extremum)
            draw.ellipse([tuple(pos - (CIRCLE_BOUNDING / 2)), tuple(pos + (CIRCLE_BOUNDING / 2))], (255, 0, 0))

            neighbor_extremum = self.compression_simulator.grid.extrema[key - 1]
            neighbor_pos = self.get_position_from_axial(neighbor_extremum)
            draw.line([tuple(pos), tuple(neighbor_pos)], (255, 0, 0), EDGE_WIDTH)

        if True:
            # This part draws the lambda gradient
            for x in xrange(self.compression_simulator.grid.min[0], self.compression_simulator.grid.max[0] + 1):
                for y in xrange(self.compression_simulator.grid.min[1], self.compression_simulator.grid.max[1] + 1):
                    axial_position = np.array([x, y])
                    array_position = axial_position[0] + self.compression_simulator.grid.max[0], axial_position[1] + self.compression_simulator.grid.max[1]
                    bias = self.compression_simulator._bias_array[array_position]
                    position = self.get_position_from_axial(axial_position)
                    clr = int((bias - 1) * 64 - 1)
                    draw.ellipse([tuple(position - (CIRCLE_BOUNDING / 2)), tuple(position + (CIRCLE_BOUNDING / 2))], (255 - clr, clr, 0))

        if True:
            for particle in self.compression_simulator.grid.get_all_particles():
                position = self.get_position_from_axial(particle.axial_coordinates)

                # Draw lines to neighbors
                neighbors_positions = [self.get_position_from_axial(neighbor.axial_coordinates) for neighbor in
                                       self.compression_simulator.grid.get_neighbors(particle.axial_coordinates) if
                                       neighbor not in drawn_hexagons]

                tuple_position = tuple(position)

                for neighbor_position in neighbors_positions:
                    draw.line([tuple_position, tuple(neighbor_position)], (100, 100, 100), EDGE_WIDTH)

                draw.ellipse([tuple(position - (CIRCLE_BOUNDING / 2)), tuple(position + (CIRCLE_BOUNDING / 2))], particle.get_color())
                #draw.text(tuple(position), str(particle.id), (255,0,0), FONT)

                drawn_hexagons[particle] = True

        start = self.get_position_from_axial(self.compression_simulator.grid.max)
        start = np.array([self.size[0] - start[0], start[1]])
        shift = (np.array([0, self.size[1]]) * 1.1 / TEXT_FACTOR).astype(int)

        metrics = self.compression_simulator.get_metrics()
        metric_count = len(metrics)
        for key in xrange(metric_count):
            metric = metrics[key]
            draw.text(tuple(start - shift * (metric_count-key)), metric, (0, 0, 0), self.font)

        start = self.get_position_from_axial(self.compression_simulator.grid.min)
        start = np.array([self.size[0] - start[0], start[1]])
        text = "Algorithm: %s" % type(self.compression_simulator).__name__
        w, h = draw.textsize(text, self.font)
        draw.text(start - np.array([w, 0]), text, (0, 0, 0), self.font)

        start += shift
        text = "Start time: %s" % self.compression_simulator.start_time
        w, h = draw.textsize(text, self.font)
        draw.text(start - np.array([w, 0]), text, (0, 0, 0), self.font)

        threading.Thread(target=save_plt, args=(plt, filename)).start()
