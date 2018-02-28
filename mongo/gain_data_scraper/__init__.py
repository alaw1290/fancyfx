try:
	from .config import *
except ImportError as e:
	downloads_directory = ''
	webdriver_path = ''
	raise Exception('Please ensure you have a config file properly configured as directed under the README of the scraper, otherwise the function will not peform as intended')


def scrape_for(currencies_list, year, downloads_directory=downloads_directory, webdriver_path=webdriver_path):
	'''
	runs the selenium scraper on the GAIN capital tick rate data for a specfied year grabbing specified currencies
	'''

	from .scraper import run_scraper
	
	currencies_list = list(set(currencies_list))
	year = str(year)

	run_scraper(currencies_list, year, downloads_directory, webdriver_path)

