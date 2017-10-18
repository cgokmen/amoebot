import numpy as np
import os
import itertools

from compsim.simulate import SeparationSimulator, ConnectivityRule
from compsim.plot import Plotter
from compsim.io import separation_simulator_grid_loader, MetricsIO
from compsim.generate import generate_random_grid

if __name__ == "__main__":
    input_dir = "input/separation/handmade/"

    #input_files = ["2-compressed-largef.txt"] #, "2-compressed-smallf.txt", "2-spread-largef.txt", "2-spread-smallf.txt"]
    input_files = ["3-compressed-largef.txt"] #, "2-compressed-smallf.txt", "2-spread-largef.txt", "2-spread-smallf.txt"]

    for f in input_files:
        input_file = os.path.join(input_dir, f)
        model_name = os.path.splitext(os.path.basename(input_file))[0]

        grid = separation_simulator_grid_loader(input_file)

        compression_constants = range(1, 5.25, 0.25)
        separation_constants = range(1, 5.25, 0.25)

        compression_constants += [1.0 / x for x in compression_constants]
        separation_constants += [1.0 / x for x in compression_constants]

        connectivity_rules = [ConnectivityRule.Strict, ConnectivityRule.Interclass, ConnectivityRule.Intraclass]

        print "Now starting model %s" % model_name

        for cr in connectivity_rules:
            simulators = [SeparationSimulator(grid, c[0], c[1], cr) for c in itertools.product(separation_constants, compression_constants)]

            print "    Now starting cr %s for model %s" % (cr.name, model_name)

            for cs in simulators:
                cs.grid = separation_simulator_grid_loader(input_file) # TODO: This is NOT a nice thing to do.

                sim_name = "lambda-%.2f--alpha-%.2f" % (cs.bias, cs.bias_alpha)

                print "\n        Starting new simulation: %s" % sim_name
                total_iterations = 3000000
                i = 0
                unit_iterations = 10000

                path = os.path.join("output", "SeparationSimulator", model_name, cr.name, sim_name)
                gif_path = os.path.join("output", "SeparationSimulator", model_name, cr.name, sim_name, "animation.gif")
                csv_path = os.path.join("output", "SeparationSimulator", model_name, cr.name, sim_name, "metrics.csv")

                plotter = Plotter(cs, path, gif_path)
                metricsio = MetricsIO(cs, csv_path)

                plotter.plot("%d.jpg" % i)
                metricsio.save_metric()

                while i < total_iterations:
                    cs.run_iterations(unit_iterations)
                    i += unit_iterations
                    plotter.plot("%d.jpg" % i)
                    metricsio.save_metric()

                plotter.close()
                metricsio.close()

                print "        Simulation complete"

            print "    Successfully completed cr %s for model %s" % (cr.name, model_name)

        print "Successfully completed model %s" % model_name