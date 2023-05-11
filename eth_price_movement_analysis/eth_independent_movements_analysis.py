import aiohttp
import asyncio
import pandas as pd
import datetime
import time
import statsmodels.api as sm


async def get_historical_data(symbol, interval, start_time, end_time):
    url = (f'https://api.binance.com/api/v3/klines?symbol={symbol}&'
           f'interval={interval}&startTime={start_time}&endTime={end_time}')

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    needed_columns = [0, 1, 4]
    filtered_data = [ [row[i] for i in needed_columns] for row in data]

    # Создайте DataFrame только с нужными столбцами
    df = pd.DataFrame(filtered_data, columns=[
        'open_time', 'open', 'close'
        ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    return df


async def days_ago_to_unix_time(days_ago):
    dt = datetime.datetime.now() - datetime.timedelta(days=days_ago)
    unix_time_ms = int(time.mktime(dt.timetuple()) * 1000)
    return unix_time_ms

symbol_eth = 'ETHUSDT'
symbol_btc = 'BTCUSDT'
interval = '1m'
days_ago_start = 0.044
days_ago_end = 0


async def main():
    start_time = await days_ago_to_unix_time(days_ago_start)
    end_time = await days_ago_to_unix_time(days_ago_end)

    eth_data, btc_data = await asyncio.gather(
        get_historical_data(symbol_eth, interval, start_time, end_time),
        get_historical_data(symbol_btc, interval, start_time, end_time)
    )
    return eth_data, btc_data


async def calculate_percent_changes(df):
    df['price_change'] = (
        (df['close'].astype(float) - df['open'].astype(float)) /
        df['open'].astype(float) * 100
    )
    return df


async def result():

    eth_data, btc_data = await main()
    eth_data = await calculate_percent_changes(eth_data)
    btc_data = await calculate_percent_changes(btc_data)
    MAJOR = btc_data['price_change']
    MINOR = eth_data['price_change']

    MAJOR = sm.add_constant(MAJOR)
    model = sm.OLS(MINOR, MAJOR).fit()
    eth_data['predicted_price_change'] = model.predict(MAJOR)
    eth_data['residuals'] = eth_data['price_change'] - eth_data['predicted_price_change']
    eth_data['adjusted_price_change'] = eth_data['residuals'] + eth_data['predicted_price_change']
    eth_data['independent_price'] = None
    eth_data.loc[0, 'independent_price'] = float(eth_data.loc[0, 'open'])
    for i in range(1, len(eth_data)):
        eth_data.loc[i, 'independent_price'] = eth_data.loc[i - 1, 'independent_price'] * (1 + eth_data.loc[i, 'adjusted_price_change'] / 100)

    print(eth_data)


async def main2():
    while True:
        await result()
        await asyncio.sleep(60)

asyncio.run(main2())
