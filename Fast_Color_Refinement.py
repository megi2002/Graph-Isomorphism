from graph_io import *
from collections import deque
from Color_Refinement import *


def initialize_queues(graph_list, i_q):
    queue_list = ([], [])
    for graph in graph_list:
        q = deque()
        s = set()
        for i in i_q:
            q.append(i)
            s.add(i)
        queue_list[0].append(q)
        queue_list[1].append(s)
    return queue_list


def color_degrees(graph):
    for vertex in graph.vertices:
        vertex.label = len(vertex.incidence)


# Color Refinement Algorithm
# Vertices with identically colored neighborhoods receive the same new color while differentiating
# vertices with different neighborhood color patterns.
def color_refinement(graph_list):
    iterations_count = {graph: 0 for graph in range(len(graph_list))}
    color_classes_temp = generate_color_classes(graph_list[0])
    initial_queue = []
    bigest_color = (-1, 0)
    for color, l in color_classes_temp.items():
        if bigest_color[0] == -1:
            bigest_color = (color, len(l))
        elif len(l) > bigest_color[1]:
            initial_queue.append(bigest_color[0])
            bigest_color = (color, len(l))
        else:
            initial_queue.append(color)
    queue_list = initialize_queues(graph_list, initial_queue)
    highest_color = max(color_classes_temp.keys()) + 1
    # COLORING REFINEMENT LOOP
    for graph in graph_list:
        graph.generate_color_classes()
    j = 0
    while not all(len(q) == 0 for q in queue_list[0]):  # Loop until all graphs have a stable coloring
        color_per_multiset = {}  # KEY: (color, color_neighbour, Incomiing Transitions) , VALUE: (Color for this multiset, where to enter ) (reset after each iteration)
        # FIRST - IDENTIFY ALL (NEW)UNIQUE NEIGHBORHOODS ACROSS ALL VERTICES IN ALL GRAPHS - DO NOT CHANGE COLORS YET !!!
        for i, graph in enumerate(graph_list):
            if not bool(queue_list[1][i]):
                continue  # if the que is empty this thing is done
            color_classes = graph.color_class
            color = queue_list[0][i].popleft()  # take the first color in the list
            queue_list[1][i].remove(color)
            new_color_vertex = {}  # KEY: color_neighbour, VALUE: Dict (KEY: Amount of Incomming Transitions, VALUe (set vertices) resets

            vertices = color_classes[color]
            for vertex in vertices:
                for neighbour in vertex.neighbours:
                    if neighbour.label == color:
                        continue
                    neighbour.t += 1
                    if not neighbour.label in new_color_vertex:  # then this color has never been seen and therefore neighbour.t must be 1
                        new_color_vertex[neighbour.label] = {neighbour.t: {neighbour}}
                        continue
                    if neighbour.t == 1:
                        new_color_vertex[neighbour.label][neighbour.t].add(neighbour)
                        continue
                    if neighbour.t not in new_color_vertex[
                        neighbour.label]:  # than this color and t combination has not been seen
                        new_color_vertex[neighbour.label][neighbour.t - 1].remove(neighbour)
                        new_color_vertex[neighbour.label][neighbour.t] = {neighbour}
                        continue
                    else:
                        new_color_vertex[neighbour.label][neighbour.t - 1].remove(neighbour)
                        new_color_vertex[neighbour.label][neighbour.t].add(neighbour)
            if not new_color_vertex:  # if there is nothing to refine
                continue
            to_add = []
            # we loop over all the colors that we can refine.
            for color_to_refine, incomming_vertices_dict in new_color_vertex.items():
                if len(incomming_vertices_dict) == 0:
                    continue  # if there are no incomming vertices just continue
                if len(incomming_vertices_dict) == 1:
                    value, = incomming_vertices_dict.values()
                    if len(value) == len(color_classes[
                                             color_to_refine]):  # if there is only 1 new collor but all vertices are in this its the same as the original color so you don't need to refine antying
                        for vertex in value:
                            vertex.t = 0
                        continue
                sum_check = 0  # this variable will keep counting up and we can check how many vertices we loop through and how many are left in the with no transitions to this class
                largest = (-1, 0)  #
                original_length = len(color_classes[color_to_refine])
                for incomming_transitoins, distinct_vertices in incomming_vertices_dict.items():
                    if len(distinct_vertices) == 0:  # if there are no vertices in with this amount of incomming transitions you can just skip it
                        continue
                    combi = (color, color_to_refine, incomming_transitoins)
                    if combi not in color_per_multiset:  # if we have already seen this combination before in previous graph we can just take this collor else we make a new color
                        color_per_multiset[combi] = highest_color
                        highest_color += 1
                    new_color = color_per_multiset[combi]
                    color_classes[new_color] = set()
                    for vertex in distinct_vertices:
                        sum_check += 1
                        vertex.label = new_color
                        vertex.t = 0
                        color_classes[color_to_refine].remove(vertex)
                        color_classes[new_color].add(vertex)
                    # adding to the queue
                    if color_to_refine in queue_list[1][i]:
                        to_add.append(new_color)
                    elif largest[0] == -1:
                        largest = (new_color, len(distinct_vertices))
                    elif len(distinct_vertices) > largest[1]:
                        to_add.append(largest[0])
                        largest = (new_color, len(distinct_vertices))
                    else:
                        to_add.append(new_color)
                if (largest[0] == -1):
                    continue
                if (color_to_refine not in queue_list[1][i]) and (largest[1] > (original_length - sum_check)):
                    to_add.append(color_to_refine)
                else:
                    to_add.append(largest[0])
            to_add = sorted(to_add)
            for element in to_add:
                queue_list[0][i].append(element)
                queue_list[1][i].add(element)
        j += 1
    return graph_list, iterations_count, 1


def main(graph_file):
    with open(graph_file, 'r') as f:
        graph_list, options = load_graph(f, read_list=True)

    for graph in graph_list:
        color_degrees(graph)

    refined_graphs, iterations_count, _ = color_refinement(graph_list)
    result = generate_output(refined_graphs, iterations_count)

    for group in result:
        if group[2]:
            print(f"{group[0]} discrete")
        else:
            print(f"{group[0]}")


if __name__ == "__main__":
    main("folder_name/file_name.grl")
