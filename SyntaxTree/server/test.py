import SyntaxTreeBuilder
import cProfile

w = SyntaxTreeBuilder.WordManager()
t = SyntaxTreeBuilder.TreeBuilder(w)

profile = cProfile.Profile()
profile.enable()
tree = t.BuildSyntaxTree('The dog is really really really really tall')
profile.disable()
profile.print_stats()

w.saveWordClasses()
print(tree[0])
