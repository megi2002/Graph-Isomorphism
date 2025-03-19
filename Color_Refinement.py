from graph_io import load_graph


def is_discrete(graph):
    # Assuming `graph.vertices` is a list of Vertex objects with a 'label' attribute
    vertex_colors = set(v.label for v in graph.vertices)
    if len(vertex_colors) == len(graph.vertices):
        return True
    return False


def set_initial_coloring_for_branching(graph_list, D, I):  # Degree coloring
    G = graph_list[0]
    H = graph_list[1]
    for v in G.vertices:
        if v not in D:
            v.label = 1
    for v in H.vertices:
        if v not in I:
            v.label = 1
    graph_list[0] = G
    graph_list[1] = H
    return graph_list


def set_initial_coloring(graph_list):  # Degree coloring

    for graph in graph_list:
        for v in graph.vertices:
            v.label = 1
    return graph_list

def set_initial_coloring_pair(G, H):  # Degree coloring
    for v in G.vertices:
        v.label = 1

    for v in H.vertices:
        v.label = 1
    return G, H


def generate_graph_signature(graphs):
    graph_signatures = {}  # KEY: unique signature, VALUE: list of graphs with this signature

    for i, graph in enumerate(graphs):
        vertex_signatures = []

        # Create a signature for each vertex
        for vertex in graph.vertices:
            vertex_color = vertex.label
            neighbours_colors = sorted([neighbour.label for neighbour in vertex.neighbours])
            vertex_signature = (vertex_color, tuple(neighbours_colors))
            vertex_signatures.append(vertex_signature)

        vertex_signatures.sort()
        graph_signature = tuple(vertex_signatures)

        if graph_signature not in graph_signatures:
            graph_signatures[graph_signature] = []
        graph_signatures[graph_signature].append(i)

    return graph_signatures


# GROUP GRAPHS BASED ON IDENTICAL COLOR PATTERNS and format the output
def generate_output(graph_list, iterations_count):
    color_patterns = generate_graph_signature(graph_list)  # KEY: Color pattern, VALUE: List of graphs with this color pattern
    output = []
    for color_pattern, graph_indices in color_patterns.items():
        iterations = iterations_count[color_patterns[color_pattern][0]]  # Number of iterations for the first graph in the group
        discrete = is_discrete(graph_list[color_patterns[color_pattern][0]])

        output.append((graph_indices, iterations, discrete))

    return output


def generate_color_classes(graph):
    a_c = {}  # KEY: Color, VALUE: List of vertices with this color - Color classes
    for vertex in graph.vertices:
        vertex_color = vertex.label
        # If the color is not in the dictionary, add it and assign it a list with the vertex
        if vertex_color not in a_c:
            a_c[vertex_color] = [vertex]
        # If the color is already in the dictionary, append the vertex to the list of vertices with this color
        else:
            a_c[vertex_color].append(vertex)
    return a_c


# Color Refinement Algorithm
# Vertices with identically colored neighborhoods receive the same new color while differentiating vertices with different neighborhood color patterns.
def color_refinement(graph_list):
    iterations_count = {graph: 0 for graph in range(len(graph_list))}
    stable_coloring_per_graph = {i: False for i in range(len(graph_list))}
    refinement_of_color_history = {i: [] for i in range(len(graph_list))}
    color_classes_graphs = {}

    # COLORING REFINEMENT LOOP
    while not all(stable_coloring_per_graph.values()):  # Loop until all graphs have a stable coloring

        color_per_multiset = {}  # KEY: Neighbourhood type, VALUE: Color for this multiset (reset after each iteration)
        multiset_current_color = {}
        # FIRST - IDENTIFY ALL (NEW)UNIQUE NEIGHBORHOODS ACROSS ALL VERTICES IN ALL GRAPHS - DO NOT CHANGE COLORS YET !!!
        for i, graph in enumerate(graph_list):

            if stable_coloring_per_graph[i]:
                continue

            refinement_of_color_per_graph = {}
            color_classes = generate_color_classes(graph)
            new_color_vertex = {}  # KEY: Vertex, VALUE: Intended new color (reset after each iteration)

            stable_coloring = True  # Assume graph is stable until proven otherwise

            # Identify all unique neighborhoods WITHIN EACH COLOR CLASS and generate new colors for them
            for color in color_classes:

                vertices = color_classes[color]
                refinement_of_color_class = []

                for v in vertices:
                    neighbor_colors = tuple(sorted([u.label for u in v.neighbours]))  # Sorted list of colors of the neighbors

                    # If this type of neighbourhood is not already in the dictionary, add it and assign it a new color(add a new key to the dictionary and assign it a value)
                    if neighbor_colors not in color_per_multiset:
                        color_per_multiset[neighbor_colors] = len(color_per_multiset)

                    if neighbor_colors not in multiset_current_color:
                        multiset_current_color[neighbor_colors] = [v]
                    else:
                        multiset_current_color[neighbor_colors].append(v)

                    # Track intended new colors for each vertex
                    new_color_vertex[v] = color_per_multiset[neighbor_colors]
                    refinement_of_color_class.append(color_per_multiset[neighbor_colors])

                refinement_of_color_per_graph[color] = refinement_of_color_class



                # IF THE COLOR CLASS HAS BEEN REFINED INTO MORE COLORS, THE GRAPH IS NOT STABLE
                if len(set(refinement_of_color_class)) > 1:
                    stable_coloring = False

            if refinement_of_color_per_graph in refinement_of_color_history[i]:
                for multiset in multiset_current_color.keys():
                    vertices = multiset_current_color[multiset]
                    vertices_colors = [v.label for v in vertices]
                    if len(set(vertices_colors)) > 1:
                        chosen_color = vertices[0].label
                        for v in vertices:
                            v.label = chosen_color
            else:
                if stable_coloring == False:
                    # SECOND - ASSIGN NEW COLORS TO VERTICES BASED ON THEIR NEIGHBORHOODS
                    for vertex, new_color in new_color_vertex.items():
                        # if the algorithm is used for branching the condition 'v.label >= 0' should be added
                        if vertex.label != new_color:
                            vertex.label = new_color

            if stable_coloring:
                color_classes_graphs[i] = generate_color_classes(graph)
                stable_coloring_per_graph[i] = True
            else:
                iterations_count[i] += 1

            refinement_of_color_history[i].append(refinement_of_color_per_graph)

    return graph_list, iterations_count, color_classes_graphs



def main(graph_file):
    with open(graph_file, 'r') as f:
        graph_list, options = load_graph(f, read_list=True)

    graph_list = set_initial_coloring(graph_list)

    refined_graphs, iterations_count, _ = color_refinement(graph_list)
    result = generate_output(refined_graphs, iterations_count)

    for group in result:
        if group[2]:
            print(f"{group[0]} {group[1]} discrete")
        else:
            print(f"{group[0]} {group[1]}")

if __name__ == "__main__":
    main("folder_name/file_name")


