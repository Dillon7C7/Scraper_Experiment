#!/usr/bin/env python3

import sqlite3
import logging

class Local_Database(object):

	def __init__(self, db_name='local_db.back'):
		self.db = ''
		self.cursor = ''
		self.db_name = db_name

		self.log_fmt = '%(filename)s - %(lineno)d - %(funcName)s - %(levelname)s - %(message)s'
		self.logger = logging.basicConfig(filename='LOGGING/DATABASE.log', filemode='w', format=self.log_fmt, level=logging.ERROR)

		try:

			# methods that we always want to run
			self.connect_to_database()
			self.create_table()

		except Exception as e:
			logging.error(e, exc_info=True)
	
	def connect_to_database(self):
		'''Connect to our local database.'''

		try:
			self.db = sqlite3.connect(self.db_name)
			self.cursor = self.db.cursor()
			self.db.commit()

		except Exception as e:
			logging.error(e, exc_info=True)

	# only one table, for now
	def create_table(self):
		'''Create our single table.'''
		try:
			self.cursor.execute('''
			CREATE TABLE IF NOT EXISTS show_data(id INTEGER PRIMARY KEY, segment_type TEXT, air_date TEXT, anchors TEXT) 
								''')
		#	self.cursor.execute('''
		#	CREATE TABLE IF NOT EXISTS show_data_new(id INTEGER PRIMARY KEY, segment_type TEXT, air_date TEXT, anchors TEXT, UNIQUE(segment_type, air_date, anchors))
		#						''')
			self.db.commit()

		except Exception as e:
			logging.error(e, exc_info=True)
	
	#BAAAILLL
######	def repair_db(self):
######		try:
######			self.cursor.execute(''' INSERT INTO show_data_new(segment_type, air_date, anchors) SELECT segment_type, air_date, anchors FROM show_data ''')
######			self.db.commit()
######
######		except Exception as e:
######			print(e)
######			print("fffuck")

	def get_errything(self):
		try:
			self.cursor.execute(''' SELECT segment_type, air_date, anchors FROM show_data ''')
			return self.cursor.fetchall()

		except Exception as e:
			print(e)
			print("fffuck")
			
	# fix later, data is a list of tuples
	def insert_many(self, data):
		'''Insert data into show_data table.'''

		try:
			self.cursor.executemany(''' INSERT INTO show_data(segment_type, air_date, anchors) VALUES(?,?,?) ''', data)
			self.db.commit()

		except Exception as e:
			logging.error(e, exc_info=True)
	
	def get_latest_date(self):
		'''Return the date of the latest air_date in database.'''

		try:
			# if no date is specified, grab the latest entry by date in database
			self.cursor.execute(''' SELECT segment_type, air_date, anchors FROM show_data ORDER BY air_date DESC LIMIT 1 ''')
			self.latest_date = self.cursor.fetchone()

			return self.latest_date[1]

		except Exception as e:
			logging.error(e, exc_info=True)



	def __del__(self):
		'''Close our database connection.'''

		try:
			self.db.commit()
			self.db.close()

		except Exception as e:
			logging.error(e, exc_info=True)
