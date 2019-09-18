#!/usr/bin/env python3

import json
import pickle
import logging
import time

import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class Google_Sheets_Filler(object):

	def __init__(self):

		self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
	##	### TEST ONE
	##	self.SPREADSHEET_ID = '1duOn6KkNQOwl32qDBn0u1N2KAzg3sH0ugcRIb5FAD3I'
		### REAL ONE
		self.SPREADSHEET_ID = '1wJG6xehj7qKgHpH7l6S3HhawF9GnPS9obxbeZGqF3ZU'
		self.creds_file='credentials.json'

		self.log_fmt = '%(filename)s - %(lineno)d - %(funcName)s - %(levelname)s - %(message)s'
		self.logger = logging.basicConfig(filename='LOGGING/GOOGLESHEET.log', filemode='w', format=self.log_fmt, level=logging.ERROR)

		try:
			self.creds = self.setup_oauth2()
			self.service = build('sheets', 'v4', credentials=self.creds)
			self.spreadsheet = self.service.spreadsheets()
			self.sheets_metadata = self.spreadsheet.get(spreadsheetId=self.SPREADSHEET_ID).execute().get('sheets')

			# get sheet titles and their corresponding IDs
			self.tuple_of_titles_and_sheetIds = self.get_sheet_titles_and_sheetIds()

			for sheet in self.tuple_of_titles_and_sheetIds:
				#if sheet['title'] != 'Video Blog':

				# get the latest date from each sheet
				self.latest_sheet_segment_date = self.get_latest_date_from_sheet(sheet['title'])
				print(self.latest_sheet_segment_date)

				# get database entries greater than the latest date in the speadsheet
				self.database_entries = self.get_db_rows_greater_than(sheet['title'], self.latest_sheet_segment_date)
				print(self.database_entries)

				## doo google stuff if we have database entries
				if self.database_entries:
					self.update_google_sheet(sheet['title'], sheet['sheetId'], self.database_entries, len(self.database_entries))

		except Exception as e:
			print(e)
			logging.error(e, exc_info=True)

	def setup_oauth2(self):
		'''Google-provided code that sets up OAuth2 stuff.'''

		creds = None

		#try:

		# get creds from token file if it exists
		if os.path.exists('token.pickle'):
			with open('token.pickle', 'rb') as token:
				creds = pickle.load(token)
		
		if not creds or not creds.valid:

			# creds present but not valid
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(self.creds_file, self.SCOPES)
				creds = flow.run_local_server()

			with open('token.pickle', 'wb') as token:
				pickle.dump(creds, token)

		return creds

		#except Exception as e:
		#	logging.error(e, exc_info=True)

	def get_sheet_titles_and_sheetIds(self):
		''' Return all sheet titles and sheetIds as a list of dicts. '''

		try:
			# list of dicts with 'title' and 'sheetId' as keys
			list_of_titles_and_sheetIds = [{'title': sheet.get('properties').get('title'), 'sheetId': sheet.get('properties').get('sheetId')} for sheet in self.sheets_metadata]

			# names of sheets to ignore
			removable_sheets = ('Sheet1', 'TV SHOWS')

			tuple_of_titles_and_sheetIds = tuple(filter(lambda reject: reject['title'] not in removable_sheets, list_of_titles_and_sheetIds))

			return tuple_of_titles_and_sheetIds

		except Exception as e:
			logging.error(e, exc_info=True)

	# let's try to GET an entire sheet, trim the anchors column, and POST it back!
	def test_one(self):

		#for element in sheets_metadata:
		#	print(element.get('properties').get('title'))
		
		#array_of_titles = [tit.get('properties').get('title') for tit in sheets_metadata]
		#print(array_of_titles)

		# let's get the # of columns, and the title
	#	for i in range(0, len(sheets_metadata)):
	#		
	#		if i % 9 == 0:
	#			time.sleep(100)
	#		
	#		sheet_num_rows = sheets_metadata[i].get('properties').get('gridProperties').get('rowCount')
	#		sheet_title = sheets_metadata[i].get('properties').get('title')

	#		if sheet_title != 'Sheet1' and sheet_title != 'TV SHOWS':

	#			RANGE_NAME = sheet_title+'!2:'+str(sheet_num_rows)

	#			sheet_result = self.sheets.values().get(spreadsheetId=self.SPREADSHEET_ID, range=RANGE_NAME).execute()
	#			sheet_values = sheet_result.get('values')

	#			# case 1 (most of them): len is 3. trim last element
	#			# case 2: len is 2. anchors empty. keep as '' (trim)
	#			# case 3: len is 4. sent to SA. keep 3 as '' (trim)
	#			# case 4: len is 4. sent to SA. trim 3

	#			for element in sheet_values:
	#				if len(element) <= 2:
	#					element.append('')
	#				element[2] = element[2].strip()
	#			#print(element)

	#			#now we write back
	#			body = {
	#				'values': sheet_values
	#				}
	#			write_result = self.sheets.values().update(spreadsheetId=self.SPREADSHEET_ID, range=RANGE_NAME, valueInputOption='USER_ENTERED', body=body).execute()
	#			print('Writing to {0}'.format(sheet_title))
		print('all done')
		#print(sheet_values)

	def get_latest_date_from_sheet(self, segment_type):
		''' Retrieve the latest date from Google Sheet for a specific segment category. '''
		
		try:
			# specific cell of the latest segment date in sheet
			range_of_date = segment_type + '!B2:B2'

			# request a ValueRange object
			request = self.spreadsheet.values().get(spreadsheetId=self.SPREADSHEET_ID, range=range_of_date)

			# response to request
			response = request.execute()

			# parse date from response
			latest_sheet_segment_date = response.get('values', [])[0][0]

			return latest_sheet_segment_date

		except Exception as e:
			logging.error(e, exc_info=True)


	def get_db_rows_greater_than(self, segment_type, latest_sheet_segment_date):

		import local_db
		database = local_db.Local_Database()
		database.cursor.execute(''' SELECT segment_type, air_date, anchors FROM show_data WHERE segment_type = ? AND air_date > ? ORDER BY air_date DESC''', (segment_type, latest_sheet_segment_date))
		database_entries = database.cursor.fetchall()

		return tuple(database_entries)
	
	def update_google_sheet(self, segment_type, sheetid, db_rows, num_of_db_rows):

		rangE = segment_type + '!A2:J' + str(num_of_db_rows + 1)
		values = db_rows

		body2 = {
			'requests': [
			{
				'insertRange': {
					'range': {
						'sheetId': sheetid,
						'startRowIndex': 1,
						'endRowIndex': num_of_db_rows+1
						},
					'shiftDimension': 'ROWS'
				}
			}
			]
		}
		request2 = self.spreadsheet.batchUpdate(spreadsheetId=self.SPREADSHEET_ID, body=body2).execute()
		print(request2)


		# valueRange object
		data = [
			{
				'range': rangE,
				'values': values,
				'majorDimension': 'ROWS'
			}] # additional ValueRange objects here

		# body of batchUpdate request must be a BatchUpdateValuesRequest object, 
		# which contains a ValueInputOption and a list of RangeValue objects
		body = {
			'valueInputOption': 'USER_ENTERED',
			'data': data
		}
		request = self.spreadsheet.values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID, body=body).execute()
		print(request)

	#result = sheets.values().append(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME2, valueInputOption='RAW', insertDataOption='INSERT_ROWS', body=body).execute()

	#print(result.get('updatedCells'))

