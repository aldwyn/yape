from bs4 import BeautifulSoup
from splinter import Browser
from collections import OrderedDict
import multiprocessing, time, json, csv

PROXIES = [
	'--proxy=23.27.197.200:24801',
	# '--proxy=23.27.197.201:24801',
	# '--proxy=23.27.197.202:24801',
	# '--proxy=23.27.197.203:24801',
	# '--proxy=23.27.197.204:24801',
	# '--proxy=23.27.197.205:24801',
	'--proxy-type=http',
]

URL_LIST = [
	# 'https://wfa.kronostm.com/index.jsp?applicationname=bevmononreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=bfsaulnonreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=bigynonreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=buehlersnonreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=burgerkingcorporationnonreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=cambridgehealthcarenonreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=carmaxnonreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=century21nonreqext',
	# 'https://wfa.kronostm.com/index.jsp?applicationname=charmingcharlienonreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=cinemarknonreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=costcononreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=covenantdovenonreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=druryhotelsnonreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=englefieldoilnonreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=famousdavesnonreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=finishlinenonreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=freshgrocernonreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=geminimotortransportnonreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=genescoindistributionnonreqext',
]

class KronosScraper:

	def __init__(self):
		results = multiprocessing.Queue()
		url_queue = multiprocessing.Queue()
		for i in URL_LIST:
			url_queue.put(i)
		url_queue.put(None)
		workers = []

		for i in range(multiprocessing.cpu_count()):
			worker = Worker(url_queue, results)
			workers.append(worker)

		for worker in workers:
			worker.start()

		writer = CSVWriter(results)
		writer.start()

		for worker in workers:
			worker.join()

		results.put(None)


class Worker(multiprocessing.Process):

	def __init__(self, url_queue, results):
		multiprocessing.Process.__init__(self)
		self.results = results
		self.url_queue = url_queue

	def run(self):
		while True:
			link = self.url_queue.get()
			if link is None:
				self.url_queue.put(link)
				break
			else:
				self.__scrape(link)

	def __scrape(self, landing_page):
		browser = Browser('chrome', executable_path='C:\Python27\Lib\site-packages\chromedriver_win32\chromedriver.exe', service_args=PROXIES)
		# browser = Browser('phantomjs', service_args=PROXIES, user_agent='Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130401 Firefox/21.0')
		with browser:
			template1 = True
			browser.visit(landing_page)
			time.sleep(2)

			nav = [x for x in browser.find_by_css('a.nav') if (x.text == 'Jobs by Location' or x.text == 'By Location')]
			if len(nav) > 0:
				nav[0].click()
			else:
				template1 = False
			link = browser.url
			state_index = 1
			city_index = 1

			while True:
				browser.visit(link)
				if not template1:
					nav = browser.find_by_css('#tabHeader')
					nav = nav.find_by_css('a')
					nav[1].click()
				states = browser.find_by_name('search.stateList.value')
				state_list = states.find_by_tag('option')
				print state_list[state_index].text
				state_list[state_index].click()
				if state_list[state_index].text != 'choose one...':
					element = 'cityList_' + state_list[state_index].text
					cities = browser.find_by_id(element)
					city_list = cities.find_by_tag('option')
					city_list[city_index].click()
					if city_list[city_index].text != 'choose one...':
						print city_list[city_index].text, state_list[state_index].text
						browser.find_by_id('cityStateSearch').click()
						links = None
						try:
							links = browser.find_by_css('a.withBubble')
						except:
							pass

						if len(links) > 0:
							for i in links:
								b = Browser('chrome', executable_path='C:\Python27\Lib\site-packages\chromedriver_win32\chromedriver.exe', service_args=PROXIES)
								# b = Browser('phantomjs', service_args=PROXIES, user_agent='Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130401 Firefox/21.0')
								with b:
									b.visit(i['href'])
									self.__navigate_pages(b)
						else:
							self.__navigate_pages(browser)
					city_index += 1
					if city_index == len(city_list):
						city_index = 0
						state_index += 1
						if state_index == len(state_list):
							break
				else:
					state_index += 1

	def __navigate_pages(self, browser):

		job_counter = 0
		while True:
			jobList = browser.find_by_css('ul.linkList')
			jobs = jobList[0].find_by_tag('a')
			jobs = [jobs[x] for x in range(len(jobs)) if x % 2 != 0]
			jobs[job_counter].click()
			self.__extract_data(browser.html.encode('utf-8'))
			job_counter += 1
			browser.back()
			if job_counter == len(jobs):
				break

	def __extract_data(self, text):

		soup = BeautifulSoup(text)
		try:
			content = soup.find('div', attrs = {'id' : 'Slot_0_3_3_10'})
			job_title = content.find('h1').text
			sidebar = soup.find(attrs = 'sidebar')
			company_name = sidebar.find(attrs = 'inline').find('strong').text
			address = sidebar.findAll('span', attrs = {'class' : 'field readOnly'})
			try:
				street = address[0].text
				city = address[1].text
				state = address[2].text
				zipcode = address[3].text
				address = street + ', ' +  state + ', ' + city + ', ' + zipcode
			except:
				address = ""
			try:
				description = soup.findAll(attrs = 'formattedContent')[0].text.strip()
			except:
				description = ""

			d = OrderedDict()
			d['job_title'] = job_title.encode('utf-8').strip()
			description = json.dumps(description.encode('utf-8').strip())
			d['job_description'] = description.replace("\u00a0", '')
			d['company_name'] = company_name.encode('utf-8').strip()
			d['address'] = address.encode('utf-8').strip()
			self.results.put(d)
		except:
			pass


class CSVWriter(multiprocessing.Process):

	def __init__(self, results):
		multiprocessing.Process.__init__(self)
		self.results = results

	def run(self):
		while True:
			if not self.results.empty():
				d = self.results.get()
				if d is None:
					break
				with open('KronosData_DropDown.csv', 'a') as f:
				    w = csv.DictWriter(f, d.keys())
				    w.writerow(d)
			else:
				time.sleep(5)


if __name__ == '__main__':
	scraper = KronosScraper()