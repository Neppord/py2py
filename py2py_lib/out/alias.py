from visitor import Visitor
class AliasOut(Visitor):
  @classmethod
  def visit_alias(self, ast, *a, **k):
    return "%s as %s"%(ast.name, ast.asname) if ast.asname else ast.name


