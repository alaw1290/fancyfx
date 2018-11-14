import os
import csv
from datetime import datetime
from multiprocessing import Pool

def read_month_dir(dirpath, output_dir, output_name, files_per_worker = 2):
	'''
	Given the path to the month directory, reads and merges all csv files using a divide and conquer pattern
	calls divide conquer helper to recursively build final result
	'''
	try:
		os.mkdir(output_dir)
	except OSError as e:
		pass
	# call helper 
	divide_conquer_helper(dirpath, output_dir, output_name, files_per_worker, False,
				["lTid","cDealable","CurrencyPair","RateDateTime","RateBid","RateAsk"],
				"CurrencyPair",
				"/",
				"RateBid",
				"RateAsk",
				"RateDateTime",
				"%Y-%m-%d %H:%M:%S.%f",
				26,
				0)


def divide_conquer_helper(dirpath, output_dir, output_name, files_per_worker, delete_input_after,
				raw_csv_schema, # ["lTid","cDealable","CurrencyPair","RateDateTime","RateBid","RateAsk"]
				currency_pair_col_name, # "CurrencyPair"
				currency_pair_delimiter, # "/"
				bid_col_name, # "RateBid"
				ask_col_name, # "RateAsk"
				date_time_col_name, #"RateDateTime"
				date_time_format, #"%Y-%m-%d %H:%M:%S.%f"
				date_time_length, #26
				filename_counter):

	# get all datafiles paths in dirpath
	filepaths = []
	for file in os.listdir(dirpath):
		# make sure it is a csv
		if '.csv' in file:
			filepaths.append(os.path.join(dirpath, file))

	# set up output name
	output_name, output_extension = output_name.split('.')

	# divide step: split files into equal parts per worker
	worker_files = []

	i = 0
	while i < len(filepaths):
		worker_files.append(filepaths[i:i+files_per_worker])
		i += files_per_worker	

	assert i*files_per_worker >= len(filepaths)
	print(len(worker_files))

	# assign n processes with worker_files
	with Pool(len(worker_files)) as p:
		args = []
		for files in worker_files:
			args.append([
					files,
					os.path.join(output_dir, output_name + str(filename_counter)+ '.' + output_extension),
					raw_csv_schema, 
					currency_pair_col_name, 
					currency_pair_delimiter, 
					bid_col_name, 
					ask_col_name,
					date_time_col_name, 
					date_time_format, 
					date_time_length
				])
			filename_counter += 1
		p.starmap(join_files, args)

	# remove files from dirpath if true
	if delete_input_after:
		for filename in filepaths:
			os.remove(filename)

	# get all datafiles paths in output dir
	filepaths = os.listdir(output_dir)

	if len([i for i in filepaths if '.csv' in i]) > 1:
		# combine step continues
		divide_conquer_helper(output_dir, output_dir, output_name + '.' + output_extension, files_per_worker, True,
			['RateDateTime', 'CurrencyPair', 'RateBid', 'RateAsk'],
			"CurrencyPair",
			"/",
			"RateBid",
			"RateAsk",
			"RateDateTime",
			"%Y-%m-%d %H:%M:%S.%f",
			26,
			filename_counter)
		# pass
	else:
		# exit condition fufilled, final output reached
		return None


