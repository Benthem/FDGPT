import collections
import os
import sys

# module level stuff
this = sys.modules[__name__]


# create dict of files/folders in dir (recursively)
def createpathdict(dir):
    if os.path.isfile(dir):
        return str(os.path.basename(dir))
    content = os.listdir(dir)
    filedir = {}
    for item in content:
        if os.path.isfile(dir + '/' + item):
            filedir[item] = item
        else:
            filedir[item] = createpathdict(dir + '/' + item)
    return filedir


def dict_recurse(dict, id):
    # weight = length of dict+1
    w = len(dict) + 1
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
                leafoutput = str(leafw) + ' 0\n'
                this.outputdict[this.id] = leafoutput
                ids.append(this.id)
                # update global id as we handle a new node
                this.id += 1
            else:
                # recurse further
                ids.append(this.id)
                dict_recurse(value, this.id)
    outputstring = str(w) + ' ' + str(len(dict))
    for childid in ids:
        outputstring += ' ' + str(childid)
    outputstring += '\n'
    this.outputdict[id] = outputstring


# convert arbitrary dict to list of lines to print to output file
def dict_to_output(dict):
    this.id = 0
    this.outputdict = {}
    dict_recurse(dict, this.id)
    sorted_by_id = sorted(this.outputdict.items(), key=lambda kv: kv[0])
    output = []
    output.append(str(len(sorted_by_id))+'\n')
    for line in sorted_by_id:
        output.append(line[1])
    return output

def main():
    output = createpathdict('.')
    outputlines = dict_to_output(output)
    # generate output from dir
    with open('filetree.in', 'w') as f:
        for line in outputlines:
            f.write(line)

if __name__ == "__main__":
    main()

