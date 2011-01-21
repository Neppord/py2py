from itertools import chain, islice
def indent(stmts, level):
  ind = " "*level if level else "\t"
  return [ind + stmt for stmt in stmts]

class Singelton(object):
  def __new__(cls,*a,**kwarg):
    return cls

class VisitorError(Exception):
  pass
  
class Visitor(Singelton):

  @classmethod
  def visit(self,node, *a):
    """Finds and calls the appropiate function visit_<NodeName>"""
    try:
      visitor = getattr(self, 'visit_' + node.__class__.__name__)
    except AttributeError:
      raise VisitorError("(%s):Visitor not found(%s)" % (self.__name__,node.__class__.__name__))

    return visitor(node,*a)

  __call__ = visit
    
class StatementOut(Visitor):

  level = 2

  @classmethod
  def handle_body(self, body, *a, **k):
    body = (self.visit(stmt, *a, **k) for stmt in body)
    body = chain.from_iterable(body)
    body = indent(body, self.level)
    return body

  @classmethod
  def visit_FunctionDef(self, ast, *a, **k):
    decorators = ["@%s" % self.visit(dec, *a, **k) for dec in ast.decorator_list]
    head = ["def %s (%s):" % (ast.name, self.visit(ast.args))]
    body = self.handle_body(ast.body, *a, **k)
    return decorators + head + body

  @classmethod
  def visit_arguments(self, ast, *a, **k):
    args = [ExpresionOut.visit(arg, *a, **k) for arg in ast.args]
    defaults = (ExpresionOut.visit(default, *a, **k) for default in ast.defaults)
    defaults = ("%s=%s"% t for t in zip(args[-len(ast.defaults):],defaults))
    args = args[:-len(ast.defaults)] 
    vararg =  ("*%s" % ast.vararg,) if ast.vararg else ()
    kwarg = ("**%s" % ast.kwarg,) if ast.kwarg else ()
    return ", ".join(chain(args, defaults, vararg, kwarg))

  @classmethod
  def visit_ClassDef (self, ast, *a, **k):
    decorators = ["@%s" % self.visit(dec, *a, **k) for dec in ast.decorator_list]
    if ast.bases:
      head = ["class %s (%s):" % (ast.name, self.visit(ast.bases))]
    else:
      head = ["class %s:" % (ast.name)]
    body = self.handle_body(ast.body, *a, **k)
    return decorators + head + body

  @classmethod
  def visit_Return (self, ast, *a, **k):
    if ast.value:
      return ["return %s" % ExpresionOut.visit(ast.value, *a, **k)]
    else:
      return ["return"]
  
  @classmethod
  def visit_Delete (self, ast, *a, **k):
    return ["del %s" % ", ".join(ExpresionOut.visit(target, *a, **k) for target in ast.targets)]

  @classmethod
  def visit_Assign (self, ast, *a, **k):
    targets = ", ".join(ExpresionOut.visit(target, *a, **k) for target in ast.targets)
    value = ExpresionOut.visit(ast.value, *a, **k)
    return ["%s = %s" %(targets, value)]

  @classmethod
  def visit_AugAssign (self, ast, *a, **k):
    target = ExpresionOut.visit(ast.target, *a, **k)
    op = OperatorOut.visit(ast.op, *a, **k)
    value = ExpresionOut.visit(ast.value, *a, **k)
    return ["%s %s= %s" % (target, op, value)]
  
  @classmethod
  def visit_Print (self, ast, *a, **k):
    values = (ExpresionOut.visit(value, *a, **k) for value in ast.values)
    dest = (ExpresionOut.visit(ast.dest, *a, **k), ) if ast.dest else ()
    stmt = "print >> %s" if dest else "print %s"
    stmt %= ", ".join(chain(dest, values))
    if ast.nl:
      return [stmt]
    else:
      return [stmt+","]

  @classmethod
  def visit_For (self, ast, *a, **k):
    target = ExpresionOut.visit(ast.target, *a, **k)
    iter = ExpresionOut.visit(ast.iter, *a ,**k)
    head = "for %s in %s:"
    head %= (target, iter)
    head = [head]
    body = self.handle_body(ast.body, *a, **k)
    if not ast.orelse:
      return head + body
    else:
      orelse = self.handle_body(ast.orelse, *a, **k)
      return head + body + ["else:"] + orelse

  @classmethod
  def visit_While(self, ast, *a, **k):
    test = ExpresionOut.visit(ast.test, *a, **k)
    head = "while %s:"
    head %= test
    head = [head]
    body = self.handle_body(ast.body, *a, **k)
    if not ast.orelse:
      return head + body
    else:
      orelse = self.handle_body(ast.orelse, *a, **k)
      return head + body + ["else:"] + orelse

  @classmethod
  def visit_If(self, ast, *a, **k):
    test = ExpresionOut.visit(ast.test, *a, **k)
    head = "if %s:"
    head %= test
    head = [head]
    body = self.handle_body(ast.body, *a, **k)
    if not ast.orelse:
      return head + body
    else:
      orelse = self.handle_body(ast.orelse, *a, **k)
      return head + body + ["else:"] + orelse

  @classmethod
  def visit_With(self, ast, *a, **k):
    context_expr = ExpresionOut.visit(ast.context_expr, *a, **k)
    if ast.optional_vars:
      optional_vars = ExpresionOut.visit(ast.context_expr, *a, **k)
      head = "with %s as %s:"
      head %= (context_expr, optional_vars)
    else:
      head = "with %s:"
      head %= context_expr
    head = [head]
    body = self.handle_body(ast.body)
    return head + body

  @classmethod
  def visit_Raise(self, ast, *a, **k):
    type = (ExpresionOut.visit(ast.type, *a, **k),) if ast.type else ()
    inst = (ExpresionOut.visit(ast.inst, *a, **k),) if ast.inst else ()
    tback = (ExpresionOut.visit(ast.tback, *a, **k),) if ast.tback else ()
    head = "raise %s"
    head %= ", ".join(chain(type, inst, tback))
    head = [head]
    return head

  @classmethod
  def visit_TryExcept(self, ast, *a, **k):
    head = ["try:"]
    body = self.handle_body(ast.body, *a, **k)
    handlers = (ExcepthandlerOut.visit(handler, *a, **k) for handler in ast.handlers)
    handlers = list(chain.from_iterable(handlers))
    orelse = self.handle_body(ast.orelse, *a, **k)
    if not ast.orelse:
      return head + body + handlers
    return head + body + handlers + ["else:"] + orelse

  @classmethod
  def visit_Tryfinally(self, ast, *a, **k):
    body = self.handle_body(ast.body, *a, **k)
    finalbody = self.handle_body(ast.finalbody, *a, **k)
    return ["try:"] + body + ["finaly:"] + finalbody

  @classmethod
  def visit_Assert(self, ast, *a, **k):
    test = (ExpresionOut.visit(ast.test, *a, **k),)
    msg = (ExpresionOut.visit(ast.msg, *a, **k),) if ast.msg else ()
    head = "assert %s"
    head %= ", ".join(chain(test, msg))
    head = [head]
    return head

  @classmethod
  def visit_Import(self, ast, *a, **k):
    names = join(AliasOut.visit(alias, *a, **k) for alias in ast.names)
    return ["import %s" % names]

  @classmethod
  def visit_ImportFrom(self, ast, *a, **k):
    # what dose ast.level do?
    module = ast.module
    names = ", ".join(AliasOut.visit(alias, *a, **k) for alias in ast.names)
    return ["from %s import %s" % (module, names)]
    

  @classmethod
  def visit_Exec(self, ast, *a, **k):
    if ast.globals:
      body = ExpresionOut.visit(ast.body, *a, **k)
      locals = ExpresionOut.visit(ast.locals, *a, **k)
      globals = ExpresionOut.visit(ast.globals, *a, **k)
      head = "exec %s in %s, %s" 
      head %= (body, globals, locals)
      head = [head]
    elif ast.locals:
      body = ExpresionOut.visit(ast.body, *a, **k)
      locals = ExpresionOut.visit(ast.locals, *a, **k)
      head = "exec %s in %s"
      head %= (body, locals)
      head = [head]
    else:
      body = ExpresionOut.visit(ast.body, *a, **k)
      head = "exec %s"
      head %= body
      head = [head]
    return head

  @classmethod
  def visit_Global(self, ast, *a, **k):
    return ["global %s" % ", ".join(ast.names)]

  @classmethod
  def visit_Expr(self, ast, *a, **k):
    return [ExpresionOut.visit(ast.value, *a, **k)]

  @classmethod
  def visit_Pass (self, ast, *a, **k):
    return ["pass"]

  @classmethod
  def visit_Break(self, ast, *a, **k):
    return ["break"]

  @classmethod
  def visit_Continue(self, ast, *a, **k):
    return ["continue"]

