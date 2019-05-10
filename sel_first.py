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
		'''load the web browser'''

		self.browser.get(self.url)
		try:
			wait = WebDriverWait(self.browser, self.delay)
			wait.until(EC.presence_of_element_located((By.ID, 'mobile-header-nav')))
			self.mobile_header_nav = self.browser.find_element_by_id('mobile-header-nav')

		except Exception as e:
			logging.error(e)

	def login(self):
		''' Login to the web browser. '''

		try:
			self.login_button = self.mobile_header_nav.find_element_by_css_selector('#mobile-header-nav > ul.nav.navbar-nav.navbar-right > li.navbar-login-link > a') 
			self.login_button.click()

		except Exception as e:
			logging.error(e)

		# handle login popup
		try:
			wait = WebDriverWait(self.browser, self.delay)
			wait.until(EC.presence_of_element_located((By.ID, 'login_prompt')))
			self.login_prompt = self.browser.find_element_by_id('login_prompt')
			self.login_prompt.find_element_by_id('modal_customer_username').send_keys(self.username)
			self.login_prompt.find_element_by_id('modal_customer_password').send_keys(self.password)
			self.login_button2 = self.login_prompt.find_element_by_id('modal_customer_submit_button')
			self.login_button2.click()

		except Exception as e:
			logging.error(e)

	def switch_to_archives(self):
		''' Switch to archives. '''

#		attempts = 0
#		while (attempts < 8):

		wait = WebDriverWait(self.browser, self.delay)
		wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '#login_prompt > div.modal-backdrop.in')))

		# this element element recieves the click before the 'ARCHIVES' button
		#invis_element = self.browser.find_element_by_css_selector('#login_prompt > div.modal-backdrop.in')

#			while invis_element.is_enabled():
#				print('hohohoh')

#		except StaleElementReferenceException as se:
#			logging.error(se)

			#wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'modal-backdrop in')))
##		try:
		wait.until(EC.presence_of_element_located((By.ID, 'header-nav')))
##
		wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'ARCHIVES')))
		wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'ARCHIVES')))
		wait.until(EC.visibility_of_element_located((By.LINK_TEXT, 'ARCHIVES')))
##
		self.header_nav = self.browser.find_element_by_id('header-nav')
		self.header_nav.find_element_by_link_text('ARCHIVES').click()
		######### working ###############
			#da = self.top_button_nav.find_elements_by_css_selector('*')
			#print(self.top_button_nav.find_elements_by_css_selector('*'))
##
##			#self.top_button_nav.find_elements_by_tag_name('li')[4].find_element_by_href().click()
##
##			# 4th button in the nav
###			self.archive_button = self.top_button_nav.find_element_by_link_text('ARCHIVES')
###			self.archive_button.click()
##
##		except Exception as e:
##			print(e)
##			logging.error(e)

