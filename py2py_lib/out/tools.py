
def indent(stmts, level):
  ind = " "*level if level else "\t"
  return [ind + stmt for stmt in stmts]


