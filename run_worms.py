import os
import itertools
import threading

from compsim.simulate import WormTheorySimulator, WormParticle, ConnectivityRule
from compsim.plot import RasterPlotter
from compsim.io import separation_simulator_grid_loader, MetricsIO

def run_simulation(input_file, root_dir, c, model_name):
    grid = separation_simulator_grid_loader(input_file, WormParticle)
    cs = WormTheorySimulator(grid, c[0], c[1])

    sim_name = "lambda-%.2f--alpha-%.2f" % (cs.bias, cs.bias_alpha)
    cr = ConnectivityRule.Strict # To maintain backwards compatibility with the html plotter etc

    print "Starting new simulation: %s. %d simulations currently running." % (sim_name, threading.activeCount() - 1)
    total_iterations = 50000000
    i = 0
    unit_iterations = 1000000
    plot_iterations = unit_iterations * 5

    path = os.path.join(root_dir, model_name, cr.name, sim_name)
    gif_path = os.path.join(root_dir, model_name, cr.name, sim_name, "animation.gif")
    csv_path = os.path.join(root_dir, model_name, cr.name, sim_name, "metrics.csv")

    plotter = RasterPlotter(cs, path, gif_path)
    metricsio = MetricsIO(cs, csv_path)

    plotter.plot("%d.jpg" % i)
    metricsio.save_metric()

    while i < total_iterations:
        cs.run_iterations(unit_iterations)
        i += unit_iterations
        #print "            %d iterations run" % i

        if i % plot_iterations == 0:
            plotter.plot("%d.jpg" % i)

        metricsio.save_metric()

    plotter.close()
    metricsio.close()

    print "Simulation completed: %s. %d simulations still running." % (sim_name, threading.activeCount() - 1)

if __name__ == "__main__":
    input_dir = "input/worms/"
    root_dir = "output/WormTheorySimulator/11-29/"

    #input_files = ["2-compressed-largef.txt"] #, "2-compressed-smallf.txt", "2-spread-largef.txt", "2-spread-smallf.txt"]
    #input_files = ["3-compressed-largef.txt", "3-spread-largef.txt", "3-spread-smallf.txt"] #"3-compressed-smallf.txt",
    input_files = ["worm_6class7particle.txt"]

    for f in input_files:
        input_file = os.path.join(input_dir, f)
        model_name = os.path.splitext(os.path.basename(input_file))[0]

        #compression_constants = {4} #{1+x*1 for x in range((4 - 1) * 1 + 1)}
        #separation_constants = {4} #{1+x*1 for x in range((4 - 1) * 1 + 1)}

        #compression_constants |= {1.0 / x for x in compression_constants}
        #separation_constants |= {1.0 / x for x in separation_constants}

        compression_constants = {1.0, 4.0}
        separation_constants = {0.25, 4.0}

        print "Now starting model %s" % model_name

        for c in itertools.product(compression_constants, separation_constants):
            threading.Thread(target=run_simulation, args=(input_file, root_dir, c, model_name)).start()

        print "Successfully completed model %s" % model_name