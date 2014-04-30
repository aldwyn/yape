from Cabarrubias_CircularLinkedList import *
from threading import Thread, Lock
from sys import stdout
import logging
import time


class Fork:
	
	def __init__(self, data):
		self.data = data
		self.lock = Lock()


class Philosopher(Thread):

	def __init__(self, data, r_fork, l_fork, eat_delay=5, think_delay=0):
		Thread.__init__(self, name=data)
		self.data = data
		self.r_fork = r_fork
		self.l_fork = l_fork
		self.eat_delay = eat_delay
		self.think_delay = think_delay
		self.philosophers = None
		self.fork_list = None
		self.to_continue = True
	

	def __eat(self):
		log_info('Philosopher %s is finishing eating' % self.data)
		time.sleep(self.eat_delay)


	def __think(self):
		log_info('Philosopher %s is thinking' % self.data)
		time.sleep(self.think_delay)


	def __leave(self):
		self.philosophers.remove(self)


	def set_philosophers(self, philosophers):
		self.philosophers = philosophers


	def run(self):
		while self.to_continue:
			self.__think()
			if not self.l_fork.lock.locked():
				log_info('Philosopher %s acquires left fork' % self.data)
				self.l_fork.lock.acquire()
				if not self.r_fork.lock.locked():
					log_info('Philosopher %s acquires right fork' % self.data)
					self.r_fork.lock.acquire()
					log_info('Philosopher %s is eating' % self.data)
					self.__eat()
					self.to_continue = False
					log_info('Philosopher %s releases right fork' % self.data)
					self.r_fork.lock.release()
				self.l_fork.lock.release()
				log_info('Philosopher %s releases left fork' % self.data)
				
		self.__leave()


class DiningPhilosophersProblem:
	
	def __init__(self, size=5, eat_delay=0):
		self.philosophers = []
		self.fork_list = []

		for i in xrange(1, size+1):
			self.fork_list.append(Fork(i))

		for i in xrange(0, size):
			r_fork = self.fork_list[i]
			l_fork = self.fork_list[(i+1) % size]
			self.philosophers.append(Philosopher(i+1, r_fork, l_fork))
			self.philosophers[i].set_philosophers(self.philosophers)

		
	def run_threads(self):
		logging.basicConfig(filename='data.log', level=logging.INFO, format='%(message)s')

		for philosopher in self.philosophers:
			philosopher.start()

		for philosopher in self.philosophers:
			philosopher.join()

		# log_info('All philosophers have dined and left.')


def log_info(message):
	logging.info(message)
	stdout.write(message + '\n')


if __name__ == '__main__':
	
	dpp = DiningPhilosophersProblem(size=6)
	dpp.run_threads()