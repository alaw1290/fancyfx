try:
	from .config import *
except ImportError as e:
	data_directory = ""
	output_directory = ""
	raw_csv_schema = []
	date_time_col_name = ""
	date_time_format = ""
	date_time_length = 0
	raise Exception('Please ensure you have a config file properly configured as directed under the README of the data munger, otherwise the function will not peform as intended')

def run_merger(currencies, year, data_directory=data_directory, output_directory=output_directory, raw_csv_schema=raw_csv_schema, date_time_col_name=date_time_col_name, date_time_format=date_time_format, date_time_length=date_time_length):
	import os
	import itertools
	import pickle
	from .merger import merge_csvs
	
	year_path = os.path.join(data_directory, year)
	for month_dir in os.listdir(year_path):
		if os.path.isdir(os.path.join(year_path, month_dir)):

			csv_filepaths= []
			month_path = os.path.join(year_path, month_dir)	
			for filename in os.listdir(month_path):
				if any([True if i in filename else False for i in currencies]):
					filepath = os.path.join(month_path, filename)
					csv_filepaths.append(filepath)

			month_tick_data = merge_csvs(csv_filepaths, 
					raw_csv_schema, 
					currency_pair_col_name, 
					currency_pair_delimiter, 
					bid_col_name, 
					ask_col_name, 
					date_time_col_name, 
					date_time_format, 
					date_time_length)

		filename = '_'.join(month_dir.split(' '))
		return month_tick_data
		# with open(os.path.join(output_directory, year, f"{filename}.pkl"), 'wb') as f:
		# 	pickle.dump(month_tick_data, f)
		# print(f'{filename} done')