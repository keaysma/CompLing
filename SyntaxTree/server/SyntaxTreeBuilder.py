#Imports
import re
import nltk
import math
import requests
import ast
from random import randint
from bs4 import BeautifulSoup
from PyDictionary import PyDictionary
from anytree import Node, RenderTree
from anytree.exporter import UniqueDotExporter
#sudo apt install graphviz

def saveDict(d, filename):
    sD = str(d)
    f = open(filename, 'w')
    f.write(sD)
    f.close()
    
def loadDict(filename):
    f = open(filename, 'r')
    sD = f.read()
    f.close()
    d = ast.literal_eval(sD)
    return d

def fetchLikelyClass(word = None, rid_url = None):
    url = "https://www.wordsmyth.net/?level=3&ent={}".format(word) if word else rid_url
    s = requests.Session()
    res = s.get(url, verify = False)
    
    likely_class = None
    soup = BeautifulSoup(res.text, 'html5lib')
    
    # There are multiple parts of speech of the word, and just one definition
    '''
    mainlist = soup.findAll("dl", {"class": "mainlist"})
    if len(mainlist) == 1:
        many_parts_of_speech_title = mainlist[0].findAll("dt", text='parts of speech:')
        if len(many_parts_of_speech_title) == 1:
            many_parts_of_speech = many_parts_of_speech_title[0].findNext("dd")
            return [_.text for _ in mpos.findAll("a")]
    '''
    
    # There is a single definition for this word
    maintable = soup.findAll("table", {"class": "maintable"})
    if len(maintable) == 1:
        part_of_speach_row = maintable[0].findAll("tr", {"class": "postitle"})
        likely_class = part_of_speach_row[0].find_all('td', {"class": "data"})[0].a.text
        return [likely_class] if word else likely_class
   
    # Make sure this is not a words suggestion page, if it is return None
    foobar = soup.findAll("div", {"class": "list_title"})
    if len(foobar) == 1 and foobar[0].text.strip() == "Did you mean this word?":
        return None

    # This is a page to pick between multiple definitions
    wordlist = soup.findAll("div", {"class": "wordlist"})
    if len(wordlist) == 1:
        ref_links = wordlist[0].table.tbody.findAll("a")
        return [fetchLikelyClass(rid_url = ref['href']) for ref in ref_links]
    
    # No definition found
    return None

def getLikelyClass(word, localBank, convert = True, save = False):
    if word in localBank:
        return localBank[word]
    
    rawClassList = fetchLikelyClass(word)
    classList = list(set(rawClassList)) #[item for sublist in rawClassList for item in sublist]
    
    switch = {
        'determiner'          :        'd',
        'noun'                :        'n',
        'pronoun'             :        'pn',
        'preposition'         :        'p',
        'verb'                :        'v',
        'transitive verb'     :        'v', #vt
        'intransitive verb'  :         'v', #vi
        'ditransitive verb'  :         'v', #vd
        'adjective'           :        'adj',
        'adverb'              :        'adv',
        'conjunction'         :        'conj',
    }
    
    if convert or save:
        #classList = [switch[_] for _ in classList]
        newClassList = []
        for classItem in classList:
            if classItem in switch:
                newClassList.append(switch[classItem])
        classList = newClassList
        
    if save and classList is not None:
        localBank[word] = classList
    return classList

def defineLikelyClass(word, wordClass, force=False):
    if word not in localBank or force:
        localBank[word] = wordClass
        return True
    return False

#This will build all of the possible base cases for perspective
#based on research forensics for each given word
def constructPerspective(tokens, parts_of_speach):
    return [{'pos' : parts_of_speach[i], 'words' : [tokens[i]]} for i in range(len(tokens))]

