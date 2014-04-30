class Queue:

	def __init__(self):
		self.queue = []
		self.front = None


	def __str__(self):
		return '['+', '.join(self.queue)+']'

	def enqueue(self, data):
		self.queue.append(data)
		self.front = self.queue[0]


	def dequeue(self):
		front = self.front
		self.queue.remove(front)
		return front


if __name__ == '__main__':

	q = Queue()
	q.enqueue('a')
	q.enqueue('b')

	print q

	q.dequeue()

	print q
