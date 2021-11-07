# Binance-Crypto-Trader-Bot

This simple bot will trade Crypto Automatically on the Binance exchange using either Bollinger Bands strategy or Double Bottoms Bollinger Bands strategy

Adjust settings in the config file:
Duration: the candle close time length. A 15m or 1h candle works best with either strategy
Rolling_Average: the number of candle closes to create a Rolling Average from. 21 is the default and what the Binance exchange displays their Bollinger bands at. A number range of 15 - 30 works best.
N_Standard_Deviation: the number of standard deviations from the rolling average to produce upper and lower bands
Coin_Unit: the coin partner that you wish to trade. ETHUSDT is the default
Strategy: bollinger_bands or double_bottom

You will need to create an API key in your Binance account. Then create an empty secret_config.ini file in the CryptoBot directory. Add the API keys to the secret_config.ini file as shown below:
API_KEY = <your_api_key_goes_here>
SECRET_KEY = <your_secret_key_goes_here>

You can test that your settings are working by opening a terminal where you would run the python code. Navigate to the CryptoBot directory and type the command:
python -m unittest test_Strategy.py

If you get an OK, then to start your bot, run the command:
python CryptoBot.py
