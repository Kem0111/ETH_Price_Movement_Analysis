import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from binance.client import Client
import time
import statsmodels.api as sm

# Initialize Binance client
client = Client('ETH', 'rtaW6vQ9GRQRsHUlm7DrG5Gupspawn0is0qkvBdCiESIKfGHdd7RzKMyy4vMWbjK')

# Initialize Linear Regression model
model = LinearRegression()

# Start with empty dataframes
eth_prices = pd.DataFrame()
btc_prices = pd.DataFrame()

while True:
    # Get current prices
    eth_price = float(client.get_symbol_ticker(symbol='ETHUSDT')['price'])
    btc_price = float(client.get_symbol_ticker(symbol='BTCUSDT')['price'])
    
    # Append to dataframes
    eth_prices = pd.concat([eth_prices, pd.DataFrame({'price': [eth_price]}, index=[pd.Timestamp.now()])])
    btc_prices = pd.concat([btc_prices, pd.DataFrame({'price': [btc_price]}, index=[pd.Timestamp.now()])])
    
    # Only keep last 60 minutes of data
    eth_prices = eth_prices.last('60Min')
    btc_prices = btc_prices.last('60Min')

    if len(eth_prices) > 1:
        # Fit regression model
        X = sm.add_constant(btc_prices)  # Adding a constant (intercept term) to our model
        model = sm.OLS(eth_prices, X).fit()
        
        # Calculate residuals
        residuals = eth_prices['price'] - model.predict(X)

        # Check if the last residual is more than 1%
        if np.abs(residuals.iloc[-1]) / eth_prices['price'].iloc[-2] > 0.01:
            print(f"Independent ETH price movement detected at {pd.Timestamp.now()}. Change: {residuals.iloc[-1]}")
    
    # Sleep for a while before fetching new prices
    time.sleep(1)
