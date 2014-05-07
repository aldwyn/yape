from Cabarrubias_Queue import *
from bs4 import BeautifulSoup
from collections import OrderedDict
from threading import Thread, Lock
import logging
import requests
import json
import cProfile




class Keywords(Queue):

	def __init__(self):
		Queue.__init__(self)
		self.lock = Lock()


class Logger(Thread):

	def __init__(self, data_to_log):
		Thread.__init__(self)
		logging.basicConfig(filename='scraped.json', level=logging.WARNING, format='%(message)s')
		logging.getLogger('requests')
		self.data_to_log = data_to_log

	def run(self):
		while self.data_to_log:
			to_log = self.data_to_log.dequeue()
			logging.warning(json.dumps(to_log, indent=4))
		


class Worker(Thread):

	def __init__(self, data_to_log, searchType='jobs', searchCategory=''):
		Thread.__init__(self)
		self.proxies = {
				'http': 'http://23.27.197.200:24801',
				'http': 'http://23.27.197.201:24801',
				'http': 'http://23.27.197.202:24801',
				'http': 'http://23.27.197.203:24801',
				'http': 'http://23.27.197.204:24801',
				'http': 'http://23.27.197.205:24801',
			}
		self.url = 'http://mynimo.com/'
		self.searchType = searchType
		self.searchCategory = searchCategory
		self.data_to_log = data_to_log
		self.searchCounts = 0
		self.condition = True
		self.keywords = None
		self.workers = None
		self.keyword = None



	def __set_keyword(self, keyword):
		self.keyword = keyword


	def __conclude(self):
		print '%d searches for %s' % (self.searchCounts, self.keyword)


	def __request(self, page):
		to_request = self.url + self.searchType + '/search/'
		payload = {'q': self.keyword, 'page': page, 'searchType': self.searchType, 'searchCategory': self.searchCategory}
		return requests.get(to_request, params=payload, proxies=self.proxies, timeout=10.0)


	def __scrape(self, jobs):
		for job in jobs:
			databit = OrderedDict()
			databit['keyword'] = self.keyword
			databit['job_title'] = job.find_all('td')[0].find(attrs='jobTitleLink').string.encode('utf-8').strip()
			databit['company'] = job.find_all('td')[2].string.strip()
			location = job.find_all('td')[1]
			
			try:
				address = location.find(attrs='address')
				databit['location'] = address.string + ', ' + address.previous_element.previous_element.strip()
			except AttributeError:
				databit['location'] = location.string.strip()
			
			databit['short_description'] = ' '.join(job.find_next('tr').find(attrs='searchContent').text.encode('utf-8').split())

			self.data_to_log.enqueue(databit)
			# print 'EXTRACTED: %s' % databit['job_title']
			# requests_log.warning(json.dumps(databit, indent=4))


	def __search(self):
		page_counter = 1
		
		request = self.__request(page_counter)
		parser = BeautifulSoup(request.text)
		
		while parser.find(attrs='jobs_table'):
			print 'Executing scraper to page', page_counter, 'of', self.url + '?q=' + self.keyword, '...'
			jobs = parser.find_all(attrs={'class': 'aJobS'})
			self.searchCounts += len(jobs)
			self.__scrape(jobs)
			page_counter += 1
			request = self.__request(page_counter)
			parser = BeautifulSoup(request.text)

	

	def set_keywords(self, keywords):
		self.keywords = keywords


	def set_workers(self, workers):
		self.workers = workers

	def set_poison(self, poison):
		self.poison = poison


	def run(self):
		while self.condition:
			if not self.keywords.lock.locked() and self.keywords:
				front = self.keywords.dequeue()
				if front is not None:
					with self.keywords.lock:
						self.__set_keyword(front)
						print '%s acquired %s' % (self, front)
					self.__search()
					self.__conclude()
				else:
					# pill the poison
					self.condition = False
			else:
				# pill the poison
				self.condition = False
		else:
			print '%s has been poisoned' % self



class MynimoWebScraper:
	
	def __init__(self, keywords, worker_size=3, searchType='jobs', searchCategory=''):
		self.searchType = searchType
		self.searchCategory = searchCategory

		self.keywords = Keywords()
		self.workers = []
		self.data_to_log = Queue()
		self.logger = Logger(self.data_to_log)

		for keyword in keywords:
			self.keywords.enqueue(keyword)

		# adding poison
		poison = None
		self.keywords.enqueue(poison)

		for i in xrange(worker_size):
			self.workers.append(Worker(self.data_to_log, searchType=searchType, searchCategory=searchCategory))
			self.workers[i].set_workers(self.workers)
			self.workers[i].set_keywords(self.keywords)


	def run_threads(self):
		for worker in self.workers:
			worker.start()

		self.logger.start()





if __name__ == '__main__':

	s = MynimoWebScraper(['python', 'java', 'php', 'ruby', 'rails'])
	s.run_threads()