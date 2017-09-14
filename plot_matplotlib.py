import matplotlib.pyplot as plt
import numpy as np
from particle import axial_to_pixel_mat
from matplotlib.collections import LineCollection

def plot(compression_simulator,
         filename,
         node_size=25,
         node_color='k',
         node_shape='o',
         alpha=1.0,
         line_widths=1,
         label=None):

    plt.figure()

    extreme_coords = axial_to_pixel_mat.T.dot(np.array([hex.position for hex in compression_simulator.grid.get_all_particles()]).T).flatten()
    min_coord = np.amin(extreme_coords)
    max_coord = np.amax(extreme_coords)
    plt.axis([min_coord, max_coord, min_coord, max_coord])
    ax = plt.gca()

    nodes = []
    edges = []

    drawn_hexagons = {}

    for hexagon in compression_simulator.grid.get_all_particles():
        pos = hexagon.position

        nodes.append(pos)

        # Draw lines to neighbors
        neighbors_positions = [neighbor.position for neighbor in
                               compression_simulator.grid.get_neighbors(hexagon.axial_coordinates) if
                               neighbor not in drawn_hexagons]

        for neighbor_position in neighbors_positions:
            edges.append((pos, neighbor_position))

        drawn_hexagons[hexagon] = True

    nodes = np.asarray(nodes)
    edges = np.asarray(edges)

    node_collection = ax.scatter(nodes[:, 0], nodes[:, 1],
                                 s=node_size,
                                 c=node_color,
                                 marker=node_shape,
                                 label=label)

    node_collection.set_zorder(2)

    edge_collection = LineCollection(edges,
                                     linewidths=(line_widths,),
                                     antialiaseds=(1,),
                                     transOffset=ax.transData,
                                     )

    edge_collection.set_zorder(1)  # edges go behind nodes
    edge_collection.set_label(label)
    ax.add_collection(edge_collection)

    plt.savefig(filename)

    #plt.show()