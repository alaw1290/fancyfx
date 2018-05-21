import os
import csv
from datetime import datetime

def read_and_join_tick_csvs(csv_filepaths, raw_csv_schema, currency_pair_col_name, currency_pair_delimiter, bid_col_name, ask_col_name, date_time_col_name, date_time_format, date_time_length):

	line_pair_index = raw_csv_schema.index(currency_pair_col_name)
	line_bid_index = raw_csv_schema.index(bid_col_name)
	line_ask_index = raw_csv_schema.index(ask_col_name)
	line_dt_index = raw_csv_schema.index(date_time_col_name)
	
	filename_to_files = {}
	for filepath in csv_filepaths:
		fileobj = open(filepath)
		filename = os.path.basename(fileobj.name)
		filename_to_files[filename] = csv.reader(fileobj)
		filename_to_files[filename].__next__()

	next_smallest_pairs = []
	for filename in filename_to_files:

		line = filename_to_files[filename].__next__()
		line_date_time = line[line_dt_index]
		line_date_time = datetime.strptime(line_date_time[:date_time_length], date_time_format)
		line[line_dt_index] = line_date_time
		next_smallest_pairs.append((filename, line))

	ticktime_to_exchange_data = {}

	while len(next_smallest_pairs) > 0:
		print(next_smallest_pairs)
		next_tick_update = min(next_smallest_pairs, key= lambda x: x[1][line_dt_index])
		next_smallest_pairs.remove(next_tick_update)

		try:
			filename = next_tick_update[0]
			next_pair_line = filename_to_files[filename].__next__()
			line_date_time = next_pair_line[line_dt_index]

			try:
				line_date_time = datetime.strptime(line_date_time[:date_time_length], date_time_format)
			except ValueError:
				line_date_time = datetime.strptime(line_date_time[:date_time_length], "%Y-%m-%d %H:%M:%S")

			next_pair_line[line_dt_index] = line_date_time
			next_smallest_pairs.append((filename,next_pair_line))
		except StopIteration as e:
			filename_to_files[filename].close()
		except IndexError as e:
			pass

		current_dt = next_tick_update[1][line_dt_index]
		tick_update_pair = next_tick_update[1][line_pair_index].split(currency_pair_delimiter)
		curr_A, curr_B = tick_update_pair
		tick_bid_val = float(next_tick_update[1][line_bid_index])
		tick_ask_val = float(next_tick_update[1][line_ask_index])

		ticktime_to_exchange_data[current_dt] = {}
		ticktime_to_exchange_data[current_dt][curr_A] = {}
		ticktime_to_exchange_data[current_dt][curr_B] = {}
		ticktime_to_exchange_data[current_dt][curr_A][curr_B] = tick_bid_val
		ticktime_to_exchange_data[current_dt][curr_B][curr_A] = 1.0/tick_ask_val

		for pair in next_smallest_pairs:
			tick_update_pair = pair[1][line_pair_index].split(currency_pair_delimiter)
			curr_A, curr_B = tick_update_pair
			tick_bid_val = float(pair[1][line_bid_index])
			tick_ask_val = float(pair[1][line_ask_index])

			if curr_A not in ticktime_to_exchange_data[current_dt]:
				ticktime_to_exchange_data[current_dt][curr_A] = {}

			if curr_B not in ticktime_to_exchange_data[current_dt]:
				ticktime_to_exchange_data[current_dt][curr_B] = {}

			ticktime_to_exchange_data[current_dt][curr_A][curr_B] = tick_bid_val
			ticktime_to_exchange_data[current_dt][curr_B][curr_A] = 1.0/tick_ask_val

	return ticktime_to_exchange_data




