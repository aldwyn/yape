from bs4 import BeautifulSoup
from splinter import Browser
import multiprocessing, time, logging, sqlite3, sys
from urlparse import urlparse, parse_qs

logging.basicConfig(filename="kronos.log", level=logging.INFO, format='%(message)s')
con = sqlite3.connect('kronos_sites.db')
with con:
	cur = con.cursor()
	cur.execute("DROP TABLE IF EXISTS kronos_data")
	cur.execute("CREATE TABLE kronos_data(URL TEXT, Date_Processed TEXT, Team TEXT)")

PROXIES = [
	"--proxy=23.27.197.201:24801",
	# "--proxy=23.27.197.201:24801",
	# "--proxy=23.27.197.202:24801",
	# "--proxy=23.27.197.203:24801",
	# "--proxy=23.27.197.204:24801",
	# "--proxy=23.27.197.205:24801",
	"--proxy-type=http",
]

class GoogleScraper(multiprocessing.Process):

	def __init__(self, url, keyword, queue):
		multiprocessing.Process.__init__(self)
		self.url = url
		self.keyword = keyword
		self.queue = queue


	def run(self):
		browser = Browser('chrome', executable_path="C:\Python27\Lib\site-packages\chromedriver_win32\chromedriver.exe", service_args=PROXIES)
		# browser = Browser('phantomjs', service_args=PROXIES, user_agent="Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130401 Firefox/21.0")
		with browser:
			page = 1
			browser.visit(self.url)
			browser.fill("p", self.keyword)
			browser.find_by_id("search-submit").click()

			while True:
				time.sleep(10)
				logging.info("Page " + str(page))
				for link in browser.find_by_css("div.res"):
					if "applicationname" in link.find_by_css("a").first["href"].lower():
						self.queue.put(link.find_by_css("a").first["href"])
				page += 1
				if browser.find_by_css("#pg-next"):
					browser.find_by_css("#pg-next").click()
				else:
					break
			self.queue.put(None)


class DBLogger(multiprocessing.Process):

	def __init__(self, queue):
		multiprocessing.Process.__init__(self)
		self.queue = queue

	def __verify(self, url):
		url = url.lower()
		params = parse_qs(urlparse(url).query)
		self.__check_to_db(params['applicationname'][0])

	def __check_to_db(self, application_name):
		link = "https://wfa.kronostm.com/index.jsp?applicationname=" + application_name
		with con:
			cur.execute('SELECT URL FROM kronos_data WHERE URL LIKE "' + link + '"')
			app_names_in_db = cur.fetchall()
			if len(app_names_in_db) == 0:
				cur.execute("INSERT INTO kronos_data(URL) VALUES('" + link + "')")
				
	def run(self):
		while True:
			if not self.queue.empty():
				link = self.queue.get()
				if link is None:
					break
				else:
					self.__verify(link)
			else:
				time.sleep(10)


if __name__ == "__main__":
	url_queue = multiprocessing.Queue()
	url = "https://www.yahoo.com"
	keyword = "site:https://wfa.kronostm.com"
	gs = GoogleScraper(url, keyword, url_queue)
	gs.start()
	logger = DBLogger(url_queue)
	logger.start()