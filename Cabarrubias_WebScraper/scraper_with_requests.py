import mynimo_web_scraper
import requests


PROXIES = {
	'http': 'http://23.27.197.200:24801',
	'http': 'http://23.27.197.201:24801',
	'http': 'http://23.27.197.202:24801',
	'http': 'http://23.27.197.203:24801',
	'http': 'http://23.27.197.204:24801',
	'http': 'http://23.27.197.205:24801',
}



class Worker(mynimo_web_scraper.Worker):

	def __init__(self, keywords, logger, searchType, searchCategory):
		mynimo_web_scraper.Worker.__init__(self, keywords, logger, searchType, searchCategory)


	def __request(self, page):
		to_request = mynimo_web_scraper.URL + self.searchType + '/search/'
		payload = {'q': self.current_keyword, 'page': page, 'searchType': self.searchType, 'searchCategory': self.searchCategory}
		return requests.get(to_request, params=payload, proxies=PROXIES, timeout=10.0)


	def __search(self):
		page_counter = 1
		
		request = self.__request(page_counter)
		parser = mynimo_web_scraper.BeautifulSoup(request.text)
		
		while parser.find(attrs='jobs_table'):
			print 'Executing scraper to page', page_counter, 'of', request.url, '...'
			jobs = parser.find_all(attrs={'class': 'aJobS'})
			self.searchCounts += len(jobs)
			self.__scrape(jobs)
			page_counter += 1
			request = self.__request(page_counter)
			parser = mynimo_web_scraper.BeautifulSoup(request.text)



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