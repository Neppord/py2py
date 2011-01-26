from itertools import chain
from op import OperatorOut
from visitor import Visitor
from slice import SliceOut

class ExpresionOut(Visitor):

  @classmethod
  def visit_BoolOp (self, ast, *a, **k):
    op = OperatorOut.visit(ast.op, *a, **k)
    return op.join(self.visit(expr, *a, **k) for expr in ast.values)

  @classmethod
  def visit_BinOp (self, ast, *a, **k):
    left = self.visit(ast.left, *a, **k)
    op = OperatorOut.visit(ast.op, *a, **k)
    right = self.visit(ast.right, *a, **k)
    return left + " " + op + " " + right

  @classmethod
  def visit_UnaryOp (self, ast, *a, **k):
    operand = self.visit(ast.operand, *a, **k)
    op = OperatorOut.visit(ast.op, *a, **k)
    return op + operand

  @classmethod
  def visit_Lambda (self, ast, *a, **k):
    arguments = self.visit(ast.arguments, *a, **k)
    expr = self.visit(ast.expr, *a, **k)
    return "lambda %s:%s" % (arguments, expr)

  @classmethod
  def visit_IfExp (self, ast, *a, **k):
    test = self.visit(ast.test, *a, **k)
    body = self.visit(ast.body, *a, **k)
    orelse = self.visit(ast.body, *a, **k)
    return "%s if %s else %s" % (body, test, orelse)

  @classmethod
  def visit_Dict (self, ast, *a, **k):
    keys = (self.visit(key, *a, **k) for key in ast.keys)
    values = (self.visit(value, *a, **k) for value in ast.values)
    return "{%s}" % (",".join("%s:%s" % t for t in zip(keys, values) ))

  @classmethod
  def visit_ListComp (self, ast, *a, **k):
    elt = self.visit(ast.elt, *a, **k)
    generators (self.visit(gen, *a, **k) for gen in  ast.generators)
    return "[%s %s]" % (elt, " ".join(generators))
    
  @classmethod
  def visit_GeneratorExp (self, ast, *a, **k):
    elt = self.visit(ast.elt, *a, **k)
    generators = (self.visit(gen, *a, **k) for gen in  ast.generators)
    return "(%s %s)" % (elt, " ".join(generators))

  @classmethod
  def visit_comprehension (self, ast, *a, **k):
    target = self.visit(ast.target, *a, **k)
    iter = self.visit(ast.iter, *a, **k)
    ifs = ("if  " + self.visit(if_, *a, **k) for if_ in ast.ifs)
    return "for %s in %s %s" % (target, iter, " ".join(ifs))

  @classmethod
  def visit_Yield (self, ast, *a, **k):
    if ast.expr:
      expr = self.visit(ast.expr, *a, **k)
      return "yield %s" % (expr)
    else:
      return "yield"

  @classmethod
  def visit_Compare (self, ast, *a, **k):
    left = self.visit(ast.left, *a, **k)
    ops = (OperatorOut.visit(op, *a, **k) for op in ast.ops)
    comparators = (self.visit(comparator, *a, **k) for comparator in ast.comparators)
    return "%s %s" %(left, " ".join("%s %s" % t for t in zip(ops, comparators)))

  @classmethod
  def visit_Call (self, ast, *a, **k):
    func = self.visit(ast.func, *a, **k)
    args = (self.visit(arg, *a, **k) for arg in ast.args)
    keywords = (self.visit(keyword, *a, **k) for keyword in ast.keywords)
    starargs = self.visit(ast.starargs, *a, **k) if ast.starargs else None
    kwargs = self.visit(ast.kwargs, *a, **k) if ast.kwargs else None
    params = ", ".join(chain(args, keywords))
    if starargs:
      if params:
        params += ", *%s" % starargs
      else:
        params += "*%s" % starargs
    if kwargs:
      if params:
        params += ", **%s" % kwargs
      else:
        params += "**%s" %kwargs
    return "%s(%s)" % (func, params)

  @classmethod
  def visit_keyword(self, ast, *a, **k):
    return "%s=%s" % (ast.arg, self.visit(ast.value))


  @classmethod
  def visit_Repr(self, ast, *a, **k):
    value = self.visit(ast.value, *a, **k)
    return "`%s`" % value

  @classmethod
  def visit_Num(self, ast, *a, **k):
    return `ast.n`

  @classmethod
  def visit_Str (self, ast, *a, **k):
    return `ast.s`
    
  @classmethod
  def visit_Attribute (self, ast, *a, **k):
    value = self.visit(ast.value, *a, **k)
    attr = ast.attr
    return "%s.%s" % (value, attr)

  @classmethod
  def visit_Subscript (self, ast, *a, **k):
    value = self.visit(ast.value, *a, **k)
    slice = SliceOut.visit(ast.slice, *a, **k)
    return "%s[%s]" % (value, slice)

  @classmethod
  def visit_Name (self, ast, *a, **k):
    return ast.id

  @classmethod
  def visit_List (self, ast, *a, **k):
    return "[%s]" % ", ".join(self.visit(elt, *a, **k) for elt in ast.elts)

  @classmethod
  def visit_Tuple (self, ast, *a, **k):
    return "(%s)" % ", ".join(self.visit(elt, *a, **k) for elt in ast.elts)


