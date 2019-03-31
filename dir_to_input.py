import collections
import os
import sys
from Bio import Phylo
# module level stuff
this = sys.modules[__name__]
# assign weight by direct children if true, total number of descendants (or sum of element values if given) otherwise
this.weightbydirectchildren = False

# generate pathdict by storing filesize
this.usefilesize = True


def recurse(clade):
    name = clade.name
    if name is None:
        name = clade.confidence
    if not clade.clades:
        return name
    phylodict = {}
    for child in clade.clades:
        name = child.name
        if name is None:
            name = child.confidence
        phylodict[name] = recurse(child)
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
    #output = createpathdict('.')
    # output = createPhylodict('ncbi-taxonomy.tre')
    output = createPhylodict('hierarchy_degree5_depth5_randomDegree_degenerated.tre')
    print(output)
    outputlines = dict_to_output(output)
    # generate output from dir
    with open('filetree.in', 'w') as f:
        for line in outputlines:
            f.write(line)


if __name__ == "__main__":
    main()

