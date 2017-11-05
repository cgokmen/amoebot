import os
import time

from compsim.simulate import HeatTransferSimulator, Ant, UndiscoveredFood
from compsim.plot import Plotter
from compsim.io import compression_simulator_grid_loader

if __name__ == "__main__":
    #grid = compression_simulator_grid_loader("input/heattransfer/small_heattransfer.txt", False, (Ant,))
    #grid = compression_simulator_grid_loader("input/heattransfer/big_heattransfer.txt", False, (Ant,))
    grid = compression_simulator_grid_loader("input/heattransfer/bigger_heattransfer.txt", False, (Ant,))

    cs = HeatTransferSimulator(grid)

    # Heat up a particle
    #cs.grid.get_particle((0, -1)).bias = 2

    food = UndiscoveredFood((0, 7), "f00d")
    cs.add_food(food)

    food2 = UndiscoveredFood((0, -7), "f00d2")
    cs.add_food(food2)

    total_iterations = 100000
    unit_iterations = 10000

    plotter = Plotter(cs, os.path.join("output", "heattransfer", str(int(time.time()))))

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

    #print(cs.get_metrics())

    #interface.quit_app()
