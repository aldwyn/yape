from Cabarrubias_Queue import *
from threading import Thread, Semaphore
import sys, logging, random, time


logging.basicConfig(filename='data.log', level=logging.INFO, format='%(message)s')


class Barber(Thread):

	def __init__(self, lounge, name='Tigtupi'):
		Thread.__init__(self)
		self.name = name
		self.__poison_pill = None
		self.__lounge = lounge
		

	def familiarize_poison_pill(self, poison_pill):
		self.__poison_pill = poison_pill
		

	def __serve(self, customer):
		self.__lounge.sema.release()
		log_info('%s is serving %s for %d seconds...' % (self.name, customer.name, customer.hairdo_rate))
		customer.is_being_served = True
		time.sleep(customer.hairdo_rate)
		log_info('%s has been served and leaves' % customer.name)


	def run(self):
		while True:
			customer = self.__lounge.seats.dequeue()
			if customer:
				self.__serve(customer)
				if customer == self.__poison_pill:
					break
			else:
				log_info('%s is sleeping' % self.name)
		log_info('%s\'s barbershop now closes' % self.name)



class Customer(Thread):

	def __init__(self, name, lounge, idle_time=None):
		Thread.__init__(self)
		self.name = name
		self.hairdo_rate = random.randint(1, 5)
		self.is_being_served = False
		self.__idle_time = idle_time or random.randint(10, 15)
		self.__is_waiting_outside = True
		self.__is_allowed_to_sit = False
		self.__lounge = lounge


	def __wait(self):
		if self in self.__lounge.seats.queue and not self.is_being_served:
			log_info('%s is waiting for %d seconds...' % (self.name, self.__idle_time))
			time.sleep(self.__idle_time)
			
		try: # if not still served
			if self in self.__lounge.seats.queue and not self.is_being_served:
				log_info('%s is annoyed and is leaving' % self.name)
				self.__lounge.seats.remove(self)
		except ValueError:
			pass
		
		self.__lounge.sema.release()


	def run(self):
		while self.__is_waiting_outside:
			if self.__lounge.sema.acquire(False):
				log_info('%s acquired a seat' % self.name)
				self.__is_waiting_outside = False
				self.__lounge.seats.enqueue(self)
				self.__wait()


		
class Lounge:

	def __init__(self, lounge_size):
		self.sema = Semaphore(lounge_size)
		self.seats = Queue()



class Barbershop:

	def __init__(self, lounge_size):
		self.lounge = Lounge(lounge_size)
		self.barber = Barber(self.lounge)



class SleepingBarberProblem:

	def __init__(self, lounge_size=5, customer_size=20):
		self.barbershop = Barbershop(lounge_size)
		self.customers = []

		for ascii in xrange(65, 65+customer_size):
			customer = Customer(chr(ascii), self.barbershop.lounge)
			# customer = Customer(ascii-65, self.barbershop.lounge)
			self.customers.append(customer)

		self.poison_pill = Customer('Poison Ivy', self.barbershop.lounge)
		self.barbershop.barber.familiarize_poison_pill(self.poison_pill)


	def simulate(self):
		self.barbershop.barber.start()

		for customer in self.customers:
			time.sleep(random.randint(0, 5))
			customer.start()

		time.sleep(1)
		self.poison_pill.start()



def log_info(message):
	logging.info(message)
	sys.stdout.write(message + '\n')



if __name__ == '__main__':
	sbp = SleepingBarberProblem()
	sbp.simulate()