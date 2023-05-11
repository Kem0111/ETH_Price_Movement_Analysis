import aiohttp
import asyncio
import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime

# Таймфрейм для проверки изменения цены
TIMEFRAME = 60

# Минимальное изменение цены для вывода сообщения
PRICE_CHANGE_THRESHOLD = 0.01


async def initialize_data():
    # Binance's historical klines endpoint
    url = 'https://api.binance.com/api/v3/klines'
    
    # parameters for the last 60 minutes of 1-minute klines
    params_eth = {
        'symbol': 'ETHUSDT',
        'interval': '1m',
        'limit': 60
    }
    params_btc = {
        'symbol': 'BTCUSDT',
        'interval': '1m',
        'limit': 60
    }

    # make the requests
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params_eth) as resp:
            data_eth = await resp.json()
        async with session.get(url, params=params_btc) as resp:
            data_btc = await resp.json()

    # extract the closing prices
    prices_eth = [{'time': datetime.fromtimestamp(int(kline[0])/1000), 'price': float(kline[4])} for kline in data_eth]
    prices_btc = [{'time': datetime.fromtimestamp(int(kline[0])/1000), 'price': float(kline[4])} for kline in data_btc]

    return pd.DataFrame(prices_eth), pd.DataFrame(prices_btc)


async def get_price(session, symbol):
    async with session.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}') as resp:
        data = await resp.json()
        return float(data['price'])


async def track_price():
    ETH_prices, BTC_prices = await initialize_data()

    async with aiohttp.ClientSession() as session:
        while True:
            # Получаем цены
            ETH_price = await get_price(session, 'ETHUSDT')
            BTC_price = await get_price(session, 'BTCUSDT')

            # Если в списке больше чем TIMEFRAME цен, удаляем старые
            if len(ETH_prices) >= TIMEFRAME:
                ETH_prices = ETH_prices.iloc[1:]
                BTC_prices = BTC_prices.iloc[1:]

            # Добавляем цены в списки
            ETH_prices.loc[datetime.now()] = ETH_price
            BTC_prices.loc[datetime.now()] = BTC_price

            # Вычисляем возврат и остатки регрессии
            ETH_return = ETH_prices['price'].pct_change().dropna()
            BTC_return = BTC_prices['price'].pct_change().dropna()
            X = sm.add_constant(BTC_return.values)
            model = sm.OLS(ETH_return.values, X)
            results = model.fit()
            residuals = results.resid
            print(ETH_prices)
            print(f'At {datetime.now()}, ETH price changed by {residuals[-1]*100:.6f}% independently from BTC.')
            # Если изменение цены превышает порог, выводим сообщение
            if np.abs(residuals[-1]) >= PRICE_CHANGE_THRESHOLD:
                print(f'At {datetime.now()}, ETH price moved by more than {PRICE_CHANGE_THRESHOLD*100}% independently from BTC.')

            # Задержка перед следующим запросом
            await asyncio.sleep(60)

loop = asyncio.get_event_loop()
loop.run_until_complete(track_price())
