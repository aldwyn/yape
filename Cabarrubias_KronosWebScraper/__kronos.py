import splinter, time
from bs4 import BeautifulSoup

URL = 'https://wfa.kronostm.com/index.jsp?applicationName=PetsmartNonReqExt'
SERVICE_ARGS = [
    '--proxy=23.27.197.200:24801',
    '--proxy=23.27.197.201:24801',
    '--proxy=23.27.197.202:24801',
    '--proxy=23.27.197.203:24801',
    '--proxy=23.27.197.204:24801',
    '--proxy=23.27.197.205:24801',
    '--proxy-type=http',
]

# browser = splinter.Browser('chrome', service_args=SERVICE_ARGS, executable_path='C:\Python27\Lib\site-packages\chromedriver_win32\chromedriver.exe')
browser = splinter.Browser('phantomjs', service_args=SERVICE_ARGS, user_agent="Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130401 Firefox/21.0")


with browser:
	print 'hey'
	browser.visit(URL)
	states = browser.find_by_css('#stateList > option')
	del states[0]

	for state in states:
		browser.select('search.stateList.value', state.value)
		cities_select = browser.find_by_id(state.value)
		cities = cities_select.find_by_css('select > option')
		del cities[0]

		for city in cities:
			browser.select('search.cityList.value', city.value)
			print state.value, city.value