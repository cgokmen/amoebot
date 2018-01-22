import os

from compsim.simulate import NewSeparationSimulator
from compsim.generate import generate_random_separation_grid
from compsim.io import separation_simulator_grid_saver
from compsim.plot import FixedCroppedVectorPlotter

grid = generate_random_separation_grid(1000, 2, simulator_type=NewSeparationSimulator)

in_dir = "input/separation/generated/"
grid_name = "1000particles-2class"
separation_simulator_grid_saver(os.path.join(in_dir, grid_name + ".txt"), grid)
