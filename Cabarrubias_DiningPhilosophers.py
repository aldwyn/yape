from Cabarrubias_CircularLinkedList import *
from threading import Thread, Lock
import random
import time

class Philosopher(Node, Thread):

	def __init__(self, data, fork):
		Node.__init__(self, data)
		Thread.__init__(self)
		self.right_fork = fork
		self.c_list = None
	
	def __str__(self):
		return '<Philosopher: %s>' % self.data
	
	def eat(self, delay):
		print '%s now eating for %d seconds...' % (self, delay)
		time.sleep(delay)

	def is_rfork_on(self):
		print 'Attempting to grab right fork of %s' % self,
		result = self.right_fork.locked
		print 'Successful' if result else 'Failed'
		return result

	def is_lfork_on(self):
		print 'Attempting to grab left fork of %s' % self,
		result = self.next.right_fork.locked
		print 'Successful' if result else 'Failed'
		return result

	def is_forks_down(self):
		pass

	def set_c_list(self, c_list):
		self.c_list = c_list

	def remove_self_from_list(self):
		self.c_list.remove(self.data)
		print '%s already left the table' % self

	def run(self):
		if self.is_lfork_on() and self.is_rfork_on():
			self.right_fork.acquire()
			self.next.right_fork.acquire()

			delay = random.randint(1, 5)
			self.eat(delay)
			self.remove_self_from_list()
			
			self.right_fork.release()
			self.next.right_fork.release()



class DiningPhilosophers():
	
	def __init__(self):
		self.philosophers = CircularLinkedList()
		self.forks = CircularLinkedList()

		for i in xrange(1, 6):
			fork = Lock()
			self.forks.add(fork)
			self.philosophers.add(Philosopher(i, fork))
			self.philosophers.find(i).set_c_list(self.philosophers)


	def process(self):
		self.philosophers.first.start()
		initial = self.philosophers.first.next
		while initial and initial != self.philosophers.first:
			try:
				initial.start()
				initial = initial.next
			except AttributeError:
				pass

        # initial = squad.first
        # while self.philosophers.length > 0:
        #     if ctr % k == 0:
        #         squad.remove(initial.data)
        #     initial = initial.next
        #     ctr += 1

		self.philosophers.first.join()
		initial = self.philosophers.first.next
		while initial and initial != self.philosophers.first:
			try:
				initial.join()
				initial = initial.next
			except AttributeError:
				pass

		print self.philosophers

		

if __name__ == '__main__':

	dp = DiningPhilosophers()

	print dp.philosophers
	dp.process()
	