#Imports
import re, math, hashlib #, nltk

import cProfile, timeit
#from .utils import dprint
from .utils import saveDict, loadDict

class TreeBuilder:
    wordManager = None

    def __init__(self, wordManager):
        self.wordManager = wordManager
        
    
    #This will build all of the possible base cases for perspective
    #based on research forensics for each given word
    def __constructPerspective(self, tokens, parts_of_speach):
        return [{
            'pos' : parts_of_speach[i], 
            'words' : [tokens[i]]
        } for i in range(len(tokens))]

    def __constructPerspectivePermutations(self, pool, perspectives = []):
        #End case - No more perspectives to create
        if len(pool) == 0:
            return perspectives
        
        #Base case - Create base of perspectives
        if len(perspectives) == 0:
            return self.__constructPerspectivePermutations(pool[1:], [[_] for _ in pool[0]])
        
        front_pos, new_perspectives = pool[0], []
        for pool_item in front_pos:
            for perspective in perspectives:
                new_perspective = perspective + [pool_item]
                new_perspectives.append(new_perspective)
        
        return self.__constructPerspectivePermutations(pool[1:], new_perspectives)

    def __constructBasePerspectives(self, sentence):
        perspectives = []
        tokens = sentence.strip().split(" ")
        parts_of_speach = [self.wordManager.getLikelyClass(_) for _ in tokens]
        permutations = self.__constructPerspectivePermutations(parts_of_speach)
        return [self.__constructPerspective(tokens, _) for _ in permutations]
    
    #Gives the height of a tree, for those from perspective
    def __treeHeight(self, tree):
        #if type(tree) == str:
        #    return 0
        #l = len(tree)
        #if l == 0:
        #    return 0
        #if l == 1:
        #    if type(tree[0]) == str:
        #        return 0
        if len(tree) < 2:
            return 0
        return 1+max([self.__treeHeight(_['words']) for _ in tree])

    def __treeHash(self, tree):
        h = hashlib.sha384()
        if len(tree) < 2:
            return h.digest()
        [h.update(bytearray(_['pos'], 'utf-8')) for _ in tree]
        return h.digest()

    def __matchRules(self, perspective = [], verbose = 0):
        matches = {}
        for rule, conditionSet in self.wordManager.rules.items():  
            #dprint("rule {}".format(rule), verbose, 5)
            for conditions in conditionSet:
                conditionMatch, conditionPosition = 0, 0
                #dprint("\tcond {}".format(str(conditions)), verbose, 5, end='')
                #dprint(": ", verbose, 6, end='\n')
                for i in range(len(perspective)):
                    node = perspective[i]
                    if node['pos'] == conditions[conditionMatch]:
                        #dprint("\t\t{} <- {}({})".format(rule, node['pos'], node['words']), verbose, 6)
                        if conditionMatch == 0:
                            conditionPosition = i
                        conditionMatch += 1
                        if conditionMatch == len(conditions):
                            #dprint("\t\t\trule match.", verbose, 6)
                            if rule in matches:
                                matches[rule] += [(conditionPosition, conditionPosition + conditionMatch)]
                            else:
                                matches.update({rule:[(conditionPosition, conditionPosition + conditionMatch)]})
                            conditionMatch = 0
                    else:
                        conditionMatch = 0
                #dprint("", verbose, 5)
        return matches

    def __generateNewPerspectives(self, perspective, verbose):
        new_perspectives = []
        matches = self.__matchRules(perspective, verbose)
        #dprint("Inputs to Matches:\n {} -> {}".format(perspective, matches), verbose, 2)

        #dprint("Rule matches: ", verbose, 3)
        for matchRule, matchIdxTuples in matches.items():
            for match in matchIdxTuples:
                #dprint("{} <- {}".format(matchRule, match), verbose, 3)
                
                subset = perspective[match[0]:match[1]]
                left, right = perspective[:match[0]], perspective[match[1]:]
                #dprint("{}, {}, {}".format(left, subset, right), verbose, 4)
                new_perspective = left + [{'pos' : matchRule, 'words' : subset}] + right

                if new_perspective not in new_perspectives:
                    new_perspectives.append(new_perspective)
                    
        return new_perspectives

    #The rule above define what the builder will try
    #As of right now, the builder has a few problems
    #It does not accept verb complements
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
    def BuildSyntaxTree(self, sentence, maxNode = "cP", verbose = 0):
        #prepare_profile, generate_profile, scan_profile, transfer_profile = cProfile.Profile(), cProfile.Profile(), cProfile.Profile(), cProfile.Profile()
        section_timer = timeit.Timer()
        cumulative_time = 0
        #Keep track of where matches for each rule occurs, when creating a new node,
        #select the simplest matches first (adjbar before tbar), and the match that occurs later in the tree
        
        #prepare_profile.enable()
        perspectives = self.__constructBasePerspectives(sentence)
        final_perspectives = []
        
        #exhaustive list is partitioned by perspective (Tree) height to alliviate time spent on lookups
        exhaustive_perspectives = {}
        for perspective in perspectives:
            pHash = self.__treeHash(perspective)
            plen = len(perspective)
            pos = perspective[0]['pos']
            npos = perspective[-1]['pos']

            if pHash not in exhaustive_perspectives:
                exhaustive_perspectives[pHash] = {}

            if plen not in exhaustive_perspectives[pHash]:
                exhaustive_perspectives[pHash][plen] = {}

            if pos not in exhaustive_perspectives[pHash][plen]:
                exhaustive_perspectives[pHash][plen][pos] = {}

            if npos not in exhaustive_perspectives[pHash][plen][pos]:
                exhaustive_perspectives[pHash][plen][pos][npos] = []

            if perspective not in exhaustive_perspectives[pHash][plen][pos][npos]:
                exhaustive_perspectives[pHash][plen][pos][npos].append(perspective)
        #prepare_profile.disable()
        #prepare_profile.print_stats()

        while True:
            all_new_perspectives, next_perspectives = [], []
            for perspective in perspectives:
                new_perspectives = self.__generateNewPerspectives(perspective, verbose)
                all_new_perspectives.extend(new_perspectives)

            #TODO - THIS is the heaviest part of the tree generation
            start = section_timer.timer()
            for perspective in all_new_perspectives:
                pHash = self.__treeHash(perspective)
                plen = len(perspective)
                pos = perspective[0]['pos']
                pos = perspective[-1]['pos']
                
                if pHash not in exhaustive_perspectives:
                    exhaustive_perspectives[pHash] = {}

                if plen not in exhaustive_perspectives[pHash]:
                    exhaustive_perspectives[pHash][plen] = {}

                if pos not in exhaustive_perspectives[pHash][plen]:
                    exhaustive_perspectives[pHash][plen][pos] = {}
                
                if npos not in exhaustive_perspectives[pHash][plen][pos]:
                    exhaustive_perspectives[pHash][plen][pos][npos] = []

                if perspective not in exhaustive_perspectives[pHash][plen][pos][npos]: #<-- This is the bottleneck
                    exhaustive_perspectives[pHash][plen][pos][npos].append(perspective)
            
                    if perspective not in final_perspectives:
                        if self.__inTreeTop(perspective, maxNode, strict = True) == True:
                            final_perspectives.append(perspective)
                        else:
                            next_perspectives.append(perspective)
            delta_time = section_timer.timer() - start
            cumulative_time += delta_time
            print("{} -> {} : {} sum {}".format(len(all_new_perspectives), len(next_perspectives), delta_time, cumulative_time))
            
            #Stops searching
            if len(next_perspectives) == 0 or perspectives == next_perspectives:
                break
            perspectives = next_perspectives.copy()

        
        #Returns a tuple of:
        #Final list of highest level trees
        #All generated trees
        #Changes, corresponding to exhaustive indicies
        
        #print('generative profile')
        #generate_profile.print_stats()
        
        #print('scan profile')
        #scan_profile.print_stats()
        
        print("Total: {}".format(cumulative_time))
        return final_perspectives

    #determines if the given rule is at the top of a given tree
    #Strict disallows the tree from having different neighbors at the top
    # def __inTreeTop(self, tree, rule, strict = False):
    #     retVal = False
    #     strictVal = True
    #     for topNode in tree:
    #         if topNode['pos'] == rule:
    #             retVal = True
    #         else:
    #             strictVal = False
    #     if strict:
    #         return (retVal, strictVal)
    #     return retVal

    def __inTreeTop(self, tree, rule, strict = False):
        if strict and len(tree) != 1:
            return False
        for topNode in tree:
            if topNode['pos'] == rule:
                return True
        return False

    def pruneTrees(self, trees):
        pruned = []
        for tree in trees:
            print(len(tree))
            finishedVal = self.__inTreeTop(tree, "cP", strict = True)
            if finishedVal: #[0] and finishedVal[1]:
                pruned.append(tree)
        return pruned