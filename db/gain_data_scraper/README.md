# gain data scraper package

purpose: used to scrape the exchange rate tick data from the gain data repository online and download all relevant zip files provided currencies and a year timeframe.

## to setup the scraper

add a config file in the same level as the init scrip with the information below:

```
downloads_directory = '.../fancyfx/mongo/raw_data'
webdriver_path = '.../fancyfx/mongo/gain_data_scraper/webdriver/chromedriver'
```


## to run the scraping process

this python codeblock will import and run the scraper to collect tick data using selenium chromedriver (ensure you have a config.py which contains the information for getting to the driver and where to put the downloads)


```
import itertools
currencies_list = ['AUD','CAD','CHF','EUR','GBP','USD','JPY','NZD']
currency_pairs = list(itertools.combinations(currencies_list, 2))
import gain_data_scraper
gain_data_scraper.scrape_for(currency_pairs,'2017')
```

in the directory with the year range, run the following terminal lines to unzip all files and collect the raw csvs containing tick data for each month

```
find . -name "*.zip" | while read filename; do unzip -o -d "`dirname "$filename"`" "$filename"; done;
find . -name "*.zip" -type f -delete
```