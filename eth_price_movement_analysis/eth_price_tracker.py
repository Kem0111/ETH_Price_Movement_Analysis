import asyncio
from collections import deque
from typing import Dict, Deque
from api_requests import get_data, get_hist_data
from price_analysis import (calculate_independent_prices,
                            calculate_price_changes)

# URLs for real-time price and historical data for ETH and BTC
eth_url = "https://fapi.binance.com/fapi/v1/ticker/price?symbol=ETHUSDT"
btc_url = "https://fapi.binance.com/fapi/v1/ticker/price?symbol=BTCUSDT"
eth_hist_url = ("https://fapi.binance.com/fapi/v1/klines?symbol=ETHUSDT&"
                "interval=1m&limit=60")
btc_hist_url = ("https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&"
                "interval=1m&limit=60")
PRICE_CHANGE_THRESHOLD = 1


async def track_independent_eth_price():
    """
    Main function that fetches the current and historical prices of ETH and
    BTC, calculates the independent price of ETH, and prints a message
    whenever the independent price changes by 1% or more within
    the last 60 minutes.
    """
    price_history: Dict[str, Deque[float]] = {
        'ETHUSDT': deque(maxlen=60),
        'BTCUSDT': deque(maxlen=60)
    }
    independent_price_history = deque(maxlen=60)

    eth_hist_data, btc_hist_data = await asyncio.gather(
        get_hist_data(eth_hist_url),
        get_hist_data(btc_hist_url)
    )
    price_history['ETHUSDT'].extend(eth_hist_data)
    price_history['BTCUSDT'].extend(btc_hist_data)

    while True:
        eth_data, btc_data = await asyncio.gather(
            get_data(eth_url),
            get_data(btc_url)
        )
        price_history['ETHUSDT'].append(float(eth_data['price']))
        price_history['BTCUSDT'].append(float(btc_data['price']))

        eth_price_changes = calculate_price_changes(
            list(price_history['ETHUSDT'])
        )
        btc_price_changes = calculate_price_changes(
            list(price_history['BTCUSDT'])
        )

        independent_price = calculate_independent_prices(
            eth_price_changes,
            btc_price_changes,
            price_history['ETHUSDT'][0]
        )
        independent_price_history.append(independent_price)
        price_change = ((independent_price - independent_price_history[0])
                        / independent_price_history[0]) * 100
        if abs(price_change) >= PRICE_CHANGE_THRESHOLD:
            print(
                f"Independent ETH price changed by {price_change:.1f}% "
                f"over the last 60 minutes\n"
                f"ETHUSDT open price: {independent_price_history[0]}\n"
                f"ETHUSDT last price: {independent_price}")
        await asyncio.sleep(60)
