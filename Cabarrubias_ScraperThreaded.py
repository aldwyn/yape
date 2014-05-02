from Cabarrubias_Queue import *
from bs4 import BeautifulSoup
from collections import OrderedDict
from threading import Thread, Lock
import logging
import requests
import json
import cProfile


logging.basicConfig(filename='scraped.json', level=logging.WARNING, format='%(message)s')
requests_log = logging.getLogger('requests')


class Keyword:

	def __init__(self, name):
		self.name = name
		self.lock = Lock()


class Worker(Thread):

	def __init__(self, searchType='jobs', searchCategory=''):
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
		self.searchCounts = 0
		self.condition = True
		self.keyword = None
		self.queue = None
		self.workers = None


	def __set_keyword(self, keyword):
		self.keyword = keyword


	def __conclude(self):
		print '%d searches for %s' % (self.searchCounts, self.keyword)
		self.workers.remove(self)


	def __request(self, page):
		to_request = self.url + self.searchType + '/search/'
		payload = {'q': self.keyword, 'page': page, 'searchType': self.searchType, 'searchCategory': self.searchCategory}
		return requests.get(to_request, params=payload, proxies=self.proxies, timeout=10.0)


	def __scrape(self, jobs):
		for job in jobs:
			databit = OrderedDict()
			databit['keyword'] = self.keyword
			databit['job_title'] = job.find_all('td')[0].find(attrs='jobTitleLink').string
			databit['company'] = job.find_all('td')[2].string.strip()
			location = job.find_all('td')[1]
			
			try:
				address = location.find(attrs='address')
				databit['location'] = address.string + ', ' + address.previous_element.previous_element.strip()
			except AttributeError:
				databit['location'] = location.string.strip()
			
			databit['short_description'] = ' '.join(job.find_next('tr').find(attrs='searchContent').text.encode('utf-8').split())

			requests_log.warning(json.dumps(databit, indent=4))


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

	

	def set_queue(self, queue):
		self.queue = queue


	def set_workers(self, workers):
		self.workers = workers


	def run(self):
		while self.condition:
			if not self.queue.front.lock.locked():
				front = self.queue.dequeue()
				self.condition = False
				with front.lock:
					self.__set_keyword(front.name)
		
		self.__search()
		self.__conclude()



class MynimoWebScraper:
	
	def __init__(self, keywords, searchType='jobs', searchCategory=''):
		self.searchType = searchType
		self.searchCategory = searchCategory

		self.queue = Queue()
		self.workers = []
		for i in xrange(0, len(keywords)):
			self.queue.enqueue(Keyword(keywords[i]))
			self.workers.append(Worker(searchType=searchType, searchCategory=searchCategory))
			self.workers[i].set_queue(self.queue)
			self.workers[i].set_workers(self.workers)


	def run_threads(self):

		for worker in self.workers:
			worker.start()



if __name__ == '__main__':

	s = MynimoWebScraper(['python', 'java', 'php', 'ruby', 'rails'])
	s.run_threads()