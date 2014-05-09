from bs4 import BeautifulSoup
from collections import OrderedDict
import json, logging, multiprocessing as mp
import splinter

# global variables
logging.basicConfig(filename='scraped.json', level=logging.WARNING, format='%(message)s')
service_args = [
    '--proxy=23.27.197.200:24801',
    '--proxy=23.27.197.201:24801',
    '--proxy=23.27.197.202:24801',
    '--proxy=23.27.197.203:24801',
    '--proxy=23.27.197.204:24801',
    '--proxy=23.27.197.205:24801',
    '--proxy-type=http',
]
url = 'http://cebu.mynimo.com/'



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
		browser = splinter.Browser('phantomjs', service_args=service_args)
		with browser:
			browser.visit(url)
			browser.fill('q', self.current_keyword)
			browser.select('searchType', self.searchType)
			browser.select('searchCategory', self.searchCategory)
			
			go_search_button = browser.find_by_id('searchButton')
			go_search_button.click()
			
			while True:
				print 'Executing scraper to', browser.url, '...'
				parser = BeautifulSoup(browser.html)
				jobs = parser.find_all(attrs={'class': 'aJobS'})
				self.searchCounts += len(jobs)
				self.__scrape(jobs)
				try:
					browser.click_link_by_text('Next')
				except splinter.exceptions.ElementDoesNotExist:
					break


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
		
		self.logger = Logger(self.data_to_log)
		self.workers = []


	def set_query_params(self, keywords, searchType='jobs', searchCategory=''):
		for keyword in keywords:
			self.keywords.put(keyword)
		
		# adding poison
		self.poison = None
		self.keywords.put(self.poison)

		for i in xrange(self.worker_size):
			new_worker = Worker(self.keywords, self.logger, searchType=searchType, searchCategory=searchCategory)
			self.workers.append(new_worker)

	
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



if __name__ == '__main__':

	queries = ['java', 'php', 'python', 'perl','ada']
	s = MynimoWebScraper()
	s.set_query_params(queries)
	s.run()