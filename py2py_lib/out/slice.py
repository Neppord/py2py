from visitor import Visitor
class SliceOut(Visitor):

  @classmethod
  def visit_Ellipsis (self, ast, *a, **k):
    return "..."

  @classmethod
  def visit_Slice (self, ast, *a, **k):
    from expr import ExpresionOut
    if ast.lower and ast.upper and ast.step:
      return "%s:%s:%s" % (ExpresionOut.visit(ast.lower), ExpresionOut.visit(ast.upper), ExpresionOut.visit(ast.step))
    elif ast.lower and ast.upper:
      return "%s:%s" % (ExpresionOut.visit(ast.lower), ExpresionOut.visit(ast.upper))
    elif ast.lower and ast.step:
      return "%s::%s" % (ExpresionOut.visit(ast.lower), ExpresionOut.visit(ast.step))
    elif ast.upper and ast.step:
      return ":%s:%s" % (ExpresionOut.visit(ast.upper), ExpresionOut.visit(ast.step))
    elif ast.lower:
      return "%s:" % ExpresionOut.visit(ast.lower)
    elif ast.upper:
      return ":%s" % ExpresionOut.visit(ast.upper)
    elif ast.step:
      return "::%s" % ExpresionOut.visit(ast.step)
    else:
      return ":" 

  @classmethod
  def visit_ExtSlice (self, ast, *a, **k):
    return ", ".join(self.visit(slice) for slice in ast.dims)

  @classmethod
  def visit_Index (self, ast, *a, **k):
    from expr import ExpresionOut
    return ExpresionOut.visit(ast.value)


