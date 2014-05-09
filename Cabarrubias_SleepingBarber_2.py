from Cabarrubias_Queue import *
from threading import Thread, Semaphore
from sys import stdout
import logging
import random
import time


logging.basicConfig(filename='data.log', level=logging.INFO, format='%(message)s')


class Barber(Thread):

	def __init__(self, lounge, name='Tigtupi'):
		Thread.__init__(self)
		self.name = name
		self.poison_pill = None
		self.lounge = lounge
		self.is_barbershop_not_close = True


	def familiarize_poison_pill(self, poison_pill):
		self.poison_pill = poison_pill
		

	def __serve(self, customer):
		self.lounge.sema.release()
		log_info('%s is serving %s for %d seconds...' % (self.name, customer.name, customer.hairdo_rate))
		customer.is_being_served = True
		time.sleep(customer.hairdo_rate)
		log_info('%s is done serving %s' % (self.name, customer.name))


	def run(self):
		while True:
			customer = self.lounge.seats.dequeue()
			if customer:
				self.__serve(customer)
				if customer == self.poison_pill:
					break
		log_info('%s sleeps' % self.name)


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
		if self.lounge.is_present(self) and not self.is_being_served:
			log_info('%s is waiting for %d seconds...' % (self.name, self.idle_time))
			time.sleep(self.idle_time)
		try:
			if self.lounge.is_present(self) and not self.is_being_served:
				log_info('%s is annoyed and is leaving' % self.name)
				self.lounge.seats.remove(self)
		except ValueError:
			pass
		
		self.lounge.sema.release()


	def run(self):
		while self.is_waiting_outside:
			if self.lounge.sema.acquire(False):
				log_info('%s acquired a seat' % self.name)
				self.is_waiting_outside = False
				self.lounge.seats.enqueue(self)
				self.__wait()

		

class Lounge:

	def __init__(self, lounge_size):
		self.sema = Semaphore(lounge_size)
		self.seats = Queue()
		self.lounge_size = lounge_size


	def is_present(self, item):
		return item in self.seats.queue



class Barbershop:

	def __init__(self, lounge_size):
		self.lounge = Lounge(lounge_size)
		self.barber = Barber(self.lounge)



class SleepingBarberProblem:

	def __init__(self, lounge_size=5, customer_size=20):
		self.barbershop = Barbershop(lounge_size)
		self.customers = []

		for ascii in xrange(65, 65+customer_size):
			# customer = Customer(chr(ascii), self.barbershop.lounge)
			customer = Customer(ascii-65, self.barbershop.lounge)
			self.customers.append(customer)

		self.poison_pill = Customer('Poison Ivy', self.barbershop.lounge)
		self.barbershop.barber.familiarize_poison_pill(self.poison_pill)


	def simulate(self):
		self.barbershop.barber.start()

		for customer in self.customers:
			time.sleep(random.randint(0, 5))
			customer.start()

		time.sleep(10)
		print '-------------------------------------------------------'
		self.poison_pill.start()



def log_info(message):
	logging.info(message)
	stdout.write(message + '\n')



if __name__ == '__main__':
	sbp = SleepingBarberProblem()
	sbp.simulate()