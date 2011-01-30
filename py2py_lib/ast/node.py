class ParserBuilderError(Exception):
  pass

class Node(object):
	def __add__(self, other):
		return Add(self, other)

	def __radd__(self, other):
		return Add(other, self)

	def __or__(self, other):
		return Or(self, other)

	def __ror__(self, other):
		return Or(other, self)

	def __getitem__(self, slice):
		return Slice(self, slice)

	def parse(self, string):
		for c in string:
			ret = self.feed(c)
			if ret != None:
				return ret

	def clear(self):
		pass

	def feed(self, char):
		pass

class Add(Node):

  def __init__(self, first, second):
    from literal import Literal

    self.nodes = []

    if isinstance(first, str):
      first = Literal(first)

    if isinstance(first, Literal):
      self.nodes.append(first)
    elif isinstance(first, Add):
      self.nodes += first.nodes
    else:
      raise ParserBuilderError("can't add (%s) add (%s)"% (first.__class__.__name__, second.__class__.__name__))

    if isinstance(second, str):
      second = Literal(second)

    if isinstance(second, Literal):
      self.nodes.append(second)
    elif isinstance(second, Add):
      self.nodes += second.nodes
    else:
      raise ParserBuilderError("can't add (%s) add (%s)"% (first.__class__.__name__, second.__class__.__name__))
    self.clear()

  def clear(self):
    self.fail = False
    self.acum = []
    for node in self.nodes:
      node.clear()
    self.consume = self.nodes[-1::-1]

  def feed(self, char):
    if self.fail:
      return
    else:
      ret = self.consume[-1].feed(char)
      if ret == None:
        return
      self.acum.append(ret)
      self.consume.pop()
      if not self.consume:
        return self.acum

