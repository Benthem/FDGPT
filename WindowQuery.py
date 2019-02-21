from scipy.spatial import cKDTree


tree = cKDTree(data, copy_data=True)


'''
scipy.spatial.cKDTree
  Store datapoints by reference, when starting query convert to cKDTree and perform queries

Pyqtree
  Continuously delete/insert if position changes
  Might have better performance due to number of changes being low
'''
