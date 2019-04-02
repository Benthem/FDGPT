import collections
import math
import os
import random
import sys
from Bio import Phylo
# module level stuff
this = sys.modules[__name__]
# assign weight by direct children if true, total number of descendants (or sum of element values if given) otherwise
this.weightbydirectchildren = False

# generate pathdict by storing filesize
this.usefilesize = True


def recurse(clade):
    if not clade.clades:
        return clade.name
    phylodict = {}
    for child in clade.clades:
        phylodict[child.name] = recurse(child)
    return phylodict


def createPhylodict(filename):
    trees = Phylo.parse(filename, 'newick')
    a = next(trees)
    b = next(trees)
    phylodict = recurse(b.clade)
    return phylodict


def handlefile(file):
    if this.usefilesize:
        tuple = (str(os.path.basename(file)), max(1, int(os.path.getsize(file))))
        return tuple
    else:
        return str(os.path.basename(file))

# create dict of files/folders in dir (recursively)
def createpathdict(dir):
    if os.path.isfile(dir):
        return handlefile(dir)
    try:
        content = os.listdir(dir)
    except PermissionError:
        return {}
    filedir = {}
    for item in content:
        if os.path.isfile(dir + '/' + item):
            filedir[item] = handlefile(dir + '/' + item)
        else:
            returndict = createpathdict(dir + '/' + item)
            if len(returndict) > 0:
                filedir[item] = returndict
    return filedir


def dict_recurse(dict, id, dictname, reverse):
    directchildren = this.weightbydirectchildren
    if dictname == 'reverse':
        reverse = True
    w = 0

    # leaf weight
    leafw = 1
    # update global id as we handle a new node
    this.id += 1

    ids = []
    # if children, append them (should always be the case)
    if len(dict) > 0:
        toiterate = sorted(dict.items())
        if reverse:
            toiterate = reversed(toiterate)
        for key, value in toiterate:
            if not isinstance(value, collections.Mapping):
                istuple = isinstance(value, tuple)
                # found a leaf
                if istuple:
                    leafoutput = str(value[1]) + ' 0*' + str(value[0]) + '\n'
                else:
                    leafoutput = str(leafw) + ' 0*' + str(value) + '\n'
                this.outputdict[this.id] = leafoutput
                ids.append(this.id)
                # update global id as we handle a new node
                this.id += 1
                if istuple:
                    w += value[1]
                else:
                    w += leafw
            else:
                # recurse further
                ids.append(this.id)
                w += dict_recurse(value, this.id, key, reverse)
    if directchildren:
        w = len(dict) + 1
    outputstring = str(w) + ' ' + str(len(dict))
    for childid in ids:
        outputstring += ' ' + str(childid)
    outputstring += '*' + str(dictname) + '\n'
    this.outputdict[id] = outputstring
    return w


# convert arbitrary dict to list of lines to print to output file
def dict_to_output(dict):
    this.id = 0
    this.outputdict = {}
    dict_recurse(dict, this.id, os.getcwd().split(os.sep)[-1], False)
    sorted_by_id = sorted(this.outputdict.items(), key=lambda kv: kv[0])
    output = []
    output.append(str(len(sorted_by_id)) + ' 1\n')
    for line in sorted_by_id:
        output.append(line[1])
    return output


# generate hierarchy with specified branching factor and depth
def nary_dict(branching, depth):
    if depth == 0:
        return 'leaf'
    root = {}
    for i in range(0, branching):
        root[str(i)] = nary_dict(branching, depth-1)
    return root

# generate hierarchy with n children each, decreasing by 1 every iteration. Variance = random
def recursive_hierarchy(n, c, variancec=0, varianced=0):
    if n == 1:
        return 'leaf'
    root = {}
    crange = c
    if variancec > 0:
        crange += random.randint(-variancec, variancec)
        if crange <= 1:
            return 'leaf'
    drange = n
    if varianced > 0:
        drange += random.randint(-varianced, varianced)
        if drange <= 1:
            return 'leaf'
    for i in range(0, crange):
        root[str(i)] = recursive_hierarchy(n-1, c, variancec, varianced)
    return root

def degenerated_dict(n):
    root = {}
    current = root
    while n > 0:
        current['s'+str(n)] = nary_dict(2, 6)
        current['t'+str(n)] = {}
        current = current['t'+str(n)]
        n -= 1
    current['f1'] = nary_dict(2, 6)
    current['f2'] = nary_dict(2, 6)
    return root


def self_similar(size, depth):
    if depth == 0 or size == 1:
        return 'leaf'
    root = {}
    for i in range(1, size+1):
        root[str(i)] = self_similar(i, depth-1)
    return root

def symmetric_recursive(n, c, variancec=0, varianced=0):
    hierarchy = recursive_hierarchy(n, c, variancec, varianced)
    root = {}
    root['normal'] = hierarchy
    root['reverse'] = hierarchy
    return root

def main():
    #output = createpathdict('.')
    #SYMMETRIC
    #output = symmetric_recursive(7, 3, 2, 6)
    #SELF_SIMILAR
    #output = self_similar(7, 8)
    #BIG
    #output = recursive_hierarchy(15, 2, 1, 10)
    #DEGEN
    #output = degenerated_dict(10)
    # output = createPhylodict('ncbi-taxonomy.tre')
    output = self_similar(7, 5)
    outputlines = dict_to_output(output)
    # generate output from dir
    with open('input/degen.in', 'w') as f:
        for line in outputlines:
            f.write(line)


if __name__ == "__main__":
    main()

