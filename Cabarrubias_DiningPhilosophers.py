from Cabarrubias_CircularLinkedList import *
from threading import Thread, Lock
import random
import time

class Fork(Node):
	
	def __init__(self, data):
		Node.__init__(self, data)
		self.lock = Lock()

	def __str__(self):
		return '<Fork: %s>' % self.data


class Philosopher(Node, Thread):

	def __init__(self, data, fork):
		Node.__init__(self, data)
		Thread.__init__(self)
		self.right_fork = fork
		self.philosophers = None
		self.fork_list = None
	
	def __str__(self):
		return '<Philosopher: %s>' % self.data
	
	def __eat(self, delay):
		print '%s now eating for %d seconds...' % (self, delay)
		time.sleep(delay)

	def __remove_self_from_philosophers(self):
		self.philosophers.remove(self.data)
		print '%s already left the table.' % self

	def set_fork_list(self, fork_list):
		self.fork_list = fork_list

	def set_philosophers(self, philosophers):
		self.philosophers = philosophers

	def run(self):
		print '%s is already thinking.' % self
		right_fork = self.fork_list.find(self.right_fork.data)
		left_fork = self.fork_list.find(self.next.right_fork.data)

		with left_fork.lock, right_fork.lock:
			print '%s is using %s (L) and %s (R).' % (self, left_fork, right_fork)
			delay = random.randint(1, 5)
			self.__eat(delay)
			self.__remove_self_from_philosophers()


class DiningPhilosophers():
	
	def __init__(self):
		self.philosophers = CircularLinkedList()
		self.fork_list = CircularLinkedList()

		for i in xrange(1, 6):
			fork = Fork(i)
			self.fork_list.add(fork)
			self.philosophers.add(Philosopher(i, fork))
			self.philosophers.find(i).set_fork_list(self.fork_list)
			self.philosophers.find(i).set_philosophers(self.philosophers)


	def run_threads(self):
		initial, ctr = self.philosophers.first, self.philosophers.length
		while ctr > 0:
			initial.start()
			initial = initial.next
			ctr -= 1


		initial, ctr = self.philosophers.first, self.philosophers.length
		while ctr > 0:
			initial.join()
			initial = initial.next
			ctr -= 1

		print self.philosophers

		# self.philosophers.first.join()
		# initial = self.philosophers.first.next
		# while initial != self.philosophers.first:
		# 	initial.join()
		# 	initial = initial.next

		

if __name__ == '__main__':

	dp = DiningPhilosophers()
	dp.run_threads()