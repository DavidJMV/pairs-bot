import pandas as pd
import yfinance as yf

# 1. Download 60 days of 5-minute bars for both tickers at once
df = yf.download(
    tickers=['SHEL.L', 'BP.L'],
    period='60d',
    interval='5m',
    auto_adjust=True,
    progress=False
)

# 2. Pull out the Close prices (auto_adjust makes 'Close' the total-return price)
prices = df['Close'].dropna()

# 3. Show the last 5 rows
print(prices.tail())

