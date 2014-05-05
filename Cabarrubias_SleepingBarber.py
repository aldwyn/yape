from Cabarrubias_Queue import *
from threading import Thread, Semaphore
from sys import stdout
import logging
import random
import time


class Barber(Thread):

	def __init__(self, expected_last, name='Tigtupi'):
		Thread.__init__(self)
		self.sema = Semaphore()
		self.name = name
		self.expected_last = expected_last
		self.queue = None
		self.condition = True


	def __beware(self):
		try:
			while self.queue:
				front = self.queue.dequeue()
				with self.sema:
					self.__serve(front)
				if front == self.expected_last:
					self.condition = False
			else:
				log_info('%s is sleeping' % self.name)
		except ValueError:
			pass


	def __serve(self, customer):
		log_info('%s is serving %s for %d seconds...' % (self.name, customer.name, customer.hairdo_rate))
		time.sleep(customer.hairdo_rate)
		log_info('%s is finished serving %s' % (self.name, customer.name))


	def set_queue(self, queue):
		self.queue = queue


	def run(self):
		while self.condition:
			while self.condition:
				self.__beware()
			else:
				log_info('%s\'s Barbershop is now closing' % self.name)



class Customer(Thread):

	def __init__(self, name):
		Thread.__init__(self)
		self.name = name
		self.idle_time = random.randint(10, 15)
		self.hairdo_rate = random.randint(1, 5)
		self.sema = None
		self.queue = None


	def set_barber(self, barber):
		self.barber = barber


	def set_queue(self, queue):
		self.queue = queue


	def __leave(self):
		log_info('%s is leaving' % self.name)
		self.queue.remove(self)


	def __wait(self):
		allowed = self.barber.sema.acquire(False)
		self.barber.sema.release()
		if self in self.queue:
			log_info('%s is waiting for %d seconds...' % (self.name, self.idle_time))
			time.sleep(self.idle_time)
			if self in self.queue:
				if self == self.barber.expected_last:
					self.barber.condition = False
				log_info('%s is already annoyed and is leaving' % self.name)
				self.__leave()
			

	def run(self):
		self.__wait()



class Lounge(Thread):

	def __init__(self, lounge_size, customers, barber):
		Thread.__init__(self)
		self.queue = Queue()
		self.barber = barber
		self.lounge_size = lounge_size
		self.customers = customers


	def __accomodate(self, min=0, max=3):
		waiting_time = random.randint(min, max)
		time.sleep(waiting_time)

		curr_customer = self.customers.dequeue()
		self.queue.enqueue(curr_customer)
		curr_customer.set_barber(self.barber)
		curr_customer.set_queue(self.queue)

		log_info('%s enters' % curr_customer.name)
		curr_customer.start()


	def run(self):
		log_info('%s\'s Barbershop now opens' % self.barber.name)
		counter = self.lounge_size

		while len(self.queue) == 0:
			while counter > 0 and self.customers:
				self.__accomodate()
				counter -= 1
		else:
			while self.customers:
				if len(self.queue) < self.lounge_size:
					self.__accomodate()

		for customer in self.queue:
			customer.join()


class Barbershop:

	def __init__(self, lounge_size, customer_size):
		logging.basicConfig(filename='data.log', level=logging.INFO, format='%(message)s')
		expected_last = None

		customers = Queue()

		for ascii in xrange(65, 65+customer_size):
			expected_last = Customer(chr(ascii))
			customers.enqueue(expected_last)

		self.barber = Barber(expected_last)
		self.lounge = Lounge(lounge_size, customers, self.barber)
		self.barber.set_queue(self.lounge.queue)


	def run_service(self):
		self.lounge.start()
		self.barber.start()




class SleepingBarberProblem:

	def __init__(self, lounge_size=5, customer_size=10):
		self.barbershop = Barbershop(lounge_size, customer_size)


	def test(self):
		self.barbershop.run_service()



def log_info(message):
	logging.info(message)
	stdout.write(message + '\n')


def main():
	sbp = SleepingBarberProblem()
	sbp.test()
	


if __name__ == '__main__':
	main()