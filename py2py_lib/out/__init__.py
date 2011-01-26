from itertools import chain, islice
from visitor import Visitor
from expr import ExpresionOut
from stmt import StatementOut
from op import OperatorOut
from slice import SliceOut

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

class Out(Visitor):

  @classmethod
  def visit_Module(self, ast, *a, **k):
    return "\n".join(chain.from_iterable((StatementOut.visit(node, *a, **k) for node in ast.body)))
if __name__ == "__main__":
  from ast import parse
  code = "global a"
  print Out.visit(parse(code))
