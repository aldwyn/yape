from Cabarrubias_CircularLinkedList import *
from threading import Thread, Lock
from sys import stdout
import logging
import time


class Fork(Node):
	
	def __init__(self, data):
		Node.__init__(self, data)
		self.lock = Lock()


class Philosopher(Node, Thread):

	def __init__(self, data, fork_ref, eat_delay=5):
		Node.__init__(self, data)
		Thread.__init__(self, name=data)
		self.fork_ref = fork_ref
		self.eat_delay = eat_delay
		self.philosophers = None
		self.fork_list = None
		self.to_continue = True
	

	def __eat(self):
		log_info('Philosopher %s now eating for %d seconds...' % (self.data, self.eat_delay))
		time.sleep(self.eat_delay)
		log_info('Philosopher %s has done eating.' % self.data)


	def __leave(self):
		self.philosophers.remove(self.data)
		log_info('Philosopher %s left the table.' % self.data)


	def set_fork_list(self, fork_list):
		self.fork_list = fork_list


	def set_philosophers(self, philosophers):
		self.philosophers = philosophers


	def run(self):
		log_info('Philosopher %s is thinking & starving...' % self.data)

		right_fork = self.fork_list.find(self.fork_ref.data)
		left_fork = self.fork_list.find(self.fork_ref.next.data)
		
		while self.to_continue:
			log_info('Philosopher %s attempting to grab fork-%s (R)...' % (self.data, right_fork.data))
			if not right_fork.lock.locked():
				right_fork.lock.acquire()
				log_info('Philosopher %s has acquired fork-%s (R).' % (self.data, right_fork.data))
				log_info('Philosopher %s attempting to grab fork-%s (L)...' % (self.data, left_fork.data))
				if not left_fork.lock.locked():
					log_info('Philosopher %s has acquired fork-%s (L).' % (self.data, left_fork.data))
					log_info('Philosopher %s successfully grabbed both forks.' % self.data)
					left_fork.lock.acquire()
					self.__eat()
					self.to_continue = False
					left_fork.lock.release()
					log_info('Philosopher %s has released fork-%s (L).' % (self.data, left_fork.data))
				else:
					log_info('Philosopher %s failed to grab fork-%s (L)' % (self.data, left_fork.data))
					self.to_continue = True					
				right_fork.lock.release()
				log_info('Philosopher %s has released fork-%s (R).' % (self.data, right_fork.data))
			else:
				log_info('Philosopher %s failed to grab fork-%s (R)' % (self.data, right_fork.data))
				self.to_continue = True
				
		self.__leave()


class DiningPhilosophersProblem:
	
	def __init__(self, size=5, eat_delay=0):
		self.philosophers = CircularLinkedList()
		self.fork_list = CircularLinkedList()

		for i in xrange(1, size+1):
			self.fork_list.add(Fork(i))
		
		curr_node_thread, i = self.fork_list.first, 1
		while i < size+1:
			fork_ref = self.fork_list.find(i)
			self.philosophers.add(Philosopher(i, fork_ref))
			self.philosophers.find(i).set_fork_list(self.fork_list)
			self.philosophers.find(i).set_philosophers(self.philosophers)
			curr_node_thread = curr_node_thread.next
			i += 1

		
	def run_threads(self):
		logging.basicConfig(filename='data.log', level=logging.INFO)

		curr_node_thread, i = self.philosophers.first, self.philosophers.length
		while i > 0:
			curr_node_thread.start()
			curr_node_thread = curr_node_thread.next
			i -= 1

		curr_node_thread, i = self.philosophers.first, self.philosophers.length
		while i > 0:
			curr_node_thread.join()
			curr_node_thread = curr_node_thread.next
			i -= 1

		log_info('All philosophers have dined and left.')


def log_info(message):
	logging.info('\t' + message)
	stdout.write(message + '\n')


if __name__ == '__main__':
	
	dpp = DiningPhilosophersProblem()
	dpp.run_threads()