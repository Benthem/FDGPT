import collections
import os
import sys
from Bio import Phylo
# module level stuff
this = sys.modules[__name__]
# assign weight by direct children if true, total number of descendants if false
this.weightbydirectchildren = False


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


# create dict of files/folders in dir (recursively)
def createpathdict(dir):
    if os.path.isfile(dir):
        return str(os.path.basename(dir))
    try:
        content = os.listdir(dir)
    except PermissionError:
        return {}
    filedir = {}
    for item in content:
        if os.path.isfile(dir + '/' + item):
            filedir[item] = item
        else:
            returndict = createpathdict(dir + '/' + item)
            if len(returndict) > 0:
                filedir[item] = returndict
    return filedir


def dict_recurse(dict, id, dictname):
    directchildren = this.weightbydirectchildren
    w = 0

    # leaf weight
    leafw = 1
    # update global id as we handle a new node
    this.id += 1

    ids = []
    # if children, append them (should always be the case)
    if len(dict) > 0:
        for key, value in dict.items():
            if not isinstance(value, collections.Mapping):
                # found a leaf
                leafoutput = str(leafw) + ' 0*' + str(value) + '\n'
                this.outputdict[this.id] = leafoutput
                ids.append(this.id)
                # update global id as we handle a new node
                this.id += 1
                w += leafw
            else:
                # recurse further
                ids.append(this.id)
                w += dict_recurse(value, this.id, key)
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
    dict_recurse(dict, this.id, os.getcwd().split(os.sep)[-1])
    sorted_by_id = sorted(this.outputdict.items(), key=lambda kv: kv[0])
    output = []
    output.append(str(len(sorted_by_id)) + ' 1\n')
    for line in sorted_by_id:
        output.append(line[1])
    return output


def main():
    # output = createpathdict('.')
    output = createPhylodict('ncbi-taxonomy.tre')
    outputlines = dict_to_output(output)
    # generate output from dir
    with open('filetree.in', 'w') as f:
        for line in outputlines:
            f.write(line)


if __name__ == "__main__":
    main()

