# fancyfx
A personal continuation of a [previous cs591 project](https://github.com/alaw1290/591-hw/tree/master/final_project), the goal is to develop a python/d3.js/mongodb visualization tool of arbitrage in historical forex tick data to observe trends and predict opportunities

## background
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

## current stage
- [x] scrape gain capital historical rate data for every exchange rate in scope for the year of 2017
- [x] transform tick data for each currency table to one unified table with every tick for every currency
- [ ] EDA and network generation using notebooks

