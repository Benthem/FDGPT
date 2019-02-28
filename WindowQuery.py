from pyqtree import Index
from Graphstuff import *
from math import sin, cos, pi


class TreeStruct

    var = 1

    ##
    # Maintain link from points to rectangle objects?
    def __init__(self, data=[]):
        self.data += [i for i in data]

    def addRect(self, rect):
        # compute corner points


        print(self.data)

    def build(self):
        self.built = True
        self.tree = KDTree(self.data, metric='chebyshev')

    def query(self, rect):
        if not built:
            print('tree not built')
            return
        # Compute radius based on size and angle
        # Then query for points
        # Then figure out which points are actually within the query rectangle.


tree = TreeStruct()
tree.addRect(Rectangle((0, 0), 2, 1, pi / 3))

'''
sklearn KDTree
scipy.spatial.cKDTree
  Store datapoints by reference, when starting query convert to cKDTree and perform queries

Pyqtree
  Continuously delete/insert if position changes
  Might have better performance due to number of changes being low
'''

