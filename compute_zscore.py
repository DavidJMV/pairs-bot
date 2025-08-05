import pandas as pd
import numpy as np
import yfinance as yf

# 1. Download data
df = yf.download(
    tickers=['SHEL.L', 'BP.L'],
    period='60d',
    interval='5m',
    auto_adjust=True,
    progress=False
)

prices = df['Close'].dropna()

# 2. Compute log prices
log_prices = np.log(prices)

# 3. Compute spread: log(SHEL) – log(BP)
spread = log_prices['SHEL.L'] - log_prices['BP.L']

# 4. Rolling window parameters
window = 60  # bars

# 5. Rolling mean and standard deviation
mu = spread.rolling(window).mean()
sigma = spread.rolling(window).std()

# 6. Compute z-score
zscore = (spread - mu) / sigma

# 7. Show the last 5 values
print("Latest Z-Scores:")
print(zscore.dropna().tail())