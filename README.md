![Pythagoras Trees](trees.png?raw=true)

# Force-directed Generalized Pythagoras Tree

Generalized Pythagoras trees [1] are an aesthetic approach to visualize hierarchies. However, visual overlap may decrease readability. Our approach removes all overlap and maintains the general structure of a tree.

This project provides the source code for the short paper [Overlap-Free Drawing of Generalized Pythagoras Trees for Hierarchy Visualization](https://ieeexplore.ieee.org/document/8933606).

## Getting Started

The system was developed for Python 3.7 and you need to install the packages listed in `requirements.txt`:
```
git clone https://github.com/ToonBoon/FDGPT
cd FDGPT
pip install -r requirements.txt
```

Start the system using `treevis.py`:
```
python treevis.py [input.in [rootID]]
```

There are multiple example input files available in the `input` directory. If no file is given when executing `treevis.py`, an example file will be loaded.
To visualize a subtree, rootID has to be specified. This will use the node with the given ID as root node (see input format for more information about node IDs).

## General Control

First, the hierarchy will be visualized as generalized Pythagoras tree. 

Use the following keys to run and visualize results of the algorithm:
* `Space` to run for 50 iterations
* `Left Ctrl` to load best configuration from automatically saved cache file determined for the same root ID
* `Left Alt` to load best configuration from automatically saved cache file determined for the root (with ID 0) of the hierarchy and merge it into the subtree currently being visualized
* `Left Shift` to load best configuration from current session (from internal memory)
* `R` to reset to the generalized Pythagoras tree before removing overlap

We provide interaction to navigate in the view:
* Click on a node to move this node to the position of the root node and zoom
* Hold middle mouse to draw a rectangle to zoom in on
* `W`/`A`/`S`/`D` for moving the view
* `Up`/`Down` arrow to zoom
* `Left`/`Right` arrow to rotate

## Input Format

The input file contains a file header followed by the hierarchy's nodes, one node per line:

```
<numNodes> <format>
<weight> <numChildren> <id_0> ... <id_n-1>*<name>
<weight> <numChildren> <id_0> ... <id_n-1>*<name>
...
```

The first line contains the total number of nodes in the tree and the input format (0 if nodes have no name, else 1).
Then, each line describes one node:
First, the weight of the node, then the number of children and the IDs of all children.
If the input format is set to 1, the text after a *\** character is used as name for the node.
The IDs are assigned to the nodes as they occur in the input file starting with 0.

### Example File

```
3 1
3 2 1 2*root
2 0*child 1
1 0*child 2
```

### Generating Input Files

`inputgenerator.py` provides some functions to generate input files for 
* some artificial hierarchies (n-ary, degenerated, self similar, symmetric, deep)
* the hierarchical structure of a file system (this will assign weights based on either the number of descendants or file size) 
* hierarchies given in the Newick format.
* hierarchies represented by any arbitrary Python dictionary object consisting of dictionaries as internal nodes and either strings (for a name) or tuples (string: name, int: weight) as leaves

## Citation

When referencing our work, please cite the paper [Overlap-Free Drawing of Generalized Pythagoras Trees for Hierarchy Visualization](https://ieeexplore.ieee.org/document/8933606).

T. Munz, M. Burch, T. v. Benthem, Y. Poels, F. Beck and D. Weiskopf. Overlap-Free Drawing of Generalized Pythagoras Trees for Hierarchy Visualization. In Proceedings of 2019 IEEE Visualization Conference (VIS), pp. 251-255, 2019. 

```
@inproceedings{vis2019pythagoras,
  author={Munz, Tanja and Burch, Michael and van Benthem, Toon and Poels, Yoeri and Beck, Fabian and Weiskopf, Daniel},
  booktitle={2019 IEEE Visualization Conference (VIS)}, 
  title={Overlap-Free Drawing of Generalized Pythagoras Trees for Hierarchy Visualization}, 
  year={2019},
  pages={251-255},
}
```
    
## References

[1] F. Beck, M. Burch, T. Munz, L. D. Silvestro, and D. Weiskopf. Generalized Pythagoras trees for visualizing hierarchies. In Proceedings of International Conference on Information Visualization Theory and Applications (IVAPP), pp. 17–28, 2014.
