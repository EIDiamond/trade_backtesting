## Description
Historical backtesting tool based on historical market data.

The main goal is to use the tool with [invest-bot](https://github.com/EIDiamond/invest-bot) project.
Test and tune strategies for the bot on historical market data. 

## Before Start
### Dependencies

- [Tinkoff Invest Python gRPC client](https://github.com/Tinkoff/invest-python)
<!-- termynal -->
```
$ pip install tinkoff-investments
```

- [matplotlib](https://matplotlib.org)
<!-- termynal -->
```
$ pip install -U matplotlib
```

- [pandas](https://pandas.pydata.org)
<!-- termynal -->
```
$ pip install pandas
```

### Required configuration (minimal)
1. Open `settings.ini` file
2. Specify data provider section `DATA_PROVIDER`

### Run
Recommendation is to use python 3.10. 

Run main.py

## Configuration
Configuration can be specified via [settings.ini](settings.ini) file.

### Section COMMISSION
Specify `EVERY_ORDER_PERCENT` to calculate broker commission. 
By default, it's already specified for 'Инвестор' tariff in Tinkoff broker. 

### Section TEST_STRATEGY
Detailed settings for test strategy on historical candles.    

- `STRATEGY_NAME` - name of algorithm
- `TICKER` - ticker name 
- `FIGI` - figi of stock. Required for API
- `MAX_LOTS_PER_ORDER` - Maximum count of lots per order

### Section TEST_STRATEGY_SETTINGS
Detailed settings for strategy. Strategy class reads and parses settings manually.  

Note: Only one strategy in configuration can be specified.

### Section DATA_PROVIDER
Specify `NAME` of data provider:
- `TinkoffHistoric` -  using Tinkoff broker historical candles.
Candles are downloading via [Tinkoff Invest Python gRPC client](https://github.com/Tinkoff/invest-python) api.
- `TinkoffDownloaded` - using pre downloaded market data by 
the [tinkoff_market_data_collector](https://github.com/EIDiamond/tinkoff_market_data_collector) project

Specify test period by `FROM_DAYS` - count of days from now to past.

### Section DATA_PROVIDER_SETTINGS
#### TinkoffHistoric
Specify `TOKEN` and `APP_NAME` for [Тинькофф Инвестиции](https://www.tinkoff.ru/invest/) api.
#### TinkoffDownloaded
Specify `ROOT_PATH` for pre downloaded market data. 

## Trade emulator
The trade strategy is testing on different trade emulators.  
The tool has two different trade emulators: MovingStopEmulator and StopTakeEmulator.
Both emulators are being used while testing to see the difference in profit summary. 

### StopTakeEmulator
- Strategy analyses candles and returns signal (long or short) if needed  
- If signal exists, last price is being used to check take profit or stop loss price levels from signal
- If stop or take price levels are confirmed, strategy will start find signals again

### MovingStopEmulator
- Strategy analyses candles and returns signal (long or short) if needed  
- If signal exists, last price is being used to check stop loss price level from signal
- If last price is moving to the signal direction (long or short) when stop price level is moving also
- If stop price level are confirmed, strategy will start find signals again
- (Configurable) The trade emulator is able to set stop to no loss position. 

## How to add a new strategy
- Write a new class with trade logic
- The new class must have IStrategy as super class 
- Give a name for the new class
- Extend StrategyFactory class by the name and return the new class by the name
- Specify new settings in settings.ini file. Put the new class name in `STRATEGY_NAME`
- Test the new class on historical candles

## Test results
Detailed test results can be viewed in log file. All detailed information are written after all tests. 
Also, for better visualisation purposes total summary information represented via matplotlib in the end. 

All results have commission details. 

## RSI_CALCULATION example
- Just an example how you can develop your own indicator and use it by tool. 

## Use case
1. Download market data using [tinkoff_market_data_collector](https://github.com/EIDiamond/tinkoff_market_data_collector) project
2. Research data and find an idea for trade strategy using [analyze_market_data](https://github.com/EIDiamond/analyze_market_data) project
3. Test and tune your trade strategy using [trade_backtesting](https://github.com/EIDiamond/trade_backtesting) project
4. Trade by [invest-bot](https://github.com/EIDiamond/invest-bot) and your own strategy.
5. Profit!

### Example
Your can find example in code:
- Let's imagine your have great idea to invent your own idicator. Rsi idicator was selected for example.
- RSI Calculation alghoritm has been written for [research tool](https://github.com/EIDiamond/analyze_market_data/blob/main/analyze/rsi_calculation/rsi_calculation_analyze.py)
- It has been tested by [backtesting](https://github.com/EIDiamond/trade_backtesting/blob/main/trade_system/strategies/rsi_example/rsi_strategy.py)
- And now you are able to make your desicion.


## Logging
All logs are written in logs/test.log.
Any kind of settings can be changed in main.py code

## Project change log
[Here](CHANGELOG.md)

## Disclaimer
The author is not responsible for any errors or omissions, or for the trade results obtained from the use of this tool. 
