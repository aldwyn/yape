import mynimo_web_scraper
import splinter


SERVICE_ARGS = [
    '--proxy=23.27.197.200:24801',
    '--proxy=23.27.197.201:24801',
    '--proxy=23.27.197.202:24801',
    '--proxy=23.27.197.203:24801',
    '--proxy=23.27.197.204:24801',
    '--proxy=23.27.197.205:24801',
    '--proxy-type=http',
]



class Worker(mynimo_web_scraper.Worker):

	def __init__(self, keywords, logger, searchType, searchCategory):
		mynimo_web_scraper.Worker.__init__(self, keywords, logger, searchType, searchCategory)


	def __search(self):
		browser = splinter.Browser('phantomjs', service_args=SERVICE_ARGS)
		with browser:
			browser.visit(mynimo_web_scraper.URL)
			browser.fill('q', self.current_keyword)
			browser.select('searchType', self.searchType)
			browser.select('searchCategory', self.searchCategory)
			
			go_search_button = browser.find_by_id('searchButton')
			go_search_button.click()
			
			while True:
				print 'Executing scraper to', browser.url, '...'
				parser = mynimo_web_scraper.BeautifulSoup(browser.html)
				jobs = parser.find_all(attrs={'class': 'aJobS'})
				self.searchCounts += len(jobs)
				self.__scrape(jobs)
				try:
					browser.click_link_by_text('Next')
				except splinter.exceptions.ElementDoesNotExist:
					break



class MynimoWebScraper(mynimo_web_scraper.MynimoWebScraper):
	
	def __init__(self):
		mynimo_web_scraper.MynimoWebScraper.__init__(self)


	def __add_workers(self):
		for i in xrange(self.worker_size):
			new_worker = Worker(self.keywords, self.logger, searchType=self.searchType, searchCategory=self.searchCategory)
			self.workers.append(new_worker)




if __name__ == '__main__':

	queries = ['java', 'php', 'python', 'perl','ada']
	s = MynimoWebScraper()
	s.set_query_params(queries)
	s.run()