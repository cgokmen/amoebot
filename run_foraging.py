import numpy as np

from compsim.simulate import CompressionSimulator, ForagingSimulator, Grid, Direction, Particle, Ant, UndiscoveredFood
from compsim.plot import Plotter
from compsim.io import compression_simulator_grid_loader

if __name__ == "__main__":
    #grid = compression_simulator_grid_loader("input_smallline.txt", True)
    #grid = compression_simulator_grid_loader("input_smallhex.txt", True)
    #grid = compression_simulator_grid_loader("input_longline.txt", True)
    grid = compression_simulator_grid_loader("input_longline2.txt", False, Ant)

    #grid = Grid((4, 4))
    #particle = Particle(np.array([0, 0]), 1)
    #grid.add_particle(particle)
    #particle2 = Particle(grid.get_position_in_direction(particle.axial_coordinates, Direction.N), 2)
    #print(particle2.axial_coordinates)
    #grid.add_particle(particle2)

    cs = ForagingSimulator(grid)

    food = UndiscoveredFood((20, 0), "f00d")
    cs.add_food(food)

    #food = Food((-20, 0), "f00d")
    #cs.add_food(food)

    total_iterations = 30000000
    i = 0
    unit_iterations = 1000000

    plotter = Plotter(cs)

    plotter.plot("output/%d.jpg" % i)

    while i < total_iterations:
        cs.run_iterations(unit_iterations)
        i += unit_iterations
        plotter.plot("output/%d.jpg" % i)
        print(i)

    print(cs.get_metrics())

    #interface.quit_app()