if __name__ == '__main__':
	g = Google_Sheets_Filler()
	#our_list = g.get_sheet_titles_and_sheetIds()
	#print(our_list)
	#date = g.get_latest_date_from_sheet('Closing Remarks')
	#db_rows = g.get_db_rows_greater_than('Closing Remarks', date)
	#g.update_google_sheet('Closing Remarks', db_rows, len(db_rows))


	# 1) get sheet list with sheet IDs [{'title': 'One on One', 'sheetId': 34578345897}, ...]
	############ do the following for each segment ###################
	# 2) get latest date from sheet
	# 3) get database rows greater than that sheet date
	# 4) update google sheet with those rows
		#range_of_date = segment_type + '!2:2'
		#request = self.spreadsheet.values().get(spreadsheetId=self.SPREADSHEET_ID, range=range_of_date).execute()
		#rows = request.get('values', [])
		#print(rows)
	#########################################################################
		#range_names = [x + '!B2:B2' for x in sheet_titles]
		#result = self.sheets.values().batchGet(spreadsheetId=self.SPREADSHEET_ID, ranges=range_names).execute()
		#ranges = result.get('valueRanges', [])
		##print('{0} ranges retrieved.'.format(len(ranges)))
		#for r in ranges:
		#	if r.get('values'):
		#		print(r.get('values'), r.get('range'))
		##print(ranges)

	###	body = {
	###		'requests': [
	###		{
	###			'insertRange': {
	###				'range': {
	###					'sheetId': '946272867',
	###					'startRowIndex': 1,
	###					#'endRowIndex': 2,
	###					'startColumnIndex': 0
	###					#'endColumnIndex': 3
	###					},
	###					'shiftDimension': 'ROWS'
	###				}
	###			},
	###			'values': data_to_insert
	###		#	{
	###		#		'pasteData': {
	###		#			'data': 'shitty tst, brosef, a delimiter lol',
	###		#			'type': 'PASTE_VALUES',
	###		#			'delimiter': ',',
	###		#			'coordinate': {
	###		#				'sheetId': '946272867',
	###		#				'rowIndex': 2,
	###		#			}
	###		#		}
	###		#	}
	###		]
	###	}
		
		# InsertDimensionRequest
		#body = {
		#	'requests': [
		#	{
		#		'insertRangeRequest': {
		#			'range': {
		#				'sheetId': '946272867',
		#				'dimension': 'ROWS',
		#				'startIndex': 2,
		#				'endIndex': len_of_data
		#			},
		#			'inheritFromBefore': False
		#		}
		#	]
		#}
