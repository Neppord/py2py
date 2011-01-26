
from visitor import Visitor

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


