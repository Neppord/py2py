from itertools import chain

from tools import indent
from visitor import Visitor

from expr import ExpresionOut
from alias import AliasOut

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


