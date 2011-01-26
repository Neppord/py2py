

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
    

