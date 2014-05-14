from bs4 import BeautifulSoup
from splinter import Browser
from urlparse import urlparse, parse_qs
import time, logging, sqlite3, multiprocessing as mp


logging.basicConfig(filename="kronos.log", level=logging.INFO, format='%(message)s')


URL = 'https://www.google.com'
KEYWORD = 'site:https://wfa.kronostm.com'
EXECUTABLE_PATH = 'C:\Python27\Lib\site-packages\chromedriver_win32\chromedriver.exe'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130401 Firefox/21.0'
DB_CONNECTION = sqlite3.connect('kronos.db')
PROXIES = [
	"--proxy=23.27.197.201:24801",
	# "--proxy=23.27.197.201:24801",
	# "--proxy=23.27.197.202:24801",
	# "--proxy=23.27.197.203:24801",
	# "--proxy=23.27.197.204:24801",
	# "--proxy=23.27.197.205:24801",
	"--proxy-type=http",
]


class GoogleScraper(mp.Process):

	def __init__(self, url_queue):
		mp.Process.__init__(self)
		self.url_queue = url_queue


	def run(self):
		browser = Browser('chrome', executable_path=EXECUTABLE_PATH, service_args=PROXIES)
		# browser = Browser('phantomjs', service_args=PROXIES, user_agent=USER_AGENT)
		with browser:
			page = 1
			browser.visit(URL)
			browser.fill("q", KEYWORD)
			browser.find_by_name("btnG").click()
			time.sleep(5)

			while True:
				time.sleep(10)
				logging.info("Page " + str(page))
				for link in browser.find_by_css("h3.r"):
					if "applicationname" in link.find_by_css("a").first["href"].lower():
						self.url_queue.put(link.find_by_css("a").first["href"])
				page += 1
				if browser.find_by_css("#pnnext"):
					browser.find_by_css("#pnnext").click()
				else:
					break
			self.url_queue.put(None)



class Verifier(mp.Process):

	def __init__(self, db_logger, url_queue):
		mp.Process.__init__(self)
		self.db_logger = db_logger
		self.url_queue = url_queue


	def __verify(self, url):
		tmp = url
		url = url.lower()
		params = parse_qs(urlparse(url).query)
		self.__check_to_db(params['applicationname'][0])


	def __check_to_db(self, application_name):
		with DB_CONNECTION:
			cur = DB_CONNECTION.cursor()
			cur.execute('SELECT URL FROM kronos_data WHERE URL LIKE "%' + application_name + '"')
			if len(cur.fetchall()) == 0:
				self.db_logger.results.put(application_name)


	def run(self):
		while True:
			if not self.url_queue.empty():
				front = self.url_queue.get()
				if front is None:
					self.url_queue.put(front)
					break
				else:
					self.__verify(front)



class DBLogger(mp.Process):

	def __init__(self, results):
		mp.Process.__init__(self)
		self.results = results


	def __add_to_db(self, application_name):
		with DB_CONNECTION:
			cur = DB_CONNECTION.cursor()
			cur.execute("INSERT INTO kronos_data (URL) VALUES('https://wfa.kronostm.com/index.jsp?applicationname=" + application_name + "')")


	def run(self):
		while True:
			if not self.results.empty():
				front = self.results.get()
				if front:
					self.__add_to_db(front)
				else:
					break
			else:
				time.sleep(5)



class Tester:

	def __init__(self):
		with DB_CONNECTION:
			cur = DB_CONNECTION.cursor()
			cur.execute("DROP TABLE IF EXISTS kronos_data")
			cur.execute("CREATE TABLE kronos_data(URL TEXT, Date_Processed TEXT, Team TEXT)")

		self.url_queue = mp.Queue()
		self.results = mp.Queue()
		self.google_scraper = GoogleScraper(self.url_queue)
		self.db_logger = DBLogger(self.results)
		self.verifiers = []

		for i in xrange(2):
			self.verifiers.append(Verifier(self.db_logger, self.url_queue))


	def run(self):
		self.google_scraper.start()
		self.db_logger.start()

		for verifier in self.verifiers:
			verifier.start()




if __name__ == "__main__":
	tester = Tester()
	tester.run()