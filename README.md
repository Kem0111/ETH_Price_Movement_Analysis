<a href="https://codeclimate.com/github/Kem0111/ETH_Price_Movement_Analysis/maintainability"><img src="https://api.codeclimate.com/v1/badges/521f3e3d54f9f792d538/maintainability" /></a>

# Project Description

The "ETH Price Movement Analysis" project is designed to track Ethereum's price movement independently of Bitcoin. The program fetches current and historical prices of Ethereum (ETH) and Bitcoin (BTC), calculates the independent price movement of ETH, and prints a message whenever the independent price changes by 1% or more within the last 60 minutes. This is accomplished by factoring out the impact of BTC's price movements on ETH.

This project uses the Binance API to get real-time and historical data.

## How to Use

This project uses Poetry for dependency management. Make sure you have it installed before proceeding.

To use this project, follow these steps:

Clone the repository to your local machine:

```
git clone https://github.com/Kem0111/ETH_Price_Movement_Analysis.git
````
cd ETH_Price_Movement_Analysis

```
make install
make start
```

The program will now start tracking the independent price movement of ETH and print a message whenever the independent price changes by 1% or more within the last 60 minutes.  


## Note

The "ETH Price Movement Analysis" project is a tool designed to provide information about the independent price movement of Ethereum. It is not intended to provide financial advice. Please do your own research or consult a financial advisor before making any investment decisions.