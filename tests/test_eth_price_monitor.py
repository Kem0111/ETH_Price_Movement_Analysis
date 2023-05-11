import unittest
from eth_price_movement_analysis.eth_price_monitor import get_klines, get_price_change


class TestEthPriceMonitor(unittest.TestCase):
    def test_get_klines(self):
        # Пример тестового случая для функции get_klines
        symbol = "ETHUSDT"
        interval = "1m"
        start_time = 1620000000000
        end_time = 1620000600000

        klines = get_klines(symbol, interval, start_time, end_time)
        self.assertIsNotNone(klines)
        self.assertIsInstance(klines, list)

    def test_get_price_change(self):
        # Пример тестового случая для функции get_price_change
        eth_prices = [1000, 1005, 1010, 1020, 1030, 1035, 1040, 1045, 1050, 1060, 1065] * 6
        btc_prices = [10000, 10050, 10100, 10200, 10300, 10350, 10400, 10450, 10500, 10600, 10650] * 6

        price_change = get_price_change(eth_prices, btc_prices)
        self.assertIsNotNone(price_change)
        self.assertIsInstance(price_change, float)
