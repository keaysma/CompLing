import SyntaxTreeBuilder
import cProfile

w = SyntaxTreeBuilder.WordManager()
t = SyntaxTreeBuilder.TreeBuilder(w)

profile = cProfile.Profile()
profile.enable()
tree = t.BuildSyntaxTree('The man and the table and the egg run to the dog and the lamp')
profile.disable()
profile.print_stats()

w.saveWordClasses()
print(tree[0])
