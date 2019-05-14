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
import sqlite3
import re

#class Database(object):
#
#	def __init__(self, database_name):
#		self.database_name = database_name
#		self.db = None
#		self.cursor = None
#		self.connect

class NakedNewsScraper(object):

	def __init__(self):
		self.chromedriver_path = '/mnt/c/Users/dillon/AppData/Local/Programs/Python/Python36-32/chromedriver.exe' 
		self.url = 'https://www.nakednews.com'
		self.chrome_options = Options()
		self.chrome_options.add_argument('--start-maximized')
		self.chrome_options.add_argument('--incognito')
		self.delay = 10 # seconds
		self.wait = '' # WebDriverWait object
		self.username = ''
		self.password = ''
		self.browser = webdriver.Chrome(chrome_options=self.chrome_options, executable_path=self.chromedriver_path)
		self.segment_types = []

		log_fmt = '%(filename)s - %(lineno)d - %(funcName)s - %(levelname)s - %(message)s'
		self.logger = logging.basicConfig(filename='SCRAPE_LOG.log', filemode='w', format=log_fmt, level=logging.ERROR)

	def get_credentials(self, key_file='.nnkey', usr_file='.nnuser', pw_file='.nnpass'):
		'''Method used to store symmetrically encrypted credentials on disk.
		
			Attributes:
				key_file: text file storing the Fernet key.
				usr_file: text file storing an encrypted username.
				pw_file:  text file storing an encrypted password.
		'''
		
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
		
		self.username = f.decrypt(username).decode()
		self.password = f.decrypt(password).decode()
		
	def load_browser(self):
		''' Load the web browser. '''

		self.browser.get(self.url)
		self.wait = WebDriverWait(self.browser, self.delay)

		try:
			self.wait.until(EC.presence_of_element_located((By.ID, 'mobile-header-nav')))
			self.mobile_header_nav = self.browser.find_element_by_id('mobile-header-nav')

		except Exception as e:
			logging.error(e, exc_info=True)

	def login(self):
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
			self.login_prompt.find_element_by_id('modal_customer_username').send_keys(self.username)
			self.login_prompt.find_element_by_id('modal_customer_password').send_keys(self.password)
			self.login_button2 = self.login_prompt.find_element_by_id('modal_customer_submit_button')
			self.login_button2.click()

		except Exception as e:
			logging.error(e, exc_info=True)

	def switch_to_archives(self):
		''' Switch to archives. '''

		try:

			# this element receives the click before the 'ARCHIVES' link, so we wait until it is not visible.
			self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '#login_prompt > div.modal-backdrop.in')))

			#invis_element = self.browser.find_element_by_css_selector('#login_prompt > div.modal-backdrop.in')

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

		except Element as e:
			logging.error(e, exc_info=True)
	
	def switch_to_segment_list(self):
		''' Switch to segment list. '''	

		try:
			self.wait.until(EC.presence_of_element_located((By.ID, 'subnav')))

			self.subnav = self.browser.find_element_by_id('subnav')
			self.search_by_segment_btn = self.subnav.find_element_by_css_selector('#subnav > div.container > ul > li:nth-child(2) > button')

			self.search_by_segment_btn.click()
				
		except Exception as e:
			logging.error(e, exc_info=True)

	def get_segment_types(self):
		''' Get the segment types and store result in list self.segment_types and json. '''

		try:
			self.wait.until(EC.presence_of_element_located((By.ID, 'filter-segments')))

			# web element containing list of segment types
			self.segment_filter = self.browser.find_element_by_id('filter-segments')
			
			# child div of child div containing list of segment types
			self.segment_filter_div = self.segment_filter.find_element_by_css_selector('#filter-segments > div > div')

			# list of selenium web objects containing segment type text
			self.segment_type_li = self.segment_filter_div.find_elements_by_tag_name('li')

			# list of segment type text
			self.segment_types = [li.text for li in self.segment_type_li]

			# create seperate class to make a database
			with open('segment_types.json', 'w') as segment_json:
				json.dump(self.segment_types, segment_json)

			#db = sqlite3.connect('MAY14.db')
			#cursor = db.cursor()
			#cursor.execute('''CREATE TABLE IF NOT EXISTS segment_types(type_id INTEGER PRIMARY KEY, segment_type TEXT NOT NULL UNIQUE''')
			#db.commit()

		except Exception as e:
			logging.error(e, exc_info=True)

	def get_segment_info(self, segment_ID):
		''' Scrape segment info '''

		page_data = []

		# link to a certain segment's archives page
		self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, segment_ID)))
		self.segment_filter_div.find_element_by_link_text(segment_ID).click()

		#sdlfjasdklfsdfsdf# while the div containing the 'LAST' button exists, click

		while True:

			try:
				# parent div containing nested divs which desired text
				self.wait.until(EC.presence_of_element_located((By.ID, 'arhive_index_view')))
				
				# wait for first child div of arhive_index_view (container)
				self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#arhive_index_view > div')))
		
				# wait for second child div of arhive_index_view (row-r)
				self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#arhive_index_view > div > div')))
				self.arhive_index_view_rows_container = self.browser.find_element_by_css_selector('#arhive_index_view > div > div')
		
				# list of all divs containing desired segment info on page
				self.individual_segment_list = self.arhive_index_view_rows_container.find_elements_by_css_selector('#arhive_index_view > div > div > div')
		
				# loop through each div containing segment info
				for segment in self.individual_segment_list:
		
					# Anchors + Segment Type
					self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#arhive_index_view > div > div > div > div > div > a')))
					anchor_and_segment = segment.find_element_by_css_selector('#arhive_index_view > div > div > div > div > div > a')
		
					# Date
					self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#arhive_index_view > div > div > div > div > div > small')))
					air_date = segment.find_element_by_css_selector('#arhive_index_view > div > div > div > div > div > small')
		
					# append anchors, segment type, and date to our list
					page_data.append((air_date.text, anchor_and_segment.text))

				# list containing web elements with the link text 'LAST »'
				# **will break the program if it appears elsewhere on the page!
				self.last_button_list = self.browser.find_elements_by_link_text('LAST »')

				# if the last_button_list is empty, then there is no "LAST" button on the page, and we can break
				if not self.last_button_list:
					break
				
				# else:
				# loop through pages until no "LAST" link is found
				self.page_list = self.browser.find_element_by_class_name('pagnation-controls')
				self.next_button = self.page_list.find_element_by_link_text('NEXT ›')
				self.next_button.click()
		
			# most important error check.
			except Exception as e:
				logging.error(e, exc_info=True)

		#print(page_data)

	def scrape_all(self):

		with open('segment_types.json', 'r') as seg_types:
			self.segment_types = json.load(seg_types)

		for seggy in self.segment_types:
			self.switch_to_archives()
			self.switch_to_segment_list()
			self.get_segment_type(seggy)
			
		
				

########################################
if __name__ == '__main__':
	scraper = NakedNewsScraper()
	scraper.get_credentials()
	scraper.load_browser()
	scraper.login()
	scraper.switch_to_archives()
	scraper.switch_to_segment_list()
	scraper.get_segment_types()
	scraper.get_segment_info('Travels')
	#scraper.scrape_all()
#	scraper.switch_to_archives()
	time.sleep(4)
	scraper.browser.quit()
