try:
	from .config import *
except ImportError as e:
	data_directory = ""
	raw_csv_schema = []
	date_time_col_name = ""
	date_time_format = ""
	date_time_length = 0
	raise Exception('Please ensure you have a config file properly configured as directed under the README of the data munger, otherwise the function will not peform as intended')


def run_munger(csv_filenames, data_directory=data_directory, raw_csv_schema=raw_csv_schema, date_time_col_name=date_time_col_name, date_time_format=date_time_format, date_time_length=date_time_length):
	import os
	from .munger import read_and_join_tick_csvs
	
	csv_fileobjs = []
	for filename in csv_filenames:
		file = open(os.path.join(data_directory,filename))
		csv_fileobjs.append(file)

	return read_and_join_tick_csvs(csv_fileobjs, 
		raw_csv_schema, 
		currency_pair_col_name, 
		currency_pair_delimiter, 
		bid_col_name, 
		ask_col_name, 
		date_time_col_name, 
		date_time_format, 
		date_time_length)