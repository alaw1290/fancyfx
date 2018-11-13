import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def run_scraper(currency_pairs, year, downloads_directory, webdriver_path):
	"""
	function that will grab all forex data from the currencies listed and the year specified
	"""


	chrome_options = webdriver.ChromeOptions()
	
	prefs = {
		"directory_upgrade": 1,
		"download.default_directory": downloads_directory,
		"download.prompt_for_download": 0
	}

	chrome_options.add_experimental_option("prefs",prefs)

	driver = webdriver.Chrome(executable_path=webdriver_path, chrome_options=chrome_options)
	driver.get(f'http://ratedata.gaincapital.com/{year}')

	if '404' in driver.title:
		driver.close()
		raise Exception('Year parameter is not valid')

	months = [
		'01 January',
		'02 February',
		'03 March',
		'04 April',
		'05 May',
		'06 June',
		'07 July',
		'08 August',
		'09 September',
		'10 October',
		'11 November',
		'12 December'
		]

	for month in months:
		driver.get(f'http://ratedata.gaincapital.com/{year}/{month}')
		a_links = driver.find_elements(By.TAG_NAME, 'a')
		for link in a_links:
			filename = link.text
			if any([True if a in filename else False for a,b in currency_pairs]):
				for pair in currency_pairs:
					a,b = pair 
					if a in filename and b in filename:
						link.click()
						break
		time.sleep(30)
		destination = os.path.join(downloads_directory, f'{year}/{month}')
		os.makedirs(os.path.join(downloads_directory, f'{year}/{month}'), exist_ok=True)
		zip_files = os.listdir(downloads_directory)
		for zip_file in zip_files:
			if '.zip' in zip_file:
				shutil.move(os.path.join(downloads_directory,zip_file), os.path.join(destination,zip_file))


	driver.close()


