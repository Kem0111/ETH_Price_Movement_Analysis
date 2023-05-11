import asyncio
import json
from collections import deque

import numpy as np
import pandas as pd
import websockets


# async def get_price(symbol):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f'https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}') as response:
#             data = await response.json()
#             return data


# async def run():
#     price_history = {'ETH': [], 'BTC': []}
#     window_size = 60
#     price_threshold = 0.01

#     while True:
#         eth_data, btc_data = await asyncio.gather(
#             get_price('ETHUSDT'),
#             get_price('BTCUSDT')
#         )

#         price_history['ETH'].append(float(eth_data['lastPrice']))
#         price_history['BTC'].append(float(btc_data['lastPrice']))

#         if len(price_history['ETH']) >= window_size:
            # Создаем объект DataFrame на основе массивов цен на ETH и BTC.
            # Затем вычисляем процентное изменение цен на каждую криптовалюту,
            # используя метод pct_change(). Этот метод позволяет нам измерять
            # изменения цен в процентном отношении, что учитывает различия в
            # масштабах и изменчивости переменных, и облегчает сравнение
            # изменений во времени.
            # df = pd.DataFrame({'ETH': price_history['ETH'], 'BTC': price_history['BTC']})
            # df['ETH_pct_change'] = df['ETH'].pct_change()
            # df['BTC_pct_change'] = df['BTC'].pct_change()
            # # Удаляем строки с пропущенными значениями в объекте DataFrame `df`
            # df.dropna(inplace=True)
            # # Создаем независимую переменную MAJOR, представляющую изменение
            # # цены BTC, и зависимую переменную minor, представляющую
            # # изменение цены ETH
            # MAJOR = sm.add_constant(df['BTC_pct_change'])
            # minor = df['ETH_pct_change']
            # # Используем метод OLS() из библиотеки statsmodels.api для
            # # построения модели линейной регрессии между переменными MAJOR и
            # # minor и оценки коэффициентов регрессии.
            # model = sm.OLS(minor, MAJOR).fit()
            # # Используем ранее построенную модель линейной регрессии,
            # # чтобы прогнозировать, как изменение цены BTC влияет на изменение
            # # цены ETH. Затем мы вычисляем остатки, которые
            # # представляют разницу между фактическими значениями изменения
            # # цены ETH и прогнозными значениями, которые были вычислены
            # # на основе модели линейной регрессии.
            # df['predicted_eth_pct_change'] = model.predict(MAJOR)
            # df['residuals'] = df['ETH_pct_change'] - df['predicted_eth_pct_change']

            # independent_eth_pct_change = df['residuals'].iloc[-1]
            # if abs(independent_eth_pct_change) >= price_threshold:
            #     print(f"Цена ETH изменилась на {independent_eth_pct_change * 100:.2f}% за последние 60 минут")

            #     current_eth_price = price_history['ETH'][-1]
            #     independent_eth_price = current_eth_price * (1 + independent_eth_pct_change)

            #     print(f"Фактическая цена ETH: {current_eth_price}")
            #     print(f"Цена ETH на основе собственного движения: {independent_eth_price}")

            #     print(f"Собственное движение цены ETH: {independent_eth_pct_change}")

            # price_history['ETH'] = price_history['ETH'][-window_size:]
            # price_history['BTC'] = price_history['BTC'][-window_size:]
            # await asyncio.sleep(60)


# asyncio.run(run())


ETH_URL = 'wss://fstream.binance.com/ws/ethusdt@trade'
BTC_URL = 'wss://fstream.binance.com/ws/btcusdt@trade'
PRICE_CHANGE_THRESHOLD = 0.01
price_history = {'ETH': deque(maxlen=60 * 30), 'BTC': deque(maxlen=60 * 30)}
price_history_lock = asyncio.Lock()



async def tokenusdt_handler(url, token):

    async with websockets.connect(url) as websocket:
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            tokenusdt_price = float(data['p'])

            async with price_history_lock:
                price_history[token].append(tokenusdt_price)

            if token == 'ETH':
                await analyze_price_movements()

            await asyncio.sleep(2)


async def analyze_price_movements():
    async with price_history_lock:
        if len(price_history['ETH']) < 2:
            return

        df = pd.DataFrame({'ETH': price_history['ETH'], 'BTC': price_history['BTC']}).dropna()
        eth_prices = np.array(df['ETH'])
        btc_prices = np.array(df['BTC'])

        eth_prices_pct_change = (eth_prices[-1] - eth_prices[0]) / eth_prices[0]
        btc_prices_pct_change = (btc_prices[-1] - btc_prices[0]) / btc_prices[0]
        eth_independent_pct_change = eth_prices_pct_change - btc_prices_pct_change

        if abs(eth_independent_pct_change) >= PRICE_CHANGE_THRESHOLD:
            print(f"Собственное движение цены ETH: {eth_independent_pct_change * 100:.2f}% за последние 60 минут.")


async def main():
    await asyncio.gather(tokenusdt_handler(ETH_URL, 'ETH'), tokenusdt_handler(BTC_URL, 'BTC'))


asyncio.run(main())
