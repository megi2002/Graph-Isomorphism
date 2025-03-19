from graph_io import load_graph


def set_initial_coloring_DI(G, H, D, I):
    D = list(D or [])
    I = list(I or [])

    for index, v in enumerate(G.vertices):
        if v in D:
            v.label = -(D.index(v) + 1)  # Use index in D to set label
        else:
            v.label = 1

    for index, v in enumerate(H.vertices):
        if v in I:
            v.label = -(I.index(v) + 1)  # Use index in I to set label
        else:
            v.label = 1

    return G, H


def is_discrete(graph):
    vertex_colors = set(v.label for v in graph.vertices)
    if len(vertex_colors) == len(graph.vertices):
        return True
    return False


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


def set_initial_coloring(graph_list):

    for graph in graph_list:
        for v in graph.vertices:
            v.label = 1
    return graph_list


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


def calculateEquivalenceClasses(graph_list, find, auto):
    global isom
    graph_list = set_initial_coloring(graph_list)
    refined_graphs, _, _ = color_refinement(graph_list)
    color_patterns = generate_graph_signature(
        graph_list)  # KEY: Color pattern, VALUE: List of graphs with this color pattern

    equivalence_classes = {}
    for color_pattern in color_patterns.keys():
        balanced_graphs = color_patterns[color_pattern]
        for g in balanced_graphs:
            for h in balanced_graphs:
                G = graph_list[g]
                H = graph_list[h]
                if G != H:
                    if find:
                        #H = graph_list[h]
                        isom = findIsomorphism(G, H, [], [])
                    else:
                        H = graph_list[h].copy()
                        isom = countIsomorphism(G, H, [], [])
                    if isom > 0:
                        if g not in equivalence_classes:
                            equivalence_classes[g] = tuple([[h], isom])
                        else:
                            graphs = equivalence_classes[g][0]
                            new_graphs = set(graphs + [h])
                            equivalence_classes[g] = tuple([list(new_graphs), isom])


    for g in range(len(graph_list)):
        if g not in equivalence_classes:
            if find:
                equivalence_classes[g] = tuple([[-1], 1])
            else:
                isom = countIsomorphism(graph_list[g], graph_list[g].copy(), [], [])
                equivalence_classes[g] = tuple([[-1], isom])

    equivalence_classes_auto = {}
    for key, value in equivalence_classes.items():
        g1 = [key]
        g_rest = value[0]
        if g_rest != [-1]:
            equivalence_class = tuple(list(set(sorted(g1 + g_rest))))
            if equivalence_class not in equivalence_classes_auto.keys():
                equivalence_classes_auto[equivalence_class] = value[1]
        else:
            equivalence_class = tuple(g1)
            if equivalence_class not in equivalence_classes_auto.keys():
                equivalence_classes_auto[equivalence_class] = value[1]

    return equivalence_classes_auto


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

            if stable_coloring == False:
                # SECOND - ASSIGN NEW COLORS TO VERTICES BASED ON THEIR NEIGHBORHOODS
                for vertex, new_color in new_color_vertex.items():
                    if vertex.label != new_color and vertex.label >= 0: # if this is not a mapped vertex from branching - a negative number
                        vertex.label = new_color

            if stable_coloring:
                color_classes_graphs[i] = generate_color_classes(graph)
                stable_coloring_per_graph[i] = True
            else:
                iterations_count[i] += 1

            refinement_of_color_history[i].append(refinement_of_color_per_graph)

    return graph_list, iterations_count, color_classes_graphs


