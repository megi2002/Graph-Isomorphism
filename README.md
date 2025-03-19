# Graph Isomorphism Problem

The Graph Isomorphism Problem is a computational challenge that involves determining 
whether two finite graphs are isomorphic. This means checking if there is a one-to-one correspondence 
between the vertices of the two graphs such that the adjacency relations are preserved. 

# Graph Automorphism Problem

The Graph Automorphism Problem involves determining the set of all automorphisms of a given graph. 
An automorphism is a permutation of the graph's vertices that preserves the graph's edge structure. 
Essentially, it's a way of rearranging the graph's vertices so that the graph looks the same as before the rearrangement. 
This problem is important in various fields such as chemistry, physics, and computer science, 
for tasks that involve understanding the symmetry properties of graphs.

# GI Algorithm

The GI_Algorithm.py program utilizes the Color Refinement Algorithm, it takes as input a file of graphs and 
determines if the graphs are identical in structure, regardless of how the vertices are labeled or how they are drawn. 
It also solves the Graph Automorphism Problem by computing the number of automorphisms of a given graph.

## Usage

A folder containing graph files with the '.grl' extension should be added to the repository.
The files array in the main() function should be changed to contain the correct names of the graph files

```python
files = ["file1GI.grl", "file2GI.grl", "file3GI.grl", "file4GI.grl", "file5Aut.grl", "file6GIAut.grl", "file7GIAut.grl"]
```

The filenames should contain certain key-words:
- for solving the GI problem: the filename should end in "GI"
- for solving the Aut problem: the filename should end in "Aut"
- for solving both the GI problem and the Aut problem: the filename should end in "GIAut"

The argument of the main() function should be changed to the folder name and 
the main() function should be called.

```python
if __name__ == "__main__":
    main("folder_name/")
```

# Fast Color Refinement Algorithm

The fast color refinement algorithm improves basic color refinement by efficiently updating vertex colors. It uses 
queues to manage updates, processing only vertices that need refinement, thus speeding up the stabilization of color classes. 

## Usage

A folder containing graph files with the '.grl' extension should be added to the repository.
The argument of the main() function should be changed to the correct folder_name and file_name, and 
the main() function should be called.

```python
if __name__ == "__main__":
    main("folder_name/file_name.grl")
```

# Color Refinement Algorithm

Color refinement is a method to distinguish graphs by organizing vertices into color classes 
based on their neighbours. Initially, all vertices start with the same colors. The algorithm updates these 
colors iteratively by considering the colors of adjacent vertices. This process continues until no further changes occur, 
resulting in stable color classes.

## Usage

A folder containing graph files with the '.grl' extension should be added to the repository.
The argument of the main() function should be changed to the correct folder_name and file_name, and 
the main() function should be called.

```python
if __name__ == "__main__":
    main("folder_name/file_name.grl")
```