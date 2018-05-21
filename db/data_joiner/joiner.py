import os
import csv
from datetime import datetime

def join_pair_files(dirpath, 
					outpath,
					raw_csv_schema, # ["lTid","cDealable","CurrencyPair","RateDateTime","RateBid","RateAsk"]
					currency_pair_col_name, # "CurrencyPair"
					currency_pair_delimiter, # "/"
					bid_col_name, # "RateBid"
					ask_col_name, # "RateAsk"
					date_time_col_name, #"RateDateTime"
					date_time_format, #"%Y-%m-%d %H:%M:%S.%f"
					date_time_length): #26
	"""
	Given a list of filepaths of currency pairs in a month it will parse the ticks in order 
	Writes out a single csv with all the ticks in order for said month
	"""

	# dict filename (str) to file (csv.reader)
	filename_to_files = {}

	# get all datafiles paths in dirpath
	filepaths = os.listdir(dirpath)

	# dict filename (str) to next row in file (list)
	filename_to_nextrow = {}

	for filepath in filepaths:
		fileobj = open(os.path.join(dirpath, filepath))
		filename = os.path.basename(fileobj.name)
		filename_to_files[filename] = {'reader': csv.DictReader(fileobj, raw_csv_schema), 'fileobj':fileobj}
		next(filename_to_files[filename]['reader'])
		filename_to_nextrow[filename] = parse_row(
				next(filename_to_files[filename]['reader']),
				currency_pair_col_name, 
				currency_pair_delimiter, 
				bid_col_name, 
				ask_col_name, 
				date_time_col_name, 
				date_time_format,
				date_time_length
			)


	# with open(outpath) as file:
	# 	writer = csv.writer(file)
	writer = []

	# while there are any files with rows left in filename_to_nextrow
	while len(filename_to_nextrow) > 0:

		# get next smallest datetime row from filename_to_nextrow
		filename, row = get_smallest_row(filename_to_nextrow)

		# save the row in writer
		writer.append(row)

		# get the next row for file in filename_to_nextrow using filename_to_files
		update_row(filename, filename_to_nextrow, filename_to_files,
					currency_pair_col_name, 
					currency_pair_delimiter, 
					bid_col_name, 
					ask_col_name, 
					date_time_col_name, 
					date_time_format,
					date_time_length
					)

	return writer


def get_smallest_row(filename_to_nextrow):
	'''
	Given filename_to_nextrow, returns the filename and row of the next row in time
	returns a string and list
	'''

	# timestame is first element in val for each filename
	filename = min(filename_to_nextrow, key=lambda k: filename_to_nextrow[k][0])
	row = filename_to_nextrow[filename]

	return filename, row


def update_row(filename, filename_to_nextrow, filename_to_files,
				currency_pair_col_name, 
				currency_pair_delimiter, 
				bid_col_name, 
				ask_col_name, 
				date_time_col_name, 
				date_time_format,
				date_time_length
	):
	'''
	Given the filename to update and dicts filename_to_nextrow and filename_to_files, returns the updated filename_to_nextrow with the next row or removes the key if no more rows exist
	returns nothing, all changes done in memory
	'''
	try:
		# next row is available, replace val in filename_to_nextrow[filename]
		row = next(filename_to_files[filename]['reader'])
		filename_to_nextrow[filename] = parse_row(
				row,
				currency_pair_col_name, 
				currency_pair_delimiter, 
				bid_col_name, 
				ask_col_name, 
				date_time_col_name, 
				date_time_format,
				date_time_length
			)

	except StopIteration as e:
		# next row is not available, del key filename in filename_to_nextrow
		filename_to_files[filename]['fileobj'].close()
		del filename_to_nextrow[filename]


def parse_row(  row, 
				currency_pair_col_name, # "CurrencyPair"
				currency_pair_delimiter, # "/"
				bid_col_name, # "RateBid"
				ask_col_name, # "RateAsk"
				date_time_col_name, #"RateDateTime"
				date_time_format, #"%Y-%m-%d %H:%M:%S.%f"
				date_time_length): #26
	"""
	parses a row from the currency pair csv
	returns a list of the parsed values 
	"""

	# get the currency names rates and timestamp
	cur_A, cur_B = row[currency_pair_col_name].split(currency_pair_delimiter)
	bid_rate = float(row[bid_col_name])
	ask_rate = float(row[ask_col_name])
	timestamp = row[date_time_col_name]

	# parse timestamp to 
	try:
		timestamp = datetime.strptime(timestamp[:date_time_length], date_time_format)
	except ValueError:
		timestamp = datetime.strptime(timestamp[:date_time_length], "%Y-%m-%d %H:%M:%S")

	# format of the returned row: time, currency pair, bid rate, ask rate
	return [timestamp, (cur_A,cur_B), bid_rate, ask_rate]

