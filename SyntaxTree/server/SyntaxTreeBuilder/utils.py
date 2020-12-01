import ast

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

#Debugging handling, small but out of the tree builder to keep things clean
def dprint(statement, currentLevel, evalLevel, **kwargs):
    if currentLevel >= evalLevel or currentLevel == -1:
        print(statement, **kwargs)

