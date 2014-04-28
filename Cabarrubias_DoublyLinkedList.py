from Cabarrubias_Node import *

class DoublyLinkedList:

	def __init__(self):
		self.first = None
		self.length = 0

	def __str__(self):
		haystack = []
		initial = self.first
		ctr = 0
		while initial:
			haystack.append(initial)
			initial = initial.next
		return '[' + ', '.join(str(e) for e in haystack) + ']'

	def add(self, new_node):
		try:
			last = self.get(self.length-1)
			last.next = new_node
			new_node.prev = last
		except AttributeError:
			self.first = new_node
		self.length += 1

	def get(self, index):
		initial = self.first
		ctr = 0
		while initial:
			if ctr == index:
				return initial
			initial = initial.next
			ctr += 1

	def find(self, filter):
		initial = self.first
		while initial:
			if initial.data == filter:
				return initial
			initial = initial.next

	def remove(self, index):
		to_remove = self.find(index)
		if to_remove != self.first:
			try:
				to_remove.prev.next = to_remove.next
				to_remove.next.prev = to_remove.prev
			except AttributeError:
				pass
		else:
			self.first = to_remove.next
			to_remove.prev = None
		self.length -= 1


if __name__ == '__main__':
	d = DoublyLinkedList()
	d.add(Node(1))
	d.add(Node(2))
	d.add(Node(3))
	d.remove(1)
	print d