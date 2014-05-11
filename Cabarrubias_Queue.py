class Queue:

	def __init__(self):
		self.queue = []
		self.front = None
		

	def __repr__(self):
		return self.queue.__repr__()


	def qsize(self):
		return len(self.queue)


	def enqueue(self, data):
		self.queue.append(data)
		self.front = self.queue[0]


	def dequeue(self):
		try:
			to_return = self.queue.pop(0)
			try:
				self.front = self.queue[0]
			except IndexError:
				self.front = None
		except IndexError:
			to_return = None
			self.front = None
		return to_return


	def remove(self, item):
		try:
			self.queue.remove(item)
		except ValueError:
			pass


if __name__ == '__main__':

	q = Queue()
	q.enqueue('a')
	q.enqueue('b')
	q.enqueue('c')
	q.enqueue('d')

	print q.dequeue()
	print q.dequeue()
	print q.dequeue()
	print q.dequeue()
	print q.dequeue()
	print q.dequeue()
	q.remove('a')

	# a = ['a', 'b']
	# a.remove('c')
	# print a

	print q.front
