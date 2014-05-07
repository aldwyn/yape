import threading
import random
import time

class Thread(threading.Thread):

	def __init__(self, data):
		threading.Thread.__init__(self)
		self.data = data

	def run(self):
		print 'Value %d in thread %s' % (self.data, self.getName())
		seconds_to_sleep = random.randint(1, 5)
		print '%s sleeping for %d seconds...' % (self.getName(), seconds_to_sleep)
		time.sleep(seconds_to_sleep)

			

if __name__ == '__main__':
	a = Thread(4)
	a.setName('Aldwyn')

	b = Thread(4)
	b.setName('Oreo')

	a.start()
	b.start()

	a.join()
	b.join()

	print 'Terminating...'