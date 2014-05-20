import splinter, requests, time, sys, sqlite3, json, csv, collections, multiprocessing as mp
from bs4 import BeautifulSoup


EXECUTABLE_PATH = 'C:\Python27\Lib\site-packages\chromedriver_win32\chromedriver.exe'
PROXIES = [
	"--proxy=23.27.197.201:24801",
	# "--proxy=23.27.197.201:24801",
	# "--proxy=23.27.197.202:24801",
	# "--proxy=23.27.197.203:24801",
	# "--proxy=23.27.197.204:24801",
	# "--proxy=23.27.197.205:24801",
	"--proxy-type=http",
]
REQUEST_PROXIES = {
	'http': 'http://23.27.197.200:24801',
	# 'http': 'http://23.27.197.201:24801',
	# 'http': 'http://23.27.197.202:24801',
	# 'http': 'http://23.27.197.203:24801',
	# 'http': 'http://23.27.197.204:24801',
	# 'http': 'http://23.27.197.205:24801',
}
SITES = [
	'https://wfa.kronostm.com/index.jsp?applicationname=allonereqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=bayareahospitalreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=bcnepareqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=beaverdamcommunityhospitalktmdreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=brandywineseniorlivingreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=burgerkingcorporationktmdreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=centralstatesreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=celadongroupktmdreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=century21ktmdreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=charmingcharliektmdreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=connextionsktmdreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=druryhotelsreqexternalseekersite',
	'https://wfa.kronostm.com/index.jsp?applicationname=extendicarereqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=famousdavesreqexternalseekersite',
	'https://wfa.kronostm.com/index.jsp?applicationname=finishlinektmdreqext',
]



class CSVLogger(mp.Process):

	def __init__(self, data_queue):
		mp.Process.__init__(self)
		self.data_queue = data_queue


	def __log_to_csv(self, databit):
		to_csv = collections.OrderedDict([
			('job_title', databit['job_title'].encode('utf-8')),
			('job_description', json.dumps(databit['job_description'].encode('utf-8'))),
			('company_name', databit['company_name'].encode('utf-8')),
			('address', databit['address'].encode('utf-8')),
		])

		with open('kronos.csv', 'a') as csv_connection:
			data_writer = csv.DictWriter(csv_connection, to_csv.keys())
			data_writer.writerow(to_csv)


	def run(self):
		while True:
			if not self.data_queue.empty():
				front = self.data_queue.get()
				if front:
					self.__log_to_csv(front)
				else:
					break
			else:
				time.sleep(5)


class Scraper(mp.Process):

	def __init__(self, posting_id_queue, csv_logger):
		mp.Process.__init__(self)
		self.posting_id_queue = posting_id_queue
		self.csv_logger = csv_logger


	def __browse_all(self, site, company_name, browser):
		pages = browser.find_by_name('pagesel_select')[0].find_by_tag('option')

		for i in xrange(len(pages)):
			pagination = browser.find_by_name('pagesel_select')[0]
			pagination.click()
			pagination.find_by_tag('option')[i].click()

			parser = BeautifulSoup(browser.html)
			table_rows = parser.find_all('tr')
			del table_rows[0]

			for job in table_rows:
				td = job.find_all('td')
				tmp = td[1].find(attrs='massActionLabel')
						
				to_put = {
					'url': site,
					'posting_id': tmp.get('for'),
					'job_title': tmp.get_text().strip(),
					'company_name': company_name.replace('Welcome to', '').strip(),
					'address': td[len(td)-2].get_text().strip(),
				}
				self.posting_id_queue.put(to_put)


	def run(self):
		with splinter.Browser('chrome', executable_path=EXECUTABLE_PATH, service_args=PROXIES) as browser:
			for site in SITES:
				browser.visit(site)
				company_name = browser.find_by_css('#welcomeMessage > h1').value
				
				menu_bar = browser.find_by_css('#menuBar > div.menuItemNoSub:last-child > a')

				if menu_bar:
					menu_bar.click()
					self.__browse_all(site, company_name, browser)
				else:
					for menu_item_no_sub in browser.find_by_css('#tabHeader > ul > li > a'):
						if menu_item_no_sub.value.strip() == 'By Location':
							menu_item_no_sub.click()
							browser.find_by_css('#oneClickLocation > div > a').click()
							self.__browse_all(site, company_name, browser)
							break

		self.posting_id_queue.put(None)


class Worker(mp.Process):

	def __init__(self, index, posting_id_queue, csv_logger):
		mp.Process.__init__(self)
		self.index = index
		self.posting_id_queue = posting_id_queue
		self.csv_logger = csv_logger
		self.curr_app_url = None


	def set_app_url(self, curr_app_url):
		self.curr_app_url = curr_app_url


	def __request(self, url, posting_id):
		to_request = url + '&seq=jobDetails&posting_id=' + str(posting_id)
		print to_request
		return requests.get(to_request, proxies=REQUEST_PROXIES)


	def __visit(self, databit):
		request = self.__request(databit['url'], databit['posting_id'])
		parser = BeautifulSoup(request.text)
		try:
			databit['job_description'] = parser.find_all(attrs={'class': 'formattedContent'})[0].text.strip()
		except:
			databit['job_description'] = None
		self.csv_logger.data_queue.put(databit)


	def run(self):
		while True:
			if not self.posting_id_queue.empty():
				front = self.posting_id_queue.get()
				if front:
					self.__visit(front)
				else:
					self.posting_id_queue.put(front)
					break
			else:
				time.sleep(5)



class Tester:

	def __init__(self):
		self.data_queue = mp.Queue()
		self.posting_id_queue = mp.Queue()
		self.csv_logger = CSVLogger(self.data_queue)
		self.scraper = Scraper(self.posting_id_queue, self.csv_logger)
		self.workers = [Worker(i, self.posting_id_queue, self.csv_logger) for i in xrange(mp.cpu_count())]


	def run(self):
		self.scraper.start()

		for worker in self.workers:
			worker.start()

		self.csv_logger.start()

		for worker in self.workers:
			worker.join()

		self.csv_logger.data_queue.put(None)




if __name__ == '__main__':
	tester = Tester()
	tester.run()
