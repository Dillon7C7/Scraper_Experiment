#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as CE
from selenium.common.exceptions import TimeoutException
from cryptography.fernet import Fernet
import time
import json
import re

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


	def get_credentials(self, key_file='.nnkey', usr_file='.nnuser', pw_file='.nnpass'):
		
		with open(key_file, 'rb') as kf:
			key = kf.read()
		
		f = Fernet(key)
		with open(usr_file, 'rb') as uf:
			username = uf.read()
		
		with open(pw_file, 'rb') as pf:
			password = pf.read()
		
		self.username = f.decrypt(username).decode()
		self.password = f.decrypt(password).decode()
		
	def load_browser(self):
		self.browser.get(self.url)
		try:
			wait = WebDriverWait(self.browser, self.delay)
			wait.until(EC.presence_of_element_located((By.ID, 'mobile-header-nav')))
			print('front page loaded!')
		except:
			print('mobile header nav not loaded!')

	def login(self):
		self.get_credentials()
		login_button = self.browser.find_element_by_css_selector('#mobile-header-nav > ul.nav.navbar-nav.navbar-right > li.navbar-login-link > a') 
		login_button.click()
		try:
			wait = WebDriverWait(self.browser, self.delay)
			wait.until(EC.presence_of_element_located((By.ID, 'login_prompt')))
			self.browser.find_element_by_id('modal_customer_username').send_keys(self.username)
			self.browser.find_element_by_id('modal_customer_password').send_keys(self.password)
			login_button2 = self.browser.find_element_by_id('modal_customer_submit_button')
			login_button2.click()

			print('login prompt loaded!')
		except:
			print('login prompt not loaded!')

	def switch_to_archives(self):
		attempts = 0
		while (attempts < 8):
			try:
				wait = WebDriverWait(self.browser, self.delay)
				wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'ARCHIVES')))
				wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'ARCHIVES')))

				archive_button = self.browser.find_element_by_link_text('ARCHIVES')
				archive_button.click()
				print('Archive button clicked!')
				break
					
			except Exception as e:
				print(e)

			attempts += 1
	
	def switch_to_segment_list(self):
		
		attempts = 0
		while (attempts < 8):
			try:
				wait = WebDriverWait(self.browser, self.delay)
				wait.until(EC.presence_of_element_located((By.ID, 'subnav')))
				search_by_segment_btn = self.browser.find_element_by_css_selector('#subnav > div.container > ul > li:nth-child(2) > button')
				search_by_segment_btn.click()
				print('Search by segment button clicked')
				break
					
			except Exception as e:
				print('Failed to navigate to \'SEARCH BY SEGMENT\'')
				print(e)

			attempts += 1

		#self.get_segment_type()

	def get_segment_type(self, segment_ID):

		attempts = 0
		while (attempts < 8):
			try:
				wait = WebDriverWait(self.browser, self.delay)

				# list of segment types
				wait.until(EC.presence_of_element_located((By.ID, 'filter-segments')))

				segment_filter = self.browser.find_element_by_id('filter-segments')
				#segment_type_li = segment_filter.find_elements_by_tag_name('li')

				break

			except Exception as e:
				print(e)

			attempts += 1








		#########################TEST STUFF#####################################

		data = []
		segment_filter.find_element_by_link_text(segment_ID).click()
	
		try:
			
			wait.until(EC.presence_of_element_located((By.ID, 'arhive_index_view')))
			archive_index_view = self.browser.find_element_by_id('arhive_index_view')
			#wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pagnation-controls')))

			# used for conditional
			segment_page_num_divs = self.browser.find_elements_by_class_name('pagnation-controls')

			if segment_page_num_divs:
				
				segment_page_num_div = self.browser.find_element_by_class_name('pagnation-controls')
				next_button = segment_page_num_div.find_element_by_partial_link_text('NEXT')

				last_button = segment_page_num_div.find_element_by_partial_link_text('LAST')
				num_pages = last_button.get_attribute('href')
				last_page_num = int(num_pages[-1])
			else:
				last_page_num = 1
				
			video_page_div = archive_index_view.find_element_by_class_name('archives-content')
			video_page_list = video_page_div.find_elements_by_css_selector('.archives-content > div > div > div')
			#video_page_list = video_page_div.find_elements_by_css_selector('.archives-content > div > div > div > a')

			for vid in video_page_list:
				data.append(vid.text)

			for page in range(1, last_page_num):

				# click NEXT for every page
				next_button.click()
				wait.until(EC.presence_of_element_located((By.ID, 'arhive_index_view')))
				archive_index_view = self.browser.find_element_by_id('arhive_index_view')
				wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pagnation-controls')))
				segment_page_num_div = self.browser.find_element_by_class_name('pagnation-controls')
				# if we are on the last page, do not look for the 'NEXT' button
				if (page != last_page_num - 1):
					next_button = segment_page_num_div.find_element_by_partial_link_text('NEXT')
				video_page_div = archive_index_view.find_element_by_class_name('archives-content')
				video_page_list = video_page_div.find_elements_by_css_selector('.archives-content > div > div > div')

				for vid in video_page_list:
					data.append(vid.text)
					#print(vid.text)
				

		# this segment doesn't have a "last" button to worry about.
		except TimeoutException:
			print('PASS THIS SEGMENT. JUST ONE PAGE')		
			print('JUST DO THE GRABBIN FROM FIRST PAGE!')
		except Exception as e:
			print('something else failed')
			print(e)

		filename = segment_ID + '_data.json'

	#	with open(filename, 'w') as travel_file:
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
			if (seggy != 'Travels'):
				self.switch_to_archives()
				self.switch_to_segment_list()
				self.get_segment_type(seggy)
			
		
		
				

########################################
if __name__ == '__main__':
	scraper = NakedNewsScraper()
	scraper.load_browser()
	scraper.login()
	scraper.scrape_all()
#	scraper.switch_to_archives()
#	scraper.switch_to_segment_list()
#	scraper.get_segment_type()
#	scraper.switch_to_archives()
#	scraper.switch_to_segment_list()
	time.sleep(4)
	scraper.browser.quit()
