import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import time



BINANCE_API_BASE = "https://api.binance.com"
BINANCE_KLINES_ENDPOINT = "/api/v3/klines"


def get_klines(symbol, interval, start_time, end_time):
    url = BINANCE_API_BASE + BINANCE_KLINES_ENDPOINT
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time
    }
    response = requests.get(url, params=params)
    return response.json()


def get_price_change(eth_prices, btc_prices):
    if len(eth_prices) < 61 or len(btc_prices) < 61:
        return None

    eth_prices = np.array(eth_prices).reshape(-1, 1)
    btc_prices = np.array(btc_prices).reshape(-1, 1)

    model = LinearRegression().fit(btc_prices, eth_prices)
    eth_resid = eth_prices - model.predict(btc_prices)

    price_change = (eth_resid[-1] - eth_resid[-61]) / eth_resid[-61]

    return price_change[0]


def track_price_movement():
    while True:
        now = int(datetime.now().timestamp() * 1000)
        one_hour_ago = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)

        eth_klines = get_klines("ETHUSDT", "1m", one_hour_ago, now)
        btc_klines = get_klines("BTCUSDT", "1m", one_hour_ago, now)

        eth_prices = [float(kline[1]) for kline in eth_klines]
        btc_prices = [float(kline[1]) for kline in btc_klines]

        price_change = get_price_change(eth_prices, btc_prices)

        if price_change is not None:#and abs(price_change) >= 0.01:
            print(f"Собственное изменение цены ETHUSDT: {price_change * 100:.2f}%")

        time.sleep(10)

track_price_movement()
