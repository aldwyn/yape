class Queue:

	def __init__(self):
		self.queue = []
		self.front = None


	def __len__(self):
		return len(self.queue)


	def __repr__(self):
		return self.queue.__repr__()


	def enqueue(self, data):
		self.queue.append(data)
		self.front = self.queue[0]


	def dequeue(self):
		to_return = self.front
		try:
			self.queue.remove(self.front)
			try:
				self.front = self.queue[0]
			except IndexError:
				self.front = None
		except ValueError:
			to_return = 'Queue is empty.'
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

	print q

	print q.dequeue()
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

	print q
