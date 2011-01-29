class Node(object):
	def __and__(self, other):
		return And(self, other)

	def __rand__(self, other):
		return And(other, self)

	def __or__(self, other):
		return Or(self, other)

	def __ror__(self, other):
		return Or(other, self)

	def __getitem__(self, slice):
		return Slice(self, slice)

	def parse(self, string):
		for c in string:
			ret = self.feed(c)
			if ret:
				return ret

	def clear(self):
		pass

	def feed(self, char):
		pass

class Literal(Node):

	def __init__(self, string):
		self.string = string
		self.clear()
	
	def clear(self):
		self.faild = False
		self.consume = list(self.string[-1::-1])
	
	def feed(self, char):
		if self.faild:
			return
		else:
			if char == self.consume.pop():
				if not self.consume:
					return self.string
				return
			else:
				self.faild = True
				return

