from multiprocessing import Process, Queue, Lock
import multiprocessing as mp
import time

class Keywords:

	def __init__(self, keywords=None):
		self.queue = Queue()
		self.lock = Lock()
		if keywords:
			for k in keywords:
				self.queue.put(k)

	def put(self, keyword):
		self.queue.put(keyword)


def scrape(condition, keywords, i):
	while True:
		front = None
		with keywords.lock:
			front = keywords.queue.get()
		if front:
			print i, front
			time.sleep(5)
		else:
			print i, 'poisoned'
			keywords.put(None)
			break


if __name__ == '__main__':
	keywords = Keywords(['java', 'php', 'ruby', 'python', 'c++'])

	#poison pill
	keywords.put(None)

	workers = []
	for i in xrange(mp.cpu_count()):
		workers.append(Process(target=scrape, args=(True, keywords, i)))

	for worker in workers:
		worker.start()