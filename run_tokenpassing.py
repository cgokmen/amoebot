import os
import time

from compsim.simulate import TokenPassingSimulator, Ant, UndiscoveredFood
from compsim.plot import Plotter
from compsim.io import compression_simulator_grid_loader

if __name__ == "__main__":
    grid = compression_simulator_grid_loader("input/input_smallhex.txt", True, Ant)

    cs = TokenPassingSimulator(grid)

    food = UndiscoveredFood((0, 4), "f00d")
    cs.add_food(food)

    total_iterations = 500
    unit_iterations = 1

    plotter = Plotter(cs, os.path.join("output", "tokenpassing", str(int(time.time()))))

    plotter.plot("%d.jpg" % cs.iterations_run)

    while cs.iterations_run < total_iterations:
        if cs.run_iterations(unit_iterations):
            plotter.plot("%d.jpg" % cs.iterations_run)
            print(cs.iterations_run)

    plotter.plot("%d-foodgone.jpg" % cs.iterations_run)
    cs.remove_food(food)

    while cs.iterations_run < total_iterations * 3:
        if cs.run_iterations(unit_iterations):
            plotter.plot("%d.jpg" % cs.iterations_run)
            print(cs.iterations_run)

    print(cs.get_metrics())

    #interface.quit_app()
