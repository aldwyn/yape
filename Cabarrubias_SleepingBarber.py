from Cabarrubias_Queue import *
from threading import Thread, Semaphore
from sys import stdout
import logging
import random
import time


class Barber(Thread):

	def __init__(self, name='Tigtupi', expected=10):
		Thread.__init__(self)
		self.sema = Semaphore()
		self.name = name
		self.queue = None
		self.expected = expected

	def set_queue(self, lounge):
		self.queue = lounge.queue

	def serve(self, customer):
		log_info('%s is serving %s for %d seconds... ######################################' % (self.name, customer.name, customer.hairdo_rate))
		time.sleep(customer.hairdo_rate)
		log_info('%s is finished serving %s' % (self.name, customer.name))

	def run(self):
		while self.expected:
			while self.queue:
				try:
					front = self.queue.dequeue()
					with self.sema:
						self.serve(front)
					self.expected -= 1
				except ValueError:
					pass
			else:
				log_info('%s is zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' % self.name)

		print self.queue



class Customer(Thread):

	def __init__(self, name):
		Thread.__init__(self)
		self.name = name
		self.idle_time = random.randint(10, 15)
		self.hairdo_rate = random.randint(1, 5)
		self.sema = None
		self.queue = None

	def set_sema(self, sema):
		self.sema = sema

	def set_queue(self, queue):
		self.queue = queue

	def __leave(self):
		log_info('%s is leaving' % self.name)
		self.queue.remove(self)

	def __wait(self):
		allowed = self.sema.acquire(False)
		self.sema.release()
		if self in self.queue:
			log_info('%s is waiting for %d seconds...' % (self.name, self.idle_time))
			time.sleep(self.idle_time)
			if self in self.queue:
				log_info(self.name + 'time up! ----------------------------------------')
				self.__leave()
			

	def run(self):
		log_info('%s enters' % self.name)
		self.__wait()



class Lounge(Thread):

	def __init__(self, lounge_size, customers, barber):
		Thread.__init__(self)
		self.queue = Queue()
		self.barber = barber
		self.lounge_size = lounge_size
		self.customers = customers

	def __accomodate(self, min=0, max=3):
		time.sleep(random.randint(min, max))
		pick = random.randint(0, len(self.customers))
		while pick >= len(self.customers):
			pick = random.randint(0, len(self.customers))
		pick = self.customers[pick]
		curr_customer = Customer(pick)
		self.customers.remove(pick)
		self.queue.enqueue(curr_customer)
		curr_customer.set_sema(self.barber.sema)
		curr_customer.set_queue(self.queue)
		curr_customer.start()

	def run(self):
		counter = self.lounge_size
		while len(self.queue) == 0:
			while counter > 0 and self.customers:
				self.__accomodate()
				counter -= 1
		else:
			while self.customers:
				if len(self.queue) < self.lounge_size:
					self.__accomodate()
			else:
				log_info('Barbershop to-be-service limit reached')


class SleepingBarberProblem:

	def __init__(self, lounge_size):
		logging.basicConfig(filename='data.log', level=logging.INFO, format='%(message)s')
		self.lounge_size = lounge_size
		self.barber = Barber()

		customers = [chr(i) for i in xrange(65, 75)]

		self.lounge = Lounge(lounge_size, customers, self.barber)
		self.barber.set_queue(self.lounge)


	def run_service(self):
		self.lounge.start()
		self.barber.start()





def log_info(message):
	logging.info(message)
	stdout.write(message + '\n')


def main():
	sbp = SleepingBarberProblem(5)
	sbp.run_service()
	


if __name__ == '__main__':
	main()