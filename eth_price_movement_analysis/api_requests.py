from typing import List, Dict
import aiohttp


async def get_data(url: str) -> Dict:
    """
    Fetches the current data of a cryptocurrency from the specified url.

    :param url: The url from which to fetch the price.
    :return: A dictionary containing the fetched data.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
        return data
    except aiohttp.ClientError as e:
        print(f"An error occurred while fetching data: {str(e)}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return {}


async def get_hist_data(url: str) -> List[float]:
    """
    Fetches the historical data of a cryptocurrency from the specified url.

    :param url: The url from which to fetch the historical data.
    :return: A list of closing prices.
    """
    data = await get_data(url)
    # The closing price is the fifth item in each data point.
    close_prices = [float(item[4]) for item in data]
    return close_prices
