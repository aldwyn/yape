import splinter, time, logging
from bs4 import BeautifulSoup

logging.basicConfig(filename='kronos.log', level=logging.WARNING, format='%(message)s')

URL = 'http://www.google.com'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130401 Firefox/21.0'
EXECUTABLE_PATH = 'C:\Python27\Lib\site-packages\chromedriver_win32\chromedriver.exe'
SERVICE_ARGS = [
    '--proxy=23.27.197.200:24801',
    # '--proxy=23.27.197.201:24801',
    # '--proxy=23.27.197.202:24801',
    # '--proxy=23.27.197.203:24801',
    # '--proxy=23.27.197.204:24801',
    # '--proxy=23.27.197.205:24801',
    '--proxy-type=http',
]

# browser = splinter.Browser(user_agent=USER_AGENT)
browser = splinter.Browser('chrome', service_args=SERVICE_ARGS, executable_path=EXECUTABLE_PATH)
# browser = splinter.Browser('phantomjs', service_args=SERVICE_ARGS, user_agent=USER_AGENT)

with browser:
	browser.visit(URL)
	browser.fill('q', 'site:https://wfa.kronostm.com')
	browser.find_by_name('btnG').click()
	
	while True:
		print browser.url
		for link in browser.find_by_css('.r > a'):
			logging.warning(link['href'])

		try:
			browser.find_by_css('#pnnext').click()
			time.sleep(5)
		except:
			break

