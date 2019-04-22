#!/usr/bin/env python3

from cryptography.fernet import Fernet
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as CE
import time

class NakedNewsScraper(object):
	def __init__(self):
		self.chromedriver_path = '/mnt/c/Users/dillon/AppData/Local/Programs/Python/Python36-32/chromedriver.exe' 
		self.url = 'https://www.nakednews.com'
		self.chrome_options = Options()
		self.chrome_options.add_argument('--start-maximized')
		self.delay = 10 # seconds
		self.username = ''
		self.password = ''
		self.browser = webdriver.Chrome(chrome_options=self.chrome_options, executable_path=self.chromedriver_path)

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
		self.search_by_segment()
	
	def search_by_segment(self):
		
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
				print('second fail')
				print(e)

			attempts += 1

		#actions = ActionChains(self.browser)
		#actions.move_to_element(archive_button)
		#actions.click(archive_button)
		#actions.perform()
			
########################################
if __name__ == '__main__':
	scraper = NakedNewsScraper()
	scraper.load_browser()
	scraper.login()
	scraper.switch_to_archives()
	time.sleep(5)
	scraper.browser.quit()