def findIsomorphism(G, H, D, I):
    # get stable coloring that refines further given D and I - which are initially empty
    graph1, graph2 = set_initial_coloring_DI(G, H, D, I)
    refined_graphs, _, color_classes_graphs = color_refinement([graph1, graph2])  # coarsest stable coloring β

    # KEY: Color pattern, VALUE: List of graphs with this color pattern
    color_patterns = generate_graph_signature(refined_graphs)
    # if the two graphs have different color patterns they are unbalanced and the length of the dict will be 2
    if len(color_patterns.keys()) != 1:
        # G and H are unbalanced
        return 0
    if is_discrete(graph1) and is_discrete(graph2):
        return 1

    # filter color classes in both graphs where the color class size is less than 2
    for graph_index, color_class_dict in color_classes_graphs.items():
        keys_to_remove = [key for key, vertex_list in color_class_dict.items() if len(vertex_list) < 2]
        for key in keys_to_remove:
            del color_class_dict[key]

    color_classes_G = color_classes_graphs[0]
    color_classes_H = color_classes_graphs[1]

    # now that color classes of both graphs have length equal or above 4, we choose x and y
    C = next((cls for cls in color_classes_G.values()
              if (len(cls) >= 2)), None)
    x = C[0]
    num_isomorphisms = 0

    corresponding_color_class_H = color_classes_H[x.label]
    for i, y in enumerate(corresponding_color_class_H):
        # recursive call to explore the branch with the new D and I extended by x and y
        if num_isomorphisms < 1:
            num_isomorphisms += findIsomorphism(G, H, D + [x], I + [y])
        else:
            return num_isomorphisms

    return num_isomorphisms


def countIsomorphism(G, H, D, I):
    # get stable coloring that refines further given D and I - which are initially empty
    graph1, graph2 = set_initial_coloring_DI(G, H, D, I)
    refined_graphs, _, color_classes_graphs = color_refinement([graph1, graph2])  # coarsest stable coloring β

    # KEY: Color pattern, VALUE: List of graphs with this color pattern
    color_patterns = generate_graph_signature(refined_graphs)
    # if the two graphs have different color patterns they are unbalanced and the length of the dict will be 2
    if len(color_patterns.keys()) != 1:
        # G and H are unbalanced
        return 0
    if is_discrete(graph1) and is_discrete(graph2):
        return 1

    # filter color classes in both graphs where the color class size is less than 2
    for graph_index, color_class_dict in color_classes_graphs.items():
        keys_to_remove = [key for key, vertex_list in color_class_dict.items() if len(vertex_list) < 2]
        for key in keys_to_remove:
            del color_class_dict[key]

    color_classes_G = color_classes_graphs[0]
    color_classes_H = color_classes_graphs[1]

    # now that color classes of both graphs have length equal or above 4, we choose x and y
    C = next((cls for cls in color_classes_G.values()
              if (len(cls) >= 2)), None)
    x = C[0]
    num_isomorphisms = 0

    corresponding_color_class_H = color_classes_H[x.label]
    for i, y in enumerate(corresponding_color_class_H):
        # recursive call to explore the branch with the new D and I extended by x and y
        num_isomorphisms += countIsomorphism(G, H, D + [x], I + [y])

    return num_isomorphisms


def main(graph_file):
    files = ["file1GI.grl", "file2GI.grl", "file3GI.grl",
             "file4GI.grl", "file5Aut.grl", "file6Aut.grl", "file7GIAut.grl"]
    for filename in files:
        with open(graph_file + filename, 'r') as f:
            graph_list, options = load_graph(f, read_list=True)

        if filename.__contains__('GI') and filename.__contains__('Aut') and filename.__contains__('grl'):
            print('\n'+filename)
            equivalence_classes_auto = calculateEquivalenceClasses(graph_list, False, False)
            print('Equivalence classes:\t\t\t#Aut:')
            for ec, auto in equivalence_classes_auto.items():
                print(f"{list(ec)}\t\t\t\t\t{auto}")

        elif filename.__contains__('GI'):
            print('\n'+filename)
            equivalence_classes_auto = calculateEquivalenceClasses(graph_list, True, False)
            print('Equivalence classes:')
            for ec in equivalence_classes_auto.keys():
                print(f"{list(ec)}")

        elif filename.__contains__('Aut'):
            print('\n'+filename)
            equivalence_classes_auto = calculateEquivalenceClasses(graph_list, False, True)
            print('Graph:\t\t\t#Aut:')
            for ec, auto in equivalence_classes_auto.items():
                print(f"{list(ec)}\t\t\t\t{auto}")


if __name__ == "__main__":
    main("test_files/")

