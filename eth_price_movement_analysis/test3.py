import asyncio
import json
from collections import deque
import statsmodels.api as sm
import numpy as np
import pandas as pd
import websockets
from datetime import datetime
import aiohttp

eth_url = "https://fapi.binance.com/fapi/v1/ticker/price?symbol=ETHUSDT"
btc_url = "https://fapi.binance.com/fapi/v1/ticker/price?symbol=BTCUSDT"
eth_hist_url = "https://fapi.binance.com/fapi/v1/klines?symbol=ETHUSDT&interval=1m&limit=60"
btc_hist_url = "https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1m&limit=60"


async def get_price(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    return data

async def get_hist_data(url):
    data = await get_price(url)
    close_prices = [float(item[4]) for item in data]
    return close_prices

def calculate_independent_prices(eth_prices, btc_prices, eth):
    btc_prices = sm.add_constant(btc_prices)
    model = sm.OLS(eth_prices, btc_prices).fit()
    price_changes = eth_prices - model.predict(btc_prices)
    independent_prices = [eth]
    for i in range(1, len(price_changes)):
        independent_price = independent_prices[i-1] + (independent_prices[i-1] * price_changes[i] / 100)
        independent_prices.append(independent_price)

    return independent_prices[-1], independent_prices

def calculate_price_changes(prices):
    # Вычисляем процентное изменение цены для каждого последующего значения
    price_changes = [((prices[i] - prices[i-1]) / prices[i-1]) * 100 for i in range(1, len(prices))]

    return price_changes


async def main():
    price_history = {'ETHUSDT': deque(maxlen=60), 'BTCUSDT': deque(maxlen=60)}

    eth_hist_data, btc_hist_data = await asyncio.gather(
        get_hist_data(eth_hist_url),
        get_hist_data(btc_hist_url)
    )
    price_history['ETHUSDT'].extend(eth_hist_data)
    price_history['BTCUSDT'].extend(btc_hist_data)

    while True:
        eth_data, btc_data = await asyncio.gather(
            get_price(eth_url),
            get_price(btc_url)
        )
        price_history['ETHUSDT'].append(float(eth_data['price']))
        price_history['BTCUSDT'].append(float(btc_data['price']))

        eth_price_changes = calculate_price_changes(list(price_history['ETHUSDT']))
        btc_price_changes = calculate_price_changes(list(price_history['BTCUSDT']))

        independent_price, a = calculate_independent_prices(eth_price_changes,
                                                            btc_price_changes,
                                                            price_history['ETHUSDT'][0])
        print(f'Current ETH price: {eth_data["price"]}')
        print(f"Independent ETH price: {independent_price}")
        print(a)
        await asyncio.sleep(60)


asyncio.run(main())
