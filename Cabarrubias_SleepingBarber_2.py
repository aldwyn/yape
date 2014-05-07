from Cabarrubias_Queue import *
from threading import Thread, Semaphore
from sys import stdout
import logging
import random
import time


class Barber(Thread):

	def __init__(self, lounge, name='Tigtupi'):
		Thread.__init__(self)
		self.name = name
		self.lounge = lounge
		self.alive = True


	def __die(self):
		self.alive = False
		

	def __serve(self, customer):
		log_info('%s is serving %s for %d seconds...' % (self.name, customer.name, customer.hairdo_rate))
		customer.is_being_served = True
		time.sleep(customer.hairdo_rate)
		log_info('%s is done serving %s' % (self.name, customer.name))


	def run(self):
		while self.alive:
			try:
				while self.lounge.seats:
					customer = self.lounge.seats.dequeue()
					self.lounge.sema.release()
					if customer is self.lounge.poison_pill:
						self.__die()
					self.__serve(customer)
				else:
					log_info('%s is sleeping' % self.name)
					if self.lounge.poison_pill:
						self.__die()
			except ValueError:
				pass
		else:
			log_info('%s\'s Barbershop is now closing' % self.name)




class Customer(Thread):

	def __init__(self, name, lounge, idle_time=None):
		Thread.__init__(self)
		self.name = name
		self.idle_time = idle_time or random.randint(10, 15)
		self.hairdo_rate = random.randint(1, 5)
		self.is_waiting_outside = True
		self.is_allowed_to_sit = False
		self.is_being_served = False
		self.lounge = lounge


	def __wait(self):
		if self in self.lounge.seats and not self.is_being_served:
			log_info('%s is waiting for %d seconds...' % (self.name, self.idle_time))
			time.sleep(self.idle_time)
		try:
			if self in self.lounge.seats and not self.is_being_served:
				log_info('%s is annoyed and is leaving' % self.name)
				self.lounge.seats.remove(self)
		except ValueError:
			pass
		
		self.lounge.sema.release()


	def run(self):
		while self.is_waiting_outside:
			self.is_allowed_to_sit = self.lounge.sema.acquire(False)
			if self.is_allowed_to_sit and self.lounge.is_enqueueable():
				log_info('%s acquired a seat' % self.name)
				self.is_waiting_outside = False
				self.lounge.seats.enqueue(self)
				self.lounge.counter += 1
				if self.lounge.counter == self.lounge.expected_customer_size:
					self.lounge.poison_pill = self
					self.idle_time = 30
				self.__wait()

		

class Lounge:

	def __init__(self, lounge_size, expected_customer_size):
		self.sema = Semaphore(lounge_size)
		self.lounge_size = lounge_size
		self.seats = Queue()
		self.poison_pill = None
		self.counter = 0
		self.expected_customer_size = expected_customer_size


	def is_enqueueable(self):
		return len(self.seats) < self.lounge_size



class Barbershop:

	def __init__(self, lounge_size, customer_size):
		lounge = Lounge(lounge_size, customer_size)
		self.waitlist = []

		for ascii in xrange(65, 65+customer_size):
			customer = Customer(chr(ascii), lounge)
			self.waitlist.append(customer)

		self.barber = Barber(lounge)


	def run_service(self):
		self.barber.start()
		for customer in self.waitlist:
			customer.start()



class SleepingBarberProblem:

	def __init__(self, lounge_size=5, customer_size=20):
		logging.basicConfig(filename='data.log', level=logging.INFO, format='%(message)s')
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