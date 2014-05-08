from bs4 import BeautifulSoup
from collections import OrderedDict
import requests, json, logging, multiprocessing as mp


# global variables
logging.basicConfig(filename='scraped.json', level=logging.WARNING, format='%(message)s')
proxies = {
		'http': 'http://23.27.197.200:24801',
		'http': 'http://23.27.197.201:24801',
		'http': 'http://23.27.197.202:24801',
		'http': 'http://23.27.197.203:24801',
		'http': 'http://23.27.197.204:24801',
		'http': 'http://23.27.197.205:24801',
	}
url = 'http://mynimo.com/'



class Logger(mp.Process):

	def __init__(self, data_to_log):
		mp.Process.__init__(self)
		requests_log = logging.getLogger('requests')
		self.data_to_log = data_to_log
		self.has_active_processes = True

	def run(self):
		while True:
			to_log = self.data_to_log.get()
			if to_log:
				logging.warning(json.dumps(to_log, indent=4))
			else:
				print 'Finished dumping data.'
				break
		


class Worker(mp.Process):

	def __init__(self, keywords, logger, searchType, searchCategory):
		mp.Process.__init__(self)
		self.searchType = searchType
		self.searchCategory = searchCategory
		self.logger = logger
		self.keywords = keywords
		self.current_keyword = None
		self.searchCounts = 0


	def __set_keyword(self, keyword):
		self.current_keyword = keyword


	def __conclude(self):
		print '%d searches for %s' % (self.searchCounts, self.current_keyword)


	def __request(self, page):
		to_request = url + self.searchType + '/search/'
		payload = {'q': self.current_keyword, 'page': page, 'searchType': self.searchType, 'searchCategory': self.searchCategory}
		return requests.get(to_request, params=payload, proxies=proxies, timeout=10.0)


	def __scrape(self, jobs):
		for job in jobs:
			databit = OrderedDict()
			databit['keyword'] = self.current_keyword
			databit['job_title'] = job.find_all('td')[0].find(attrs='jobTitleLink').string.encode('utf-8').strip()
			databit['company'] = job.find_all('td')[2].string.strip()
			location = job.find_all('td')[1]
			
			try:
				address = location.find(attrs='address')
				databit['location'] = address.string + ', ' + address.previous_element.previous_element.strip()
			except AttributeError:
				databit['location'] = location.string.strip()
			
			databit['short_description'] = ' '.join(job.find_next('tr').find(attrs='searchContent').text.encode('utf-8').split())

			self.logger.data_to_log.put(databit)


	def __search(self):
		page_counter = 1
		
		request = self.__request(page_counter)
		parser = BeautifulSoup(request.text)
		
		while parser.find(attrs='jobs_table'):
			print 'Executing scraper to page', page_counter, 'of', request.url, '...'
			jobs = parser.find_all(attrs={'class': 'aJobS'})
			self.searchCounts += len(jobs)
			self.__scrape(jobs)
			page_counter += 1
			request = self.__request(page_counter)
			parser = BeautifulSoup(request.text)



	def run(self):
		while True:
			front = self.keywords.get()
			if front:
				print '%s acquired %s' % (self.name, front)
				self.__set_keyword(front)
				self.__search()
				self.__conclude()
			else:
				print '%s has been poisoned' % self.name
				self.keywords.put(front)
				break



class MynimoWebScraper:
	
	def __init__(self, keywords, searchType='jobs', searchCategory=''):
		self.keywords = mp.Queue()
		self.data_to_log = mp.Queue()
		self.worker_size = mp.cpu_count()
		
		self.logger = Logger(self.data_to_log)
		self.workers = []

		for keyword in keywords:
			self.keywords.put(keyword)

		# adding poison
		self.poison = None
		self.keywords.put(self.poison)

		for i in xrange(self.worker_size):
			new_worker = Worker(self.keywords, self.logger, searchType=searchType, searchCategory=searchCategory)
			self.workers.append(new_worker)


	def run_processes(self):
		for worker in self.workers:
			worker.start()

		self.logger.start()

		for worker in self.workers:
			worker.join()

		# adding poison pill to the logger's queue of data-to-dump
		poison_pill = None
		self.logger.data_to_log.put(poison_pill)



if __name__ == '__main__':

	queries = ['python', 'ruby', 'rails',]
	s = MynimoWebScraper(queries)
	s.run_processes()