def constructPerspectivePermutations(pool, pile = []):
    if len(pool) == 0:
        return pile
    else:
        if len(pile) == 0:
            return constructPerspectivePermutations(pool[1:], [[_] for _ in pool[0]])
        front_pos, newpile = pool[0], []
        for pool_item in front_pos:
            for pile_item in pile:
                newpile_item = pile_item + [pool_item]
                newpile.append(newpile_item)
        return constructPerspectivePermutations(pool[1:], newpile)
    if len(newpile) > 0:
        return newpile
    return pile

def constructBasePerspectives(sentence, localBank):
    perspectives = []
    tokens = sentence.strip().split(" ")
    parts_of_speach = [getLikelyClass(_, localBank, save = True) for _ in tokens]
    permutations = constructPerspectivePermutations(parts_of_speach)
    return [constructPerspective(tokens, _) for _ in permutations], localBank

#I am Michael, I love Raquel, I eat protien, etc...
rules = {
    "adjP" : [["adjbar"]],
    "adjbar" : [["adj"], ["advP", "adjbar"]],
    "advP" : [["advbar"]],
    "advbar" : [["adv"], ["advP", "advbar"]],
    "nbar": [["adjP", "nbar"], ["nbar", "pP"], ["n"], ["n", "pP"], ["pn"]],
    "nP" : [["nbar"], ["nP", "conj", "nP"]],
    "dbar" : [["d", "nP"], ["nP"]],
    "dP" : [["dP", "dbar"], ["dbar"], ["dP", "conj", "dP"]],
    "pbar" : [["p", "dP"]],
    "pP" : [["pbar"]],
    "vP" : [["vbar"], ["vP", "conj", "vP"]],
    "vbar" : [["vbar", "pP"], ["vbar", "advP"], ["advP", "vbar"], ["vbar", "dP"], ["v"], ["v", "pP"], ["v", "dP"], ["v", "adjP"], ["v", "vP"]],
    "negbar" : [["neg", "vP"]],
    "negP" : [["negbar"]],
    "t" : [["v"]],
    "tbar" : [["vP"], ["t", "vP"], ["t", "negP"]],
    "tP" : [["dP", "tbar"], ["tP", "conj", "tP"]],
    "cbar" : [["c", "tP"], ["tP"]],
    "cP" : [["cbar"], ["cP", "conj", "cP"]]
}

#determines if the given rule is at the top of a given tree
#Strict disallows the tree from having different neighbors at the top
def inTreeTop(tree, rule, strict = False):
    retVal = False
    strictVal = True
    for topNode in tree:
        if topNode['pos'] == rule:
            retVal = True
        else:
            strictVal = False
    if strict:
        return (retVal, strictVal)
    return retVal

def pruneTrees(trees):
    pruned = []
    for tree in trees:
        finishedVal = inTreeTop(tree, "cP", strict = True)
        if finishedVal[0] and finishedVal[1]:
            pruned.append(tree)
    return pruned

#Debugging handling, small but out of the tree builder to keep things clean
def dprint(statement, currentLevel, evalLevel, **kwargs):
    if currentLevel >= evalLevel or currentLevel == -1:
        print(statement, **kwargs)
        
def matchRules(perspective = [], verbose = 0):
    global rules
    
    matches = {}
    for rule, conditionSet in rules.items():  
        dprint("rule {}".format(rule), verbose, 5)
        for conditions in conditionSet:
            conditionMatch, conditionPosition = 0, 0
            dprint("\tcond {}".format(str(conditions)), verbose, 5, end='')
            dprint(": ", verbose, 6, end='\n')
            for i in range(len(perspective)):
                node = perspective[i]
                if node['pos'] == conditions[conditionMatch]:
                    dprint("\t\t{} <- {}({})".format(rule, node['pos'], node['words']), verbose, 6)
                    if conditionMatch == 0:
                        conditionPosition = i
                    conditionMatch += 1
                    if conditionMatch == len(conditions):
                        dprint("\t\t\trule match.", verbose, 6)
                        if rule in matches:
                            matches[rule] += [(conditionPosition, conditionPosition + conditionMatch)]
                        else:
                            matches.update({rule:[(conditionPosition, conditionPosition + conditionMatch)]})
                        conditionMatch = 0
                else:
                    conditionMatch = 0
            dprint("", verbose, 5)
    return matches

