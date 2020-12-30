import os, json
from uuid import uuid1
from flask import Flask, request, send_from_directory, send_file, render_template, flash, redirect, url_for
import SyntaxTreeBuilder

def create_app(path = '.'):
    w = SyntaxTreeBuilder.WordManager()
    t = SyntaxTreeBuilder.TreeBuilder(w)

    app = Flask(__name__)

    app.config["TREE_IMGS"] = os.path.join(path, "trees/img")
    app.secret_key = uuid1().bytes

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/save')
    def save_all():
        w.saveWordClasses()
        return redirect(url_for('index'))

    @app.route('/api/p')
    def process():
        #global localBank

        if 'q' not in request.args:
            return "No sentence in args!", 400
        
        sentence = request.args['q'].replace('+', ' ')
        
        finalTree = find_json_file(sentence)
        if not finalTree:
            print("building syntax tree")
            try:
                treeData = t.BuildSyntaxTree(sentence, verbose = 1)
            except Exception as e:
                return "Failed to build Syntax tree: {}".format(str(e)), 500

            print("pruning syntax tree")
            finalTrees = t.pruneTrees(treeData)
            finalTree = finalTrees[0]
            try:
                save_json_file(sentence, finalTree)
            except Exception as e:
                return "Failed to prune Syntax trees, this means no full trees were created: {}".format(str(e)), 500
            
        print("building tree representation")
        try:
            #SyntaxTreeBuilder.utils.saveDict(localBank, 'local_bank.json')
            
            if request.args['returnType'] == 'latex':
                return "<pre>{}</pre>".format(SyntaxTreeBuilder.export.latexTree(finalTree))
            
            if request.args['returnType'] == 'json':
                return json.dumps(finalTree)
            
            if request.args['returnType'] == 'text':
                anyTreeRoot = SyntaxTreeBuilder.export.anyTree(finalTree)
                return "<pre>{}</pre>".format(SyntaxTreeBuilder.export.textAnyTree(anyTreeRoot))
            
            if request.args['returnType'] == 'img':
                if not os.path.isfile(os.path.join(path, "trees/img/{}.png".format(sentence))):
                    print('building tree')
                    anyTreeRoot = SyntaxTreeBuilder.export.anyTree(finalTree)
                    print('graphing tree')
                    SyntaxTreeBuilder.export.graphAnyTree(anyTreeRoot, os.path.join(path, "trees/img/{}".format(sentence)))
                return send_from_directory(app.config["TREE_IMGS"], filename="{}.png".format(sentence))
            
        except Exception as e:
            return "Failed to build tree representation: {}".format(str(e)), 500

        return "Bad returnType", 500
        
    def save_json_file(sentence, tree):
        filepath = os.path.join(path, "trees/json/{}.json")
        with open(filepath.format(sentence), 'w') as f:
            f.write(json.dumps(tree))
        
    def find_json_file(sentence):
        filepath = os.path.join(path, "trees/json/{}.json")
        if not os.path.isfile(filepath.format(sentence)):
            return None
        tree = {}
        with open(filepath.format(sentence), 'r') as f:
            tree = json.loads(f.read())
        return tree
    
    return app
    
if __name__ == '__main__':
    app = create_app('./server')
    #localBank = SyntaxTreeBuilder.utils.loadDict('../local_bank.json')
    app.run('0.0.0.0', port=3000, debug = True)