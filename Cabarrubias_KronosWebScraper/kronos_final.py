import splinter, requests, time, sys, sqlite3, json, csv, collections, multiprocessing as mp
from urlparse import urlparse, parse_qs
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
# SITES = [
# 	'https://wfa.kronostm.com/index.jsp?applicationname=allonereqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=bayareahospitalreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=bcnepareqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=beaverdamcommunityhospitalktmdreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=bevmononreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=bfsaulnonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=bigynonreqext',
# 	# 'https://wfa.kronostm.com/index.jsp?applicationname=bilollcdsirat',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=brandywineseniorlivingreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=buehlersnonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=burgerkingcorporationktmdreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=burgerkingcorporationnonreqext',
# 	# 'https://wfa.kronostm.com/index.jsp?applicationname=burgerkingcorporationnonreqint',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=cambridgehealthcarenonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=carmaxnonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=celadongroupktmdreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=centralstatesreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=century21ktmdreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=century21nonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=charmingcharliektmdreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=charmingcharlienonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=cinemarknonreqext',
# 	# 'https://wfa.kronostm.com/index.jsp?applicationname=communitybloodcentersoffloridaktmdreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=connextionsktmdreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=costcononreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=covenantdovenonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=craighospitalreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=druryhotelsnonreqext',
# 	# 'https://wfa.kronostm.com/index.jsp?applicationname=druryhotelsreqexternalseekersite',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=druryhotelsreqinternalseekersite',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=englefieldoilnonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=extendicarereqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=famousdavesnonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=famousdavesreqexternalseekersite',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=finishlinektmdreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=finishlinenonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=freshgrocernonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=geminimotortransportnonreqext',
# 	'https://wfa.kronostm.com/index.jsp?applicationname=genescoindistributionnonreqext',
# ]

SITES = [
	# 'https://wfa.kronostm.com/index.jsp?applicationname=bevmononreqext',
	'https://wfa.kronostm.com/index.jsp?applicationname=carmaxnonreqext',
]


class CSVLogger(mp.Process):

	def __init__(self, data_queue):
		mp.Process.__init__(self)
		self.data_queue = data_queue


	def __log_to_csv(self, databit):
		to_csv = collections.OrderedDict([
			('job_title', databit['job_title']),
			('job_description', json.dumps(databit['job_description'])),
			('company_name', databit['company_name']),
			('address', databit['address']),
		])

		with open('kronos_final.csv', 'a') as csv_connection:
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


	def __navigate_pages(self, site, company_name, request_text):
		parser = BeautifulSoup(request_text)
		jobs = parser.find_all('li')
		for job in jobs:
			link = job.find('a')
			params = parse_qs(urlparse(link.get('href')).query)
			to_put = {
				'url': site,
				'dropdown': True,
				'location_id': params['LOCATION_ID'][0],
				'posting_id': params['POSTING_ID'][0],
				'company_name': company_name.replace('Welcome to', '').strip(),
			}
			self.posting_id_queue.put(to_put)


	def __browse_all_for_dropdown(self, site, company_name, browser, is_retarded=False):
		state_index = 1
		city_index = 1

		while True:
			if is_retarded:
				nav = browser.find_by_css('#tabHeader')
				nav = nav.find_by_css('a')
				nav[1].click()
			states = browser.find_by_name('search.stateList.value')
			state_list = states.find_by_tag('option')

			print state_list[state_index].text
			print state_index, city_index

			while not state_list[state_index]:
				time.sleep(2)

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
							r = requests.get(i['href'])
							self.__navigate_pages(site, company_name, r.text)
					else:
						self.__navigate_pages(site, company_name, browser.html)
				city_index += 1
				if city_index == len(city_list):
					city_index = 1
					state_index += 1
					if state_index == len(state_list):
						break
			else:
				state_index += 1
			browser.back()


	def __browse_all_for_listing(self, site, company_name, browser):
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
				address = td[len(td)-2].get_text().strip()
						
				to_put = {
					'url': site,
					'dropdown': False,
					'posting_id': tmp.get('for'),
					'job_title': tmp.get_text().strip(),
					'company_name': company_name.replace('Welcome to', '').strip(),
					'address': address,
				}
				self.posting_id_queue.put(to_put)


	def run(self):
		with splinter.Browser('chrome', executable_path=EXECUTABLE_PATH, service_args=PROXIES) as browser:
			for site in SITES:
				browser.visit(site)
				try:
					company_name = browser.find_by_css('#welcomeMessage > h1').value
				except:
					company_name = browser.find_by_css('#Slot_0_3_3_9 > h1').value

				menu_bar = browser.find_by_css('#menuBar > div.menuItemNoSub')

				if menu_bar:
					if menu_bar[len(menu_bar)-1].find_by_css('a')[0].value.strip() == 'All Open Jobs':
						menu_bar[len(menu_bar)-1].click()
						self.__browse_all_for_listing(site, company_name, browser)
					else:
						for bar in menu_bar:
							bar_name = bar.find_by_tag('a')[0].value.strip()
							if bar_name == 'Jobs by Location' or bar_name == 'By Location':
								bar.click()
								self.__browse_all_for_dropdown(site, company_name, browser)
								break
				else:
					for menu_item_no_sub in browser.find_by_css('#tabHeader > ul > li > a'):
						if menu_item_no_sub.value.strip() == 'By Location':
							menu_item_no_sub.click()
							browser.find_by_css('#oneClickLocation > div > a').click()
							self.__browse_all_for_listing(site, company_name, browser)
							break
						elif menu_item_no_sub.value.strip() == 'Apply to a Location Near You':
							menu_item_no_sub.click()
							self.__browse_all_for_dropdown(site, company_name, browser, is_retarded=True)
							break

		self.posting_id_queue.put(None)



class Worker(mp.Process):

	def __init__(self, index, posting_id_queue, csv_logger):
		mp.Process.__init__(self)
		self.index = index
		self.posting_id_queue = posting_id_queue
		self.csv_logger = csv_logger


	def __extract_data_for_dropdown(self, databit):
		to_request = databit['url'] + '&seq=postingLocationDetails&posting_id=' + str(databit['posting_id']) + '&location_id=' + str(databit['location_id'])
		print to_request
		request = requests.get(to_request, proxies=REQUEST_PROXIES)
		soup = BeautifulSoup(request.text)

		content = soup.find('div', attrs = {'id' : 'Slot_0_3_3_10'})
		job_title = content.find('h1').text
		sidebar = soup.find(attrs = 'sidebar')
		address = sidebar.find_all('span', attrs={'class' : 'field readOnly'})
		try:
			street = address[0].text
			city = address[1].text
			state = address[2].text
			zipcode = address[3].text
			address = street + ', ' +  state + ', ' + city + ', ' + zipcode
		except:
			loc = ""
			for i in range(len(address)):
				loc += address[i].text
				if i != len(address)-1:
					loc += ", "
			address = loc

		try:
			description = soup.find_all(attrs = 'formattedContent')[0].text.strip()
		except:
			description = None

		d = {}
		d['job_title'] = job_title
		d['job_description'] = description.encode('utf-8')
		d['company_name'] = databit['company_name']
		d['address'] = address
		self.csv_logger.data_queue.put(d)
		

	def __extract_data_for_listing(self, databit):
		to_request = databit['url'] + '&seq=jobDetails&posting_id=' + str(databit['posting_id'])
		print to_request
		request = requests.get(to_request, proxies=REQUEST_PROXIES)
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
					if front['dropdown']:
						self.__extract_data_for_dropdown(front)
					else:
						self.__extract_data_for_listing(front)
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
