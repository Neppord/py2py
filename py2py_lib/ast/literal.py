from node import Node

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

