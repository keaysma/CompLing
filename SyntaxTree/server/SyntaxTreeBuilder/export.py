
from anytree import Node, RenderTree
from anytree.exporter import UniqueDotExporter
from PyDictionary import PyDictionary
from random import randint

def anyTree(tree, parent = None):
    rand_int_max = 999999999
    if parent is None and len(tree) == 1:
        root = Node(str(randint(0, rand_int_max)), dname = tree[0]['pos'])
        anyTree(tree[0]['words'], root)
        return root
    for child in tree:
        if type(child) is dict:
            node = Node(str(randint(0, rand_int_max)), dname = child['pos'], parent = parent)
            anyTree(child['words'], node)
        if type(child) is str:
            node = Node(str(randint(0, rand_int_max)), dname = child, parent = parent)
    return None

def textAnyTree(anyTreeRoot):
    output = ""
    for pre, fill, node in RenderTree(anyTreeRoot):
        output += "{}{}<br/>".format(pre, node.dname)
    return output
        
def graphAnyTree(anyTreeRoot, filename):
    def nodenamefunc(node):
        return '%s' % (node.name)
    
    UniqueDotExporter(anyTreeRoot, 
                      nodenamefunc=nodenamefunc,
                      nodeattrfunc=lambda node: 'label="{}";shape=none'.format(node.dname)).to_picture("{}.png".format(filename))

def latexTree(tree, depth = 1):
    latexKeys = {
        "xbar" : '$\\bar{{{}}}$'
    }
    
    if type(tree) == str:
        return tree + " "
    if type(tree) == type([]):
        t = tree[0]
        if type(t) == str:
            return t + " "
    label = t['pos']
    if len(label) == 1:
        label = label.upper()
    ploc = label.find('P')
    if ploc > 0:
        if len(label[:ploc]) == 1:
            label = label.upper()
    barloc = label.find('bar')
    if barloc > 0:
        sublabel = label[:barloc]
        if len(sublabel) == 1:
            sublabel = sublabel.upper()
        label = latexKeys["xbar"].format(sublabel)
    if len(t['words']) == 1:
        return '[.{} {}]'.format(label, latexTree(t['words'], depth+1))
    return '[.{} \n{}{} \n{}{}]'.format(label, ' '*depth, latexTree([t['words'][0]], depth+1), ' '*depth, latexTree([t['words'][1]], depth+1))