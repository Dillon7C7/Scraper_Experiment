#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as CE
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from cryptography.fernet import Fernet
import time
import sys
import json
import re
import logging
from datetime import datetime

# custom module
import local_db

class NakedNewsScraper(object):

	def __init__(self):

		self.chromedriver_path = '/mnt/c/Users/dillon/AppData/Local/Programs/Python/Python36-32/chromedriver.exe' 
		self.url = 'https://www.nakednews.com'

		self.chrome_options = Options()
		self.chrome_options.add_argument('--incognito')
		self.chrome_options.add_argument('--disable-gpu')
		self.chrome_options.add_argument('--disable-infobars')
		self.chrome_options.add_argument('--disable-extensions')
		self.chrome_options.add_argument('--no-sandbox')
		self.chrome_options.add_argument('--disable-web-security')

		self.chrome_options.add_argument('--start-maximized')

		#self.chrome_options.add_argument('--headless')
		#self.chrome_options.add_argument('--window-size=1920,1080') # --start-maximized doesn't work in headless mode

		# tuple of segments to grab data for
		self.approved_segments = ('Auditions', 'Behind The Lens', 'Behind the Scenes', 'Boob of the Week',
				'Busts For Laughs', 'Closing Remarks', 'Cooking in the Raw', 'Dating Uncovered',
				'Entertainment', 'Flex Appeal', 'Game Spot', 'HollywoodXposed',
				'Inside The Box', 'Naked At The Movies', 'Naked Foodie', 'Naked Goes Pop',
				'Naked Goes Pot', 'Naked In The Streets', 'Naked News Moves', 'Naked Yogi',
				'News off the Top', 'News off the Top Part 2', 'Nude and Improved', 'Odds N Ends',
				'Odds N Ends Part 2', 'One on One', 'Pillow Talk', 'Point Of View', 'Pop My Cherry',
				'Riding In A Car Naked', 'Sports', 'Talk is Cheap', 'The Schmooze', 'Travels',
				'Trending Now', 'Turn it Up', 'Versus', 'Video Blog', "Viewer's Mail", 'Weather', 'Wheels')

		self.skipped_segments = ('A Closer Look', 'All The Rage', 'App-date', 'Best of',
				'Best of Naked News', 'Bloopers', 'Boob Of The Year', 'Boob-tube', 'Business',
				'Christmas Special', 'Commentary', 'Costume Contest', 'Drinking In The Raw',
				'Dumb Criminals', 'Fashion', 'Fringe', 'Health', 'Health Watch', 'Hot Properties',
				'International News', 'Know your Wood', 'Legal Briefs', 'Life & Leisure',
				'Lily in the UK', 'Locker Talk', 'Media Matters', 'Naked League Comic', 'Naked Nerd',
				'Naked Tech', 'Nerd Bites', 'New Release Rack', 'News off the Top Part 3',
				'North American News', 'NudeViews', 'Olympic Report', 'On the Web', 'One From The Vault',
				'Pan Am', 'Person of The Year', 'Power Play', 'Pranks', 'Status Update', 'Timeline',
				'Vampire Bites', 'Year In Review')

		self.log_fmt = '%(filename)s - %(lineno)d - %(funcName)s - %(levelname)s - %(message)s'
		self.logger = logging.basicConfig(filename='LOGGING/SCRAPER.log', filemode='w', format=self.log_fmt, level=logging.ERROR)

		try:
			# call method to get credentials
			self.__username, self.__password = self.__get_credentials()

			# initialize browser
			self.browser = webdriver.Chrome(chrome_options=self.chrome_options, executable_path=self.chromedriver_path)

			self.delay = 40 # seconds
			self.wait = WebDriverWait(self.browser, self.delay) # WebDriverWait object

			self.segment_types = []

			# methods that we always want to run
			self.__load_browser()
			self.__login()

			# initialize local sqlite3 database
			self.db = local_db.Local_Database('local_db.back')
			self.latest_db_date = self.db.get_latest_date()

		except Exception as e:
			logging.error(e, exc_info=True)
	
	def parse_data(self):
		pass

	def db_wrapper(self):
		pass
		
	def __get_credentials(self, key_file='.nnkey', usr_file='.nnuser', pw_file='.nnpass'):
		'''Method used to get symmetrically encrypted credentials on disk.
		
			Attributes:
				key_file: text file storing the Fernet key.
				usr_file: text file storing an encrypted username.
				pw_file:  text file storing an encrypted password.
		'''
		
		try:

			# key for Fernet object
			with open(key_file, 'rb') as kf:
				key = kf.read()
			
			# create Fernet object with key from key_file
			f = Fernet(key)

			# get encrypted user name
			with open(usr_file, 'rb') as uf:
				username = uf.read()
			
			# get encrypted password
			with open(pw_file, 'rb') as pf:
				password = pf.read()
			
			username = f.decrypt(username).decode()
			password = f.decrypt(password).decode()

			return username, password

		except Exception as e:
			logging.error(e, exc_info=True)
		
	def __load_browser(self):
		''' Load the web browser. '''

		# open browser
		self.browser.get(self.url)

		try:
			self.wait.until(EC.presence_of_element_located((By.ID, 'mobile-header-nav')))
			self.mobile_header_nav = self.browser.find_element_by_id('mobile-header-nav')

		except Exception as e:
			logging.error(e, exc_info=True)

	def __login(self):
		''' Login to the web browser. '''

		try:
			self.login_button = self.mobile_header_nav.find_element_by_css_selector('#mobile-header-nav > ul.nav.navbar-nav.navbar-right > li.navbar-login-link > a') 
			self.login_button.click()

		except Exception as e:
			logging.error(e)

		# handle login popup
		try:
			self.wait.until(EC.presence_of_element_located((By.ID, 'login_prompt')))
			self.login_prompt = self.browser.find_element_by_id('login_prompt')
			self.login_prompt.find_element_by_id('modal_customer_username').send_keys(self.__username)
			self.login_prompt.find_element_by_id('modal_customer_password').send_keys(self.__password)
			self.login_button2 = self.login_prompt.find_element_by_id('modal_customer_submit_button')
			self.login_button2.click()

		except Exception as e:
			logging.error(e, exc_info=True)

	def __switch_to_archives(self):
		''' Switch to archives. '''

		try:
			# this element receives the click before the 'ARCHIVES' link, so we wait until it is not visible.
			self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '#login_prompt > div.modal-backdrop.in')))

			# a child div seems to contain the links we need, but doesn't seem to work when clicking
			self.wait.until(EC.presence_of_element_located((By.ID, 'header-nav')))
			self.header_nav = self.browser.find_element_by_id('header-nav')

			# make sure link is ready to be clicked; all of these checks is likely overkill
			self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'ARCHIVES')))
			self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'ARCHIVES')))
			self.wait.until(EC.visibility_of_element_located((By.LINK_TEXT, 'ARCHIVES')))

			# click on archives
			self.header_nav.find_element_by_link_text('ARCHIVES').click()

		except StaleElementReferenceException as se:
			logging.error(se, exc_info=True)

		except Exception as e:
			logging.error(e, exc_info=True)
	
	def __switch_to_segment_list(self):
		''' Switch to segment list. '''	

		try:
			self.wait.until(EC.presence_of_element_located((By.ID, 'subnav')))

			self.subnav = self.browser.find_element_by_id('subnav')

			# 'SEARCH BY SEGMENT' button
			self.search_by_segment_btn = self.subnav.find_element_by_css_selector('#subnav > div.container > ul > li:nth-child(2) > button')
			self.search_by_segment_btn.click()

			# web element containing list of segment types
			self.wait.until(EC.presence_of_element_located((By.ID, 'filter-segments')))
			self.segment_filter = self.browser.find_element_by_id('filter-segments')
			
			# child div of child div containing list of segment types
			self.segment_filter_div = self.segment_filter.find_element_by_css_selector('#filter-segments > div > div')
				
		except Exception as e:
			logging.error(e, exc_info=True)

	# don't need to call this more than once...ever
	def __get_segment_types(self):
		''' Get the segment types and store result in list self.segment_types and json. '''

		try:
			# list of selenium web objects containing segment type text
			self.segment_type_li = self.segment_filter_div.find_elements_by_tag_name('li')

			# list of segment type text
			self.segment_types = [li.text for li in self.segment_type_li]

			# dump segment list into a json file
			with open('segment_types.json', 'w') as segment_json:
				json.dump(self.segment_types, segment_json)

		except Exception as e:
			logging.error(e, exc_info=True)

	def get_segment_info(self, segment_ID, latest_db_date=None):
		''' Scrape segment information '''

		is_up_to_date = False

		# parsed data ready to be inserted into db
		page_db_data = []

		if latest_db_date:
			# latest date in database
			latest_db_date = self.latest_db_date

		# switch to the appropriate page
		self.__switch_to_archives()
		self.__switch_to_segment_list()

		# link to a certain segment's archives page
		self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, segment_ID)))
		self.segment_filter_div.find_element_by_link_text(segment_ID).click()

		while True:

			try:
				# parent div containing nested divs which contain desired text
				self.wait.until(EC.presence_of_element_located((By.ID, 'arhive_index_view')))
				
				# wait for first child div of arhive_index_view (container)
				self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#arhive_index_view > div')))
		
				# wait for second child div of arhive_index_view (row-r)
				self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#arhive_index_view > div > div')))
				self.arhive_index_view_rows_container = self.browser.find_element_by_css_selector('#arhive_index_view > div > div')
		
				self.browser.implicitly_wait(self.delay)

				# list of all divs containing desired segment info on page
				self.individual_segment_list = self.arhive_index_view_rows_container.find_elements_by_css_selector('#arhive_index_view > div > div > div')
		
				# loop through each div containing segment info
				for segment in self.individual_segment_list:
		
					# Anchors + Segment Type
					self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#arhive_index_view > div > div > div > div > div > a')))
					anchor_and_segment = segment.find_element_by_css_selector('#arhive_index_view > div > div > div > div > div > a')

					# text to be parsed (1 of 2)
					as_text = anchor_and_segment.text

					# Segment type parsed for database (db data: 1 of 3)
					db_segment = as_text[as_text.index('In ')+3:]

					# Anchors parsed for database (db data: 2 of 3)
					db_anchors = as_text[:as_text.index('In ')].strip()
		
					# Date
					self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#arhive_index_view > div > div > div > div > div > small')))
					air_date = segment.find_element_by_css_selector('#arhive_index_view > div > div > div > div > div > small')

					# text to be parsed (2 of 2)
					ad_text = air_date.text

					date_obj = datetime.strptime(ad_text, '%A %B %d, %Y')

					# Date parsed for database (db data: 3 of 3)
					db_date = date_obj.strftime('%Y-%m-%d')

					# if latest_db_date is given, and it is >= date of segment,
					# e.g. if latest_db_date = '2019-03-20' >= db_date = '2019-03-19' then break
					if latest_db_date and latest_db_date >= db_date:
						is_up_to_date = True
						break
		
					# else, add to database

					db_tuple = (db_segment, db_date, db_anchors)
					page_db_data.append(db_tuple)

				# we are up to date with the DB
				if is_up_to_date:
					break

				self.browser.implicitly_wait(self.delay)

				# list containing web elements with the link text 'LAST »'. len is 0 or 1
				# **will break the program if this string appears elsewhere on the page!
				self.last_button_list = self.browser.find_elements_by_link_text('LAST »') # UTF-8 encoding

				# if the last_button_list is empty, then there is no "LAST" button on the page, and we can exit the loop
				if not self.last_button_list:
					break
				
				# else:
				# loop through pages until no "LAST" link is found
				self.page_numbers = self.browser.find_element_by_class_name('pagnation-controls')
				self.next_button = self.page_numbers.find_element_by_link_text('NEXT ›')
				self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'NEXT ›')))
				self.next_button.click()
		
			# most important error check.
			except Exception as e:
				logging.error(e, exc_info=True)

		# insert segment data for segment type into database
		try:
			self.db.insert_many(page_db_data)

		except Exception as e:
			logging.error(e, exc_info=True)

	def scrape_all(self, get_db_date=True):

		if get_db_date:
			# latest date in database
			latest_db_date = self.latest_db_date
		else:
			latest_db_date = None

		try:
			for segg in self.approved_segments:
				self.get_segment_info(segg, latest_db_date)

		except Exception as e:
			logging.error(e, exc_info=True)

	def __del__(self):

		try:
			self.browser.quit()
			# database will close during its destructor
		except Exception as e:
			logging.error(e, exc_info=True)
