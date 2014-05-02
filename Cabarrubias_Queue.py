class Queue(list):

	def __init__(self):
		list.__init__(self)
		self.front = None


	def enqueue(self, data):
		self.append(data)
		self.front = self[0]


	def dequeue(self):
		to_return = self.front
		try:
			self.remove(self.front)
			try:
				self.front = self[0]
			except IndexError:
				self.front = None
			return to_return
		except IndexError:
			return 'Queue is empty.'


if __name__ == '__main__':

	q = Queue()
	q.enqueue('a')
	q.enqueue('b')

	print q
	print q.dequeue()

	print q
	print q.dequeue()

	print q.front
