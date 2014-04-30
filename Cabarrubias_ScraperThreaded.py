from bs4 import BeautifulSoup
from collections import OrderedDict
from threading import Thread, Lock
import logging
import requests
import json
import cProfile


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
		self.keyword = None
		self.queue = None
		self.workers = None


	def __set_keyword(self, keyword):
		self.keyword = keyword


	def __conclude():
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

			logging.info(json.dumps(databit, indent=4))
			
			print 'EXTRACTED:\t' + databit['job_title'].encode('utf-8')


	def __search(self):
		page_counter = 1

		request = self.__request(page_counter)
		parser = BeautifulSoup(request.text)
		
		while parser.find(attrs='jobs_table'):
			print 'Executing scraper to page', page_counter, 'of', self.url + '?q=' + self.keyword, '...'
			jobs = parser.find_all(attrs={'class': 'aJobS'})
			self.__scrape(jobs)
			page_counter += 1
			request = self.__request(page_counter)
			parser = BeautifulSoup(request.text)
	

	def set_queue(self, queue):
		self.queue = queue


	def set_workers(self, workers):
		self.workers = workers


	def run(self):
		front = self.queue[0]
		while not front.lock.locked():
			front.lock.acquire()
			self.__set_keyword(front.name)
			front.lock.release()
			self.queue.remove(front)
			self.__search()

		self.__conclude()





class MynimoWebScraper:
	
	def __init__(self, keywords, searchType='jobs', searchCategory=''):
		logging.basicConfig(filename='scraped.json', level=logging.INFO, format='%(message)s')
		self.searchType = searchType
		self.searchCategory = searchCategory

		self.queue = []
		self.workers = []
		for i in xrange(0, len(keywords)):
			self.queue.append(Keyword(keywords[i]))
			self.workers.append(Worker(searchType=searchType, searchCategory=searchCategory))
			self.workers[i].set_queue(self.queue)
			self.workers[i].set_workers(self.workers)


	def run_threads(self):
		for worker in self.workers:
			worker.start()



if __name__ == '__main__':

	s = MynimoWebScraper(['python', 'java'])
	s.run_threads()