# fancyfx
python/d3.js/mongodb visualization tool of arbitrage in historical and current forex tick data

# background
currencies in scope are: 
- AUD
- CAD
- CHF
- EUR
- GBP
- USD
- JPY
- NZD

all currencies in scope have exchange rates for all other currencies, thus this forms a complete graph with 64 connections

the bellman ford algorithm can be used to detect negative cycles in a network with weighted edges

using -1 * log(exchange rates) as edge weights, use the bellman ford algorithm to find instances of arbitrage

# current stage
- scrape gain capital historical rate data for every exchange rate in scope for the year of 2017
- transform tick data for each currency table to one unified table with every tick for every currency
- load in transformed data to mongoDB server 
