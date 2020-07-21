import os, json
from uuid import uuid1
from flask import Flask, request, send_from_directory, send_file, render_template, flash
from SyntaxTreeBuilder import *

app = Flask(__name__)

app.config["TREE_IMGS"] = "./trees/img"
app.secret_key = uuid1().bytes #b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/p')
def process():
    global localBank

    if 'q' not in request.args:
        return "No sentence in args!", 400
    
    sentence = request.args['q'].replace('+', ' ')
    
    finalTree = find_json_file(sentence)
    if not finalTree:
        print("constructing perspectives")
        try:
            p, localBank = constructBasePerspectives(sentence, localBank)
        except Exception as e:
            return "Failed to collect word definitions: {}".format(str(e)), 500

        print("building syntax tree")
        try:
            treeData = BuildSyntaxTree(p, verbose = 1)
        except Exception as e:
            return "Failed to build Syntax tree: {}".format(str(e)), 500

        print("pruning syntax tree")
        try:
            finalTrees = pruneTrees(treeData[0])
            finalTree = finalTrees[0]
            save_json_file(sentence, finalTree)
        except Exception as e:
            return "Failed to prune Syntax trees, this means no full trees were created: {}".format(str(e)), 500
        
    print("building tree representation")
    try:
        saveDict(localBank, 'local_bank.json')
        
        if request.args['returnType'] == 'latex':
            return "<pre>{}</pre>".format(latexTree(finalTree))
        
        if request.args['returnType'] == 'json':
            return json.dumps(finalTree)
        
        if request.args['returnType'] == 'text':
            anyTreeRoot = anyTree(finalTree)
            return "<pre>{}</pre>".format(textAnyTree(anyTreeRoot))
        
        if request.args['returnType'] == 'img':
            if not os.path.isfile("./trees/img/{}.png".format(sentence)):
                anyTreeRoot = anyTree(finalTree)
                graphAnyTree(anyTreeRoot, "./trees/img/{}".format(sentence))
            return send_from_directory(app.config["TREE_IMGS"], filename="{}.png".format(sentence))
        
    except Exception as e:
        return "Failed to build tree representation: {}".format(str(e)), 500

    return "Bad returnType", 500
    
def save_json_file(sentence, tree):
    filepath = "./trees/json/{}.json"
    with open(filepath.format(sentence), 'w') as f:
        f.write(json.dumps(tree))
    
def find_json_file(sentence):
    filepath = "./trees/json/{}.json"
    if not os.path.isfile(filepath.format(sentence)):
        return None
    tree = {}
    with open(filepath.format(sentence), 'r') as f:
        tree = json.loads(f.read())
    return tree
    
if __name__ == '__main__':
    localBank = loadDict('../local_bank.json')
    app.run('0.0.0.0', port=3000, debug = True)