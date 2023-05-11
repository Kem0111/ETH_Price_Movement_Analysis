from eth_price_tracker import track_independent_eth_price
import asyncio


async def main():
    await track_independent_eth_price()


if __name__ == '__main__':
    asyncio.run(main())
