import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# 1. Fetch 60 days of 5-minute bars
df = yf.download(
    tickers=['SHEL.L', 'BP.L'],
    period='60d',
    interval='5m',
    auto_adjust=True,
    progress=False
)

prices = df['Close'].dropna()

# 2. Compute log-price spread & rolling stats
spread = np.log(prices['SHEL.L']) - np.log(prices['BP.L'])
window = 60
mu    = spread.rolling(window).mean()
sigma = spread.rolling(window).std()
zscore = (spread - mu) / sigma

# 3. Plot z-score with thresholds
ax = zscore.plot(figsize=(12, 6), title='SHEL–BP Rolling Z-Score')  # pandas wrapper around plt.plot :contentReference[oaicite:0]{index=0}
ax.axhline( 2.0, color='grey', linestyle='--')  # entry threshold :contentReference[oaicite:1]{index=1}
ax.axhline( 0.5, color='grey', linestyle='--')
ax.axhline(-0.5, color='grey', linestyle='--')
ax.axhline(-2.0, color='grey', linestyle='--')
ax.set_xlabel('Date')
ax.set_ylabel('Z-Score')
plt.tight_layout()
plt.show()  # renders the chart in most IDEs and Jupyter :contentReference[oaicite:2]{index=2}