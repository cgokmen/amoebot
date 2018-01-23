import os

from compsim.simulate import NewSeparationSimulator
from compsim.io import separation_simulator_grid_loader

if __name__ == "__main__":
    input_dir = "input/separation/generated/"
    input_file = "1000particles-2class-spread.txt"

    lambda_bias = 4.0
    alpha_bias = 4.0

    input_file = os.path.join(input_dir, input_file)
    model_name = os.path.splitext(os.path.basename(input_file))[0]

    grid = separation_simulator_grid_loader(input_file)
    simulator = NewSeparationSimulator(grid, lambda_bias, alpha_bias)

    print "Starting simulation: lambda=%.2f, alpha-%.2f on %s." % (lambda_bias, alpha_bias, model_name)
    total_iterations = 1000000
    unit_iterations = 1000000
    i = 0

    while i < total_iterations:
        simulator.run_iterations(unit_iterations)
        i += unit_iterations
        print "%d iterations run" % i

    print "Simulation completed."