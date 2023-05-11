import statsmodels.api as sm
from typing import List


def calculate_independent_prices(eth_price_changes: List[float],
                                 btc_price_changes: List[float],
                                 eth_price: float) -> float:
    """
    Calculates the independent price of ETH by factoring out the price
    changes in BTC.

    :param eth_price_changes: A list of price changes for ETH.
    :param btc_price_changes: A list of price changes for BTC.
    :param eth_price: The current price of ETH.
    :return: The independent price of ETH.
    """
    # Adding a constant term to our model allows it to have a y-intercept
    MAJOR = sm.add_constant(btc_price_changes)
    # Fitting a linear regression model
    model = sm.OLS(eth_price_changes, MAJOR).fit()
    # Calculating the residuals (observed - predicted)
    price_changes = eth_price_changes - model.predict(MAJOR)
    # Initializing the list of independent prices with the current price of ETH
    independent_prices = [eth_price]
    for i in range(1, len(price_changes)):
        independent_price = (
            independent_prices[i-1] +
            (independent_prices[i-1] * price_changes[i] / 100)
        )
        independent_prices.append(independent_price)

    return independent_prices[-1]


def calculate_price_changes(prices: List[float]) -> List[float]:
    """
    Calculates the percentage price changes for each successive
    value in the given list.

    :param prices: A list of prices.
    :return: A list of percentage price changes.
    """
    price_changes = [
        ((prices[i] - prices[i-1]) / prices[i-1])
        * 100 for i in range(1, len(prices))
    ]

    return price_changes
