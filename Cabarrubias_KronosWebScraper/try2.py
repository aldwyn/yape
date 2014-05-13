from bs4 import BeautifulSoup
from splinter import Browser
import multiprocessing, time, logging


class GoogleScraper:
	def __init__(self):
		self.proxies = [
			"--proxy=23.27.197.201:24801",
			# "--proxy=23.27.197.201:24801",
			# "--proxy=23.27.197.202:24801",
			# "--proxy=23.27.197.203:24801",
			# "--proxy=23.27.197.204:24801",
			# "--proxy=23.27.197.205:24801",
			"--proxy-type=http",
		]
		logging.basicConfig(filename="urls.log", level=logging.INFO, format='%(message)s')

	def scraper(self, url, keyword):
		# browser = Browser('chrome', executable_path="C:\Python27\Lib\site-packages\chromedriver.exe", service_args=self.proxies)
		browser = Browser('phantomjs', service_args=self.proxies, user_agent="Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130401 Firefox/21.0")
		with browser:
			page = 0
			browser.visit(url)
			browser.fill("q", keyword)
			browser.find_by_name("btnG").click()
			time.sleep(5)
			while page < 10:	
				time.sleep(5)
				links = browser.find_by_css("h3.r")
				for link in links:
					url = link.find_by_css("a").first["href"]
					logging.info(url)
					print url
				page += 1
				text1 = "Page " + str(page) + " finished.\n"
				logging.info(text1)
				print text1
				browser.find_by_css("#pnnext").click()
				# a = [x for x in browser.find_by_css("a") if x.text == "Next"]
				# browser.visit(a[0]['href'])

url = "https://www.google.com"
keyword = "site:https://wfa.kronostm.com"
gs = GoogleScraper()
gs.scraper(url, keyword)