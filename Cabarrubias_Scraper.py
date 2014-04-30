from bs4 import BeautifulSoup
from collections import OrderedDict
import requests
import json
import cProfile

class MynimoWebScraper:
	
	def __init__(self):
		self.proxies = {
				'http': 'http://23.27.197.200:24801',
				'http': 'http://23.27.197.201:24801',
				'http': 'http://23.27.197.202:24801',
				'http': 'http://23.27.197.203:24801',
				'http': 'http://23.27.197.204:24801',
				'http': 'http://23.27.197.205:24801',
			}
		self.url = 'http://mynimo.com/'


	def __request(self, q,  page, searchType, searchCategory):
		to_request = self.url + searchType + '/search/'
		payload = {'q': q, 'page': page, 'searchType': searchType, 'searchCategory': searchCategory}
		return requests.get(to_request, params=payload, proxies=self.proxies, timeout=10.0)


	def __scrape(self, jobs, keyword):
		for job in jobs:
			databit = OrderedDict()
			databit['keyword'] = keyword
			databit['job_title'] = job.find_all('td')[0].find(attrs='jobTitleLink').string
			databit['company'] = job.find_all('td')[2].string.strip()
			location = job.find_all('td')[1]
			
			try:
				address = location.find(attrs='address')
				databit['location'] = address.string + ', ' + address.previous_element.previous_element.strip()
			except AttributeError:
				databit['location'] = location.string.strip()
			
			databit['short_description'] = ' '.join(job.find_next('tr').find(attrs='searchContent').text.encode('utf-8').split())

			with open('data.json', 'a') as output:
				output.write(json.dumps(databit, indent=4))
			
			print 'EXTRACTED:\t' + databit['job_title'].encode('utf-8')


	def search(self, keywords, searchType='jobs', searchCategory=''):
		page_counter = 1

		for keyword in keywords:
			request = self.__request(keyword, page_counter, searchType, searchCategory)
			parser = BeautifulSoup(request.text)
			
			while parser.find(attrs='jobs_table'):
				print 'Executing scraper to page', page_counter, 'of', self.url + '?q=' + keyword, '...'
				jobs = parser.find_all(attrs={'class': 'aJobS'})
				self.__scrape(jobs, keyword)
				page_counter += 1
				request = self.__request(keyword, page_counter, searchType, searchCategory)
				parser = BeautifulSoup(request.text)

			page_counter = 1

		print 'Finished scraping data from site. See output file.'




if __name__ == '__main__':

	s = MynimoWebScraper()
	s.search(['nursing', 'java'])