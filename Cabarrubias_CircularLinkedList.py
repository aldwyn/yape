from Cabarrubias_DoublyLinkedList import *
from Cabarrubias_Node import *

class CircularLinkedList(DoublyLinkedList):

	def __str__(self):
		haystack = [self.first]
		try:
			initial = self.first.next
			while initial and initial != self.first:
				try:
					haystack.append(initial)
					initial = initial.next
				except AttributeError:
					pass
		except AttributeError:
			pass
		return '[' + ', '.join(str(e) for e in haystack) + ']'

	def add(self, new_node):
		try:
			last = self.get(self.length-1)
			last.next = new_node
			new_node.prev = last
			new_node.next = self.first
		except AttributeError:
			self.first = new_node
		self.length += 1

	def remove(self, index):
		to_remove = self.find(index)
		if to_remove != self.first:
			try:
				to_remove.prev.next = to_remove.next
				to_remove.next.prev = to_remove.prev
			except AttributeError:
				pass
		else:
			last = self.get(self.length-1)
			self.first = to_remove.next
			to_remove.prev = last
			last.next = self.first
		self.length -= 1


if __name__ == '__main__':
	c = CircularLinkedList()
	c.add(Node(1))
	c.add(Node(2))
	c.add(Node(3))
	c.add(Node(4))
	c.add(Node(5))
	c.remove(1)
	c.remove(3)
	print c