class AliasOut(Visitor):
  @classmethod
  def visit_alias(self, ast, *a, **k):
    return "%s as %s"%(ast.name, ast.asname) if ast.asname else ast.name


class ExcepthandlerOut(Visitor):
  @classmethod
  def visit_ExceptHandler(self, ast, *a, **k):
    type = (ExpresionOut.visit(ast.type, *a, **k),) if ast.type else ()
    name = (ExpresionOut.visit(ast.name, *a, **k),) if ast.name else ()
    head = "except %s:"
    head %= ", ".join(chain(type, name))
    head = [head]
    body = StatementOut.handle_body(ast.body, *a, **k)
    return head + body



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

class SliceOut(Visitor):

  @classmethod
  def visit_Ellipsis (self, ast, *a, **k):
    return "..."

  @classmethod
  def visit_Slice (self, ast, *a, **k):
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
    return ExpresionOut.visit(ast.value)

class OperatorOut(Visitor):
  @classmethod
  def visit_Add (self, ast, *a, **k):
    return "+"

  @classmethod
  def visit_Sub (self, ast, *a, **k):
    return "-"

  @classmethod
  def visit_Mult (self, ast, *a, **k):
    return "*"

  @classmethod
  def visit_Div (self, ast, *a, **k):
    return "/"

  @classmethod
  def visit_Mod (self, ast, *a, **k):
    return "%"

  @classmethod
  def visit_Pow (self, ast, *a, **k):
    return "**"

  @classmethod
  def visit_LShift (self, ast, *a, **k):
    return "<<"

  @classmethod
  def visit_RShift (self, ast, *a, **k):
    return ">>"

  @classmethod
  def visit_BitOr (self, ast, *a, **k):
    return "|"

  @classmethod
  def visit_BitXor (self, ast, *a, **k):
    return "^"

  @classmethod
  def visit_BitAnd (self, ast, *a, **k):
    return "&"

  @classmethod
  def visit_ (self, ast, *a, **k):
    return "//"

  @classmethod
  def visit_Invert (self, ast, *a, **k):
    return "~"

  @classmethod
  def visit_Not (self, ast, *a, **k):
    return "not"

  @classmethod
  def visit_UAdd (self, ast, *a, **k):
    return "+"

  @classmethod
  def visit_USub (self, ast, *a, **k):
    return "-"

  @classmethod
  def visit_Eq (self, ast, *a, **k):
    return "=="

  @classmethod
  def visit_NotEq (self, ast, *a, **k):
    return "!="

  @classmethod
  def visit_Lt (self, ast, *a, **k):
    return "<"

  @classmethod
  def visit_LtE (self, ast, *a, **k):
    return "<="

  @classmethod
  def visit_Gt (self, ast, *a, **k):
    return ">"

  @classmethod
  def visit_GtE (self, ast, *a, **k):
    return  ">="

  @classmethod
  def visit_Is (self, ast, *a, **k):
    return "is"

  @classmethod
  def visit_IsNot (self, ast, *a, **k):
    return "is not"

  @classmethod
  def visit_In (self, ast, *a, **k):
    return "in"

  @classmethod
  def visit_NotIn (self, ast, *a, **k):
    return "not in"

class Out(Visitor):

  @classmethod
  def visit_Module(self, ast, *a, **k):
    return "\n".join(chain.from_iterable((StatementOut.visit(node, *a, **k) for node in ast.body)))
if __name__ == "__main__":
  from ast import parse
  code = "global a"
  print Out.visit(parse(code))