def join_files(	filepaths, 
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

	# dict filename (str) to next row in file (list)
	filename_to_nextrow = {}

	for filepath in filepaths:
		fileobj = open(filepath)
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

	with open(outpath, "w+", buffering=1) as file:
		writer = csv.DictWriter(file, fieldnames=['RateDateTime', 'CurrencyPair', 'RateBid', 'RateAsk'])
		writer.writeheader()

		# while there are any files with rows left in filename_to_nextrow
		while len(filename_to_nextrow) > 0:

			if len(filename_to_nextrow) == 1:
				# just get the only available key and write out that row
				filename = list(filename_to_nextrow.keys())[0]
				row = filename_to_nextrow[filename]
			else:
				# get next smallest datetime row from filename_to_nextrow
				filename, row = get_smallest_row(filename_to_nextrow)

			# save the row in writer
			writer.writerow({'RateDateTime': str(row[0].timestamp()), 
							'CurrencyPair': "%s/%s"%(row[1][0],row[1][1]), 
							'RateBid': row[2],
							'RateAsk': row[3]})

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

		# flush stream and ensure all bytes are witten out
		file.flush()
		os.fsync(file.fileno())

	return None


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

	except ValueError as e:
		print(filename)
		raise e


def parse_row(  row, 						# Raw:
				currency_pair_col_name,  	# "CurrencyPair"
				currency_pair_delimiter, 	# "/"						
				bid_col_name, 				# "RateBid"		
				ask_col_name, 				# "RateAsk"
				date_time_col_name, 		# "RateDateTime"
				date_time_format, 			# "%Y-%m-%d %H:%M:%S.%f"
				date_time_length): 			# 26
	"""
	parses a row from the currency pair csv
	returns a list of the parsed values 
	"""

	# get the currency names rates and timestamp
	try:
		cur_A, cur_B = row[currency_pair_col_name].split(currency_pair_delimiter)
		bid_rate = float(row[bid_col_name])
		ask_rate = float(row[ask_col_name])
		timestamp = row[date_time_col_name]
	except ValueError as e:
		print(row)
		raise e

	# parse timestamp 
	try:
		timestamp = datetime.strptime(timestamp[:date_time_length], date_time_format)
	except ValueError:
		try:
			timestamp = datetime.strptime(timestamp[:date_time_length], "%Y-%m-%d %H:%M:%S")
		except ValueError:
			timestamp = datetime.fromtimestamp(float(timestamp))

	# format of the returned row: time, currency pair, bid rate, ask rate
	return [timestamp, (cur_A,cur_B), bid_rate, ask_rate]

def main():
	

	year_path = '/Users/adrian/Desktop/stuff/fancyfx/db/data/raw/2017/'
	out_path = '/Users/adrian/Desktop/stuff/fancyfx/db/data/processed/2017/'
	for i,month_dir in enumerate(os.listdir(year_path)):
		read_month_dir(os.path.join(year_path, month_dir),
			os.path.join(out_path, month_dir),
			"data.csv",
			files_per_worker=4
			)


	# read_month_dir('/Users/adrian/Desktop/stuff/fancyfx/db/data/raw/2017/01 January',
	# 		'/Users/adrian/Desktop/stuff/fancyfx/db/data/processed/2017/01 January',
	# 		'test_jan_join.csv',
	# 		files_per_worker=4
	# 	)

	# read_month_dir('/Users/adrian/Desktop/stuff/fancyfx/db/data/raw/2017/01 January',
	# 		'/Users/adrian/Desktop/stuff/fancyfx/db/data/processed/2017/01 January',
	# 		'test_jan_join.csv',
	# 		files_per_worker=70
	# 	)

	# output_dir = '/Users/adrian/Desktop/stuff/fancyfx/db/data/processed/2017/01 January'
	# output_name = 'test_jan_join'
	# output_extension = 'csv'
	# files_per_worker = 4
	# filename_counter = 47

	# divide_conquer_helper(output_dir, output_dir, output_name + '.' + output_extension, files_per_worker, True,
	# 		['RateDateTime', 'CurrencyPair', 'RateBid', 'RateAsk'],
	# 		"CurrencyPair",
	# 		"/",
	# 		"RateBid",
	# 		"RateAsk",
	# 		"RateDateTime",
	# 		"%Y-%m-%d %H:%M:%S.%f",
	# 		26,
	# 		filename_counter)

if __name__ == '__main__':
	t = int(datetime.now().strftime('%s'))
	main()
	print("%s seconds"%str(int(datetime.now().strftime('%s'))) - int(t))

