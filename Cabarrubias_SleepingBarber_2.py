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
		

	def __serve(self, customer):
		self.lounge.sema.release()
		log_info('%s is serving %s for %d seconds...' % (self.name, 'hey', customer.hairdo_rate))
		customer.is_being_served = True
		time.sleep(customer.hairdo_rate)
		log_info('%s is done serving %s' % (self.name, customer.name))


	def run(self):
		while True:
			customer = self.lounge.seats.dequeue()
			if customer:
				log_info(customer.name)
				self.__serve(customer)
			else:
				log_info('%s is now sleeping' % self.name)
				break



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
		self.lounge_size = lounge_size
		self.seats = Queue()


	def is_present(self, item):
		return item in self.seats.queue




class Barbershop:

	def __init__(self, lounge_size, customer_size):
		lounge = Lounge(lounge_size)
		self.waitlist = []

		for ascii in xrange(65, 65+customer_size):
			customer = Customer(chr(ascii), lounge)
			self.waitlist.append(customer)

		self.barber = Barber(lounge)


	def run_service(self):
		for customer in self.waitlist:
			customer.start()
		
		self.barber.start()

		for customer in self.waitlist:
			customer.join()

		# adding poison pill to the waitlist
		poison_pill = None
		self.waitlist.append(poison_pill)



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