#		try:
#			time.sleep(6)
#			self.archive_button.click()
#
#		except StaleElementReferenceException as se:
#			print('penis\;')
	#		print(se)
	#		wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'ARCHIVES')))
	#		self.archive_button = self.top_button_nav.find_element_by_css_selector('ul > li:nth-child(4) > a')
	#		self.archive_button.click()

	#		logging.error(se)

	#	except Exception as e:
	#		print(e)
	#		logging.error(e)
					

			#attempts += 1
	
	def switch_to_segment_list(self):
		''' Switch to segment list. '''	

		attempts = 0
		while (attempts < 8):
			try:
				wait = WebDriverWait(self.browser, self.delay)
				wait.until(EC.presence_of_element_located((By.ID, 'subnav')))

				self.subnav = self.browser.find_element_by_ID('subnav')
				self.search_by_segment_btn = self.subnav.find_element_by_css_selector('#subnav > div.container > ul > li:nth-child(2) > button')

				self.search_by_segment_btn.click()
				break
					
			except Exception as e:
				logging.error(e)

			attempts += 1

	def get_segment_types(self):
		''' Get the segment types and store result in list self.segment_types and json. '''

		attempts = 0
		while (attempts < 8):
			try:
				wait = WebDriverWait(self.browser, self.delay)

				# web element containing list of segment types
				wait.until(EC.presence_of_element_located((By.ID, 'filter-segments')))
				self.segment_filter = self.browser.find_element_by_id('filter-segments')
				
				# div containing lsits of segment types
				self.segment_filter_div = self.segment_filter.find_element_by_css_selector('#filter-segments > div > div')

				# list of segment types
				self.segment_type_li = segment_filter_div.find_elements_by_tag_name('li')
				self.segment_types = self.segment_type_li 

				break

			except Exception as e:
				logging.error(e)

			attempts += 1

	def get_segment_info(self, segment_ID):
		''' Scrape segment info '''

		#########################TEST STUFF#####################################
		data = []
		self.segment_type_li.find_element_by_link_text(segment_ID).click()
	
	#	try:
	#		
	#		wait.until(EC.presence_of_element_located((By.ID, 'arhive_index_view')))
	#		archive_index_view = self.browser.find_element_by_id('arhive_index_view')
	#		#wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pagnation-controls')))

	#		# used for conditional
	#		segment_page_num_divs = self.browser.find_elements_by_class_name('pagnation-controls')

	#		if segment_page_num_divs:
	#			
	#			segment_page_num_div = self.browser.find_element_by_class_name('pagnation-controls')
	#			next_button = segment_page_num_div.find_element_by_partial_link_text('NEXT')

	#			last_button = segment_page_num_div.find_element_by_partial_link_text('LAST')
	#			num_pages = last_button.get_attribute('href')
	#			last_page_num = int(num_pages[-1])
	#		else:
	#			last_page_num = 1
	#			
	#		video_page_div = archive_index_view.find_element_by_class_name('archives-content')
	#		video_page_list = video_page_div.find_elements_by_css_selector('.archives-content > div > div > div')
	#		#video_page_list = video_page_div.find_elements_by_css_selector('.archives-content > div > div > div > a')

	#		for vid in video_page_list:
	#			data.append(vid.text)

	#		for page in range(1, last_page_num):

	#			# click NEXT for every page
	#			next_button.click()
	#			wait.until(EC.presence_of_element_located((By.ID, 'arhive_index_view')))
	#			archive_index_view = self.browser.find_element_by_id('arhive_index_view')
	#			wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pagnation-controls')))
	#			segment_page_num_div = self.browser.find_element_by_class_name('pagnation-controls')
	#			# if we are on the last page, do not look for the 'NEXT' button
	#			if (page != last_page_num - 1):
	#				next_button = segment_page_num_div.find_element_by_partial_link_text('NEXT')
	#			video_page_div = archive_index_view.find_element_by_class_name('archives-content')
	#			video_page_list = video_page_div.find_elements_by_css_selector('.archives-content > div > div > div')

	#			for vid in video_page_list:
	#				data.append(vid.text)
	#				#print(vid.text)
	#			

	#	# this segment doesn't have a "last" button to worry about.
	#	except TimeoutException:
	#		print('PASS THIS SEGMENT. JUST ONE PAGE')		
	#		print('JUST DO THE GRABBIN FROM FIRST PAGE!')
	#	except Exception as e:
	#		print('something else failed')
	#		print(e)

	#	filename = segment_ID + '_data.json'
	#	rel_path = 'WEB_DATA/' + filename

	#	with open(rel_path, 'w') as travel_file:
	#		json.dump(data, travel_file)



		#########################TEST STUFF#####################################

		#try:
		#	wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pagnation-controls')))
		#except Exception as e:
		#	print(e)
		#	print('xiaogou')


		#last_but = self.browser.find_element_by_css_selector('#application > div.content > div.pagnation-controls.text-center > ul > li:nth-child(8) > a')

		#for li in segment_type_li:
		#	self.segment_types.append(li.text)

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
	#scraper.switch_to_segment_list()
	#scraper.scrape_all()
#	scraper.switch_to_segment_list()
#	scraper.get_segment_type()
#	scraper.switch_to_archives()
	time.sleep(4)
	scraper.browser.quit()
