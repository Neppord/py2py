
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


