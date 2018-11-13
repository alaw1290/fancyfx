# data merger package

purpose: used to merge the exchange rate tick data from the raw data directory ordered by tick timestamps and split by currencies

## to setup the scraper

add a config file in the same level as the init script with the information below:

```
data_directory = '.../fancyfx/mongo/raw_data'
raw_csv_schema = ['lTid','cDealable','CurrencyPair','RateDateTime','RateBid','RateAsk']
currency_pair_col_name = 'CurrencyPair'
currency_pair_delimiter = "/"
bid_col_name = 'RateBid'
ask_col_name = 'RateAsk'
date_time_col_name = "RateDateTime"
# 2017-01-02 02:01:35.037000000
date_time_format = "%Y-%m-%d %H:%M:%S.%f"
date_time_length = 26
```


## to run the scraping process

this python codeblock will import and run the merger (ensure you have a config.py which contains the information for getting to the driver and where to put the downloads)


```
import itertools
currencies_list = ['AUD','CAD','CHF','EUR','GBP','USD','JPY','NZD']
import data_merger
data_merger.run_merger(currencies_list,'2017')
```