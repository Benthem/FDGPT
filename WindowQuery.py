from pyqtree import Index
from Graphstuff import *
from math import sin, cos, pi


class TreeStruct:
    bbox = (-1000, -1000, 1000, 1000)

    ##
    # Maintain link from points to rectangle objects?
    def __init__(self):
        self.index = Index(bbox=self.bbox)

    def addRect(self, rect):
        # compute corner points
        index.insert(rect, rect.bbox)
        pass

    def removeRect(self, rect):
        index.remove(rect, rect.bbox)

    def query(self, rect):
        candidates = index.query(rect.bbox)
        
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

