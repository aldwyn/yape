from bs4 import BeautifulSoup
from collections import OrderedDict
import json, logging, multiprocessing as mp

# global variables
logging.basicConfig(filename='scraped.json', level=logging.WARNING, format='%(message)s')
URL = 'http://cebu.mynimo.com/'



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


	def __scrape(self, jobs):
		for job in jobs:
			databit = OrderedDict()
			databit['keyword'] = self.current_keyword
			databit['job_title'] = job.find_all('td')[0].find(attrs='jobTitleLink').text.encode('utf-8').strip()
			databit['company'] = job.find_all('td')[2].text.strip()
			location = job.find_all('td')[1]
			
			try:
				address = location.find(attrs='address')
				databit['location'] = address.text + ', ' + address.previous_element.previous_element.strip()
			except:
				databit['location'] = location.text.strip()
			
			databit['short_description'] = ' '.join(job.find_next('tr').find(attrs='searchContent').text.encode('utf-8').split())

			self.logger.data_to_log.put(databit)


	def __search(self):
		pass


	def run(self):
		while True:
			front = self.keywords.get()
			if front:
				print '%s acquired %s' % (self.name, front)
				self.__set_keyword(front)
				self.__search()
				self.__conclude()
				self.searchCounts = 0
			else:
				print '%s has been poisoned' % self.name
				self.keywords.put(front)
				break



class MynimoWebScraper:
	
	def __init__(self):
		self.keywords = mp.Queue()
		self.data_to_log = mp.Queue()
		self.worker_size = mp.cpu_count()
		self.searchType = None
		self.searchCategory = None
		
		self.logger = Logger(self.data_to_log)
		self.workers = []


	def set_query_params(self, keywords, searchType='jobs', searchCategory=''):
		self.searchType = searchType
		self.searchCategory = searchCategory

		for keyword in keywords:
			self.keywords.put(keyword)
		
		# adding poison
		self.poison = None
		self.keywords.put(self.poison)

		self.__add_workers()


	def __add_workers(self):
		pass

	
	def run(self):
		print 'Scraper running...'

		for worker in self.workers:
			worker.start()

		self.logger.start()

		for worker in self.workers:
			worker.join()

		# adding poison pill to the logger's queue of data-to-dump
		poison_pill = None
		self.logger.data_to_log.put(poison_pill)