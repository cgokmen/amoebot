import numpy as np
import pygame as pg
import particle

COLORS = np.array([
    [255, 255, 255],  # white
    [0, 0, 0]  # black
])


class UserInterface(object):
    def __init__(self, compression_simulator):
        self.compression_simulator = compression_simulator

        self.caption = "Compression Simulator"

        self.width, self.height = 1280, 720
        self.size = np.array([self.width, self.height])
        self.center = (self.size / 2).astype(np.int)

        self.multiplication_factor = int(min(self.width / self.compression_simulator.grid.width, self.height / self.compression_simulator.grid.height))

        if self.multiplication_factor < 3:
            raise ValueError("Graph too big for display of this size")

        self.main_surf = None
        self.font = None
        self.clock = None
        self.init_pg()

    def init_pg(self):
        pg.init()
        self.main_surf = pg.display.set_mode(self.size)
        pg.display.set_caption(self.caption)

        pg.font.init()
        self.font = pg.font.SysFont("monospace", 14, True)
        self.clock = pg.time.Clock()

    @staticmethod
    def handle_events():
        running = True
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False

        return running

    def main_loop(self):
        running = self.handle_events()

        return running

    def draw(self):
        # show all hexes
        drawn_hexagons = {}

        for hexagon in self.compression_simulator.grid.get_all_particles():
            pos = hexagon.position

            pg.draw.circle(self.main_surf, COLORS[1], (pos + self.center) * self.multiplication_factor, int(self.multiplication_factor / 3))

            # Draw lines to neighbors
            neighbors_positions = [neighbor.position for neighbor in self.compression_simulator.grid.get_neighbors(hexagon.axial_coordinates) if neighbor not in drawn_hexagons]

            for neighbor_position in neighbors_positions:
                pg.draw.line(self.main_surf, COLORS[1], (pos + self.center) * self.multiplication_factor, (neighbor_position + self.center) * self.multiplication_factor, int(self.multiplication_factor / 3))

            drawn_hexagons[hexagon] = True

        # draw values of hexes
        # for hexagon in self.hex_map.values():
        #    text = self.font.render(str(hexagon.value), False, (0, 0, 0))
        #    text.set_alpha(160)
        #    text_pos = hexagon.get_position() + self.center
        #    text_pos -= (text.get_width() / 2, text.get_height() / 2)
        #    self.main_surf.blit(text, text_pos)

        name_text = self.font.render(
                "Simulation Type: %s" % type(self.compression_simulator).__name__,
                True,
                (50, 50, 50))

        bias_text = self.font.render(
                "Bias: %.2f" % self.compression_simulator.bias,
                True,
                (50, 50, 50))

        iterations_text = self.font.render(
                "Iterations run: %d" % self.compression_simulator.iterations_run,
                True,
                (50, 50, 50))

        self.main_surf.blit(name_text, (5, 15))
        self.main_surf.blit(bias_text, (5, 30))
        self.main_surf.blit(iterations_text, (5, 45))

        # Update screen
        pg.display.update()
        self.main_surf.fill(COLORS[0])
        self.clock.tick(30)

    @staticmethod
    def quit_app():
        pg.quit()
