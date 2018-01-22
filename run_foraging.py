import os
import time

from compsim.simulate import HeatTransferForagingSimulator, Ant, UndiscoveredFood
from compsim.plot import RasterPlotter
from compsim.io import compression_simulator_grid_loader

if __name__ == "__main__":
    #grid = compression_simulator_grid_loader("input/heattransfer/small_heattransfer.txt", False, (Ant,))
    #grid = compression_simulator_grid_loader("input/heattransfer/big_heattransfer.txt", False, (Ant,))
    grid = compression_simulator_grid_loader("input/heattransfer/bigger_heattransfer.txt", False, (Ant,))

    cs = HeatTransferForagingSimulator(grid)

    food = UndiscoveredFood((0, 15), "f00d")
    cs.add_food(food)

    food2 = UndiscoveredFood((0, -15), "f00d2")
    cs.add_food(food2)

    total_iterations = 1000000
    unit_iterations = 50000

    plotter = RasterPlotter(cs, os.path.join("output", "heattransfer", str(int(time.time()))))

    plotter.plot("%d.jpg" % cs.iterations_run)

    while cs.iterations_run < total_iterations:
        if cs.run_iterations(unit_iterations):
            plotter.plot("%d.jpg" % cs.iterations_run)
            print(cs.iterations_run)

    # Run another 9 x total iterations with 10 x unit gaps
    while cs.iterations_run < 5 * total_iterations:
        if cs.run_iterations(10 * unit_iterations):
            plotter.plot("%d.jpg" % cs.iterations_run)
            print(cs.iterations_run)

    plotter.plot("%d-foodgone.jpg" % cs.iterations_run)
    cs.remove_food(cs.grid.get_particle(food.axial_coordinates))

    while cs.iterations_run < total_iterations * 6:
        if cs.run_iterations(unit_iterations):
            plotter.plot("%d.jpg" % cs.iterations_run)
            print(cs.iterations_run)

    while cs.iterations_run < total_iterations * 10:
        if cs.run_iterations(10 * unit_iterations):
            plotter.plot("%d.jpg" % cs.iterations_run)
            print(cs.iterations_run)

    #print(cs.get_metrics())

    #interface.quit_app()