def generateNewPerspectives(perspective, verbose):
    new_perspectives = []
    matches = matchRules(perspective, verbose)
    dprint("Inputs to Matches:\n {} -> {}".format(perspective, matches), verbose, 2)

    dprint("Rule matches: ", verbose, 3)
    for matchRule, matchIdxTuples in matches.items():
        for match in matchIdxTuples:
            dprint("{} <- {}".format(matchRule, match), verbose, 3)
            
            subset = perspective[match[0]:match[1]]
            left, right = perspective[:match[0]], perspective[match[1]:]
            dprint("{}, {}, {}".format(left, subset, right), verbose, 4)
            new_perspective = left + [{'pos' : matchRule, 'words' : subset}] + right

            if new_perspective not in new_perspectives:
                new_perspectives.append(new_perspective)
                
    return new_perspectives

#This is the big boy itself
#The rule above define what the builder will try
#As of right now, the builder has a few problems
#It refuses to accept verb complements
#It does not account for null items
#As a result it doesn't yet generate movement
#
#Verboseness is for debugging purposes, it works in levels
#0 - Print nothing, smooth, user experience
#1 - Prints things like how many trees are being considered in any one permutation of rules
#2 - ...
#3 - ...
#... - ...
#-1 - PRINTS. EVERYTHING. Be careful what you wish for!!!
def BuildSyntaxTree(perspectives, maxNode = "cP", verbose = 0):
    #Keep track of where matches for each rule occurs, when creating a new node,
    #select the simplest matches first (adjbar before tbar), and the match that occurs later in the tree
    
    #This is temporary for now -- in the future we will have multiple perspectives, not just one!
    #perspectives = [x]
    new_perspectives, final_perspectives = [], []
    exhaustive_perspectives = perspectives.copy()
    
    #Measures tree formation
    while True:
        new_perspectives = []
        for perspective in perspectives:
            new_perspectives += generateNewPerspectives(perspective, verbose)
        dprint("new perspectives: {}".format(new_perspectives), verbose, 4)
        
        dprint("Filling in Exaustive and Final arrays...", verbose, 2)
        next_perspectives = []
        for perspective in new_perspectives:
            if perspective not in exhaustive_perspectives:
                dprint("{} -> exhaustive_perspectives, generically missing".format(perspective), verbose, 3)
                exhaustive_perspectives.append(perspective)
                next_perspectives.append(perspective)
            if inTreeTop(perspective, maxNode, strict = True) == (True, True) and perspective not in final_perspectives:
                dprint("{} -> final_perspectives, completed tree".format(perspective), verbose, 3)
                final_perspectives.append(perspective)
        
        #Stops searching
        if perspectives == next_perspectives or len(next_perspectives) == 0:
            dprint("Halting, onboarding last trees", verbose, 2)
            for perspective in next_perspectives:
                if perspective not in final_perspectives:
                    dprint("{} -> final_perspectives".format(perspective), verbose, 3)
                    final_perspectives.append(perspectives)
            dprint("Halted", verbose, 0)
            break
        perspectives = next_perspectives.copy()
        dprint("New perspectives: {}\tTotal: {}".format(len(perspectives), len(exhaustive_perspectives)), verbose, 1)
    #Returns a tuple of:
    #Final list of highest level trees
    #All generated trees
    #Changes, corresponding to exhaustive indicies
    return (final_perspectives, exhaustive_perspectives)

#Gives the height of a tree, for those from perspective
def treeHeight(tree):
    if type(tree) == str:
        return 0
    if len(tree) == 0:
        return 0
    if len(tree) == 1:
        if type(tree[0]) == str:
            return 0
    return 1+max([treeHeight(_['words']) for _ in tree])

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