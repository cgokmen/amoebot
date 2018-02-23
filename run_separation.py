import numpy as np
import os
import itertools
import threading

from compsim.io import separation_simulator_grid_saver
from compsim.simulate import NewSeparationSimulator, SeparationSimulator, ConnectivityRule
from compsim.plot import RasterPlotter, VectorPlotter, CroppedVectorPlotter, FixedCroppedVectorPlotter
from compsim.io import separation_simulator_grid_loader, MetricsIO, GREYSCALE_COLORS, BRIGHT_COLORS

thread = False

def run_simulation(input_file, root_dir, c, model_name):
    grid = separation_simulator_grid_loader(input_file, colors=GREYSCALE_COLORS)
    cs = NewSeparationSimulator(grid, c[0], c[1], allow_swap=True)

    sim_name = "lambda-%.2f--alpha-%.2f" % (cs.bias, cs.bias_alpha)

    print "Starting new simulation: %s. %d simulations currently running." % (sim_name, threading.activeCount() - 1)
    total_iterations = 50000000
    i = 0
    unit_iterations = 10000000
    plot_iterations = 5 * unit_iterations

    path = os.path.join(root_dir, model_name, sim_name)
    gif_path = os.path.join(root_dir, model_name, sim_name, "animation.gif")

    plotter = VectorPlotter(cs, path)

    plotter.plot("%d.pdf" % i)

    if True:
        while i < total_iterations:
            cs.run_iterations(unit_iterations)
            i += unit_iterations
            print "%s: %d iterations run" % (sim_name, i)

            if i % plot_iterations == 0:
                plotter.plot("%d.pdf" % i)
                separation_simulator_grid_saver(os.path.join(path, "%d.txt" % i), grid)

    plotter.close()

    print "Simulation completed: %s. %d simulations still running." % (sim_name, threading.activeCount() - 1)

if __name__ == "__main__":
    input_dir = "input/separation/generated/"
    root_dir = "output/NewSeparationSimulator/2-16-sanscrop/"

    #input_files = ["2-compressed-largef.txt"] #, "2-compressed-smallf.txt", "2-spread-largef.txt", "2-spread-smallf.txt"]
    #input_files = ["3-compressed-largef.txt", "3-spread-largef.txt", "3-spread-smallf.txt"] #"3-compressed-smallf.txt",
    input_files = ["100particles-2class.txt"] #, "100particles-3class.txt"]
    #input_files = ["two-particles.txt"]

    for f in input_files:
        input_file = os.path.join(input_dir, f)
        model_name = os.path.splitext(os.path.basename(input_file))[0]

        compression_constants = {0.58}
        separation_constants = {0.58}

        print "Now starting model %s" % model_name

        if thread:
            for c in itertools.product(compression_constants, separation_constants):
                threading.Thread(target=run_simulation, args=(input_file, root_dir, c, model_name)).start()
        else:
            for c in itertools.product(compression_constants, separation_constants):
                run_simulation(input_file, root_dir, c, model_name)

        print "Successfully completed model %s" % model_name
