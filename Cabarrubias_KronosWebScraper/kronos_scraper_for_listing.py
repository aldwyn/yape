import splinter, requests, time, logging, sys, multiprocessing as mp
from bs4 import BeautifulSoup


logging.basicConfig(filename="kronos.log", level=logging.INFO, format='%(message)s')
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
REQUEST_POXIES = {
	'http': 'http://23.27.197.200:24801',
	# 'http': 'http://23.27.197.201:24801',
	# 'http': 'http://23.27.197.202:24801',
	# 'http': 'http://23.27.197.203:24801',
	# 'http': 'http://23.27.197.204:24801',
	# 'http': 'http://23.27.197.205:24801',
}
SITES = [
	# 'https://wfa.kronostm.com/index.jsp?applicationname=allonereqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=bayareahospitalreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=bcnepareqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=beaverdamcommunityhospitalktmdreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=brandywineseniorlivingreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=burgerkingcorporationktmdreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=centralstatesreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=celadongroupktmdreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=century21ktmdreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=charmingcharliektmdreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=connextionsktmdreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=druryhotelsreqexternalseekersite',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=extendicarereqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=famousdavesreqexternalseekersite',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=finishlinektmdreqext',
]



class Scraper(mp.Process):

	def __init__(self, posting_id_queue):
		mp.Process.__init__(self)
		self.posting_id_queue = posting_id_queue


	def run(self):
		browser = splinter.Browser('chrome', executable_path=EXECUTABLE_PATH, service_args=PROXIES)
		with browser:
			for site in SITES:
				browser.visit(site)
				company_name = browser.find_by_css('#welcomeMessage > h1').value
				by_location = None

				for menu_item_no_sub in browser.find_by_css('#tabHeader > ul > li > a'):
					if menu_item_no_sub.value.strip() == 'By Location':
						menu_item_no_sub.click()
						browser.find_by_css('#oneClickLocation > div > a').click()

						parser = BeautifulSoup(browser.html)
						for job in parser.find_all('tr'):
							tmp = job.find_all('label', class_='massActionLabel')[0]
							to_put = {
								'url': site,
								'job_title': tmp.get_text(),
								'posting_id': tmp.get('for'),
								'company_name': company_name,
								'address': job.find(attrs='cityStateCell').get_text(),
							}
							self.posting_id_queue.put(to_put)

						break

			self.posting_id_queue.put(None)


class Worker(mp.Process):

	def __init__(self, index, posting_id_queue):
		mp.Process.__init__(self)
		self.index = index
		self.posting_id_queue = posting_id_queue
		self.curr_app_url = None


	def set_app_url(self, curr_app_url):
		self.curr_app_url = curr_app_url


	def __request(self, url, posting_id):
		to_request = url + 'seq=jobDetails&posting_id=' + str(posting_id)
		return requests.get(to_request, proxies=REQUEST_PROXIES)


	def __visit(self, databit):
		# request = self.__request(databit['url'], databit['posting_id'])
		# parser = BeautifulSoup(request.text)
		logging.warning(databit['url'] + str(databit['posting_id']))



	def run(self):
		while True:
			if not self.posting_id_queue.empty():
				front = self.posting_id_queue.get()
				if front:
					# self.__visit(front)
					to_log = str(self.index) + ': ' + str(front['posting_id']) + str(front['company_name'])
					logging.warning(to_log)
				else:
					self.posting_id_queue.put(front)
					break
			else:
				time.sleep(5)



class Tester:

	def __init__(self):
		self.posting_id_queue = mp.Queue()
		# self.csv_logger = CSVLogger()
		self.scraper = Scraper(self.posting_id_queue)
		self.workers = [Worker(i, self.posting_id_queue) for i in xrange(4)]


	def run(self):
		self.scraper.start()

		for worker in self.workers:
			worker.start()




if __name__ == '__main__':
	tester = Tester()
	tester.run()
