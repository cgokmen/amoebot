import numpy as np

from compsim.simulate import CompressionSimulator, ForagingSimulator, Grid, Direction, Particle, Ant, UndiscoveredFood
from compsim.plot import RasterPlotter
from compsim.io import compression_simulator_grid_loader
from compsim.generate import generate_random_grid

if __name__ == "__main__":
    #grid = generate_random_grid(50, CompressionSimulator, [(Particle, 1)])
    grid = compression_simulator_grid_loader("input/input_longline2.txt")

    cs = CompressionSimulator(grid, 4)

    total_iterations = 30000000
    i = 0
    unit_iterations = 1000000

    plotter = RasterPlotter(cs)

    plotter.plot("%d.jpg" % i)

    while i < total_iterations:
        cs.run_iterations(unit_iterations)
        i += unit_iterations
        plotter.plot("%d.jpg" % i)
        print(i)

    print(cs.get_metrics())