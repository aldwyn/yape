from bs4 import BeautifulSoup
from collections import OrderedDict
import requests
import json
import cProfile

class Scraper:
	
	def __init__(self, url, params):
		self.proxies = {'http': 'http://23.27.197.200:24801'}
		self.url = url + params['searchType'] + '/search/'
		self.params = params


	def __request(self, keyword,  page_counter):
		self.params['q'] = keyword
		self.params['page'] = page_counter
		return requests.get(self.url, params=self.params, proxies=self.proxies).text


	def __scrape(self, jobs):
		for job in jobs:
			databit = OrderedDict()
			databit['keyword'] = self.params['q']
			databit['job_title'] = job.find_all('td')[0].find(attrs='jobTitleLink').string
			databit['company'] = job.find_all('td')[2].string.strip()
			location = job.find_all('td')[1]
			try:
				address = location.find(attrs='address')
				databit['location'] = address.string + ', ' + address.previous_element.previous_element.strip()
			except AttributeError:
				databit['location'] = location.string.strip()
			
			databit['short_description'] = ' '.join(job.find_next('tr').find(attrs='searchContent').text.encode('utf-8').split())
			self.__append_to_json(databit)


	def __append_to_json(self, to_write):
		with open('data.json', 'a') as output:
			output.write(json.dumps(to_write, indent=4) + ',\n')
		output.close()


	def execute(self):
		page_counter = 1
		
		for keyword in self.params['keywords']:
			parser = BeautifulSoup(self.__request(keyword, page_counter))
			
			while parser.find(attrs='no_entries') is None:
				print 'Executing scraper to page ' + str(page_counter) + ' of ' + self.url + '?q=' + keyword +' ...'
				jobs = parser.find_all(attrs={'class': 'aJobS'})
				self.__scrape(jobs)
				page_counter += 1
				parser = BeautifulSoup(self.__request(keyword, page_counter))

			page_counter = 1

		print 'Finished scraping data from site. See output file.'




if __name__ == '__main__':

	payload = {'keywords': ['bursing'], 'searchType': 'jobs', 'searchCategory': ''}
	s = Scraper('http://cebu.mynimo.com/', payload)

	cProfile.run('s.execute()')
	# s.execute()