from pyqtree import Index
from Graphstuff import *
from math import sin, cos, pi


# Checks if b1 is outside b2
def bboxoutside(b1, b2):
    return (b1[0] < b2[0] or b1[1] < b2[1] or b1[2] > b2[2] or b1[3] > b2[3])


class TreeStruct:
    bbox = (-1000, -1000, 1000, 1000)

    ##
    # Maintain link from points to rectangle objects?
    def __init__(self):
        self.index = Index(bbox=self.bbox)

    def addRect(self, rect):

        # TODO if rect outside bbox, make a new one.
        if (bboxoutside(rect.bbox, self.bbox))

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

