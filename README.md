# pairs-bot

A statistical arbitrage experiment on Shell (SHEL.L) and BP (BP.L), two closely related UK oil majors. It tracks the spread between their log prices, measures how far it has stretched from its recent average as a z-score, and trades the spread back towards the mean.

Built in Python with [backtrader](https://www.backtrader.com/) and Yahoo Finance data via [yfinance](https://github.com/ranaroussi/yfinance).

## How it works

1. **Data:** 60 days of 5-minute bars for both stocks (Yahoo's limit for intraday history).
2. **Spread:** log(SHEL) − log(BP).
3. **Z-score:** the spread minus its rolling mean, divided by its rolling standard deviation.
4. **Signals** (`signals.py`):
   - z above the entry level: short the spread (sell SHEL, buy BP)
   - z below minus the entry level: long the spread (buy SHEL, sell BP)
   - |z| back inside the exit level: close both legs
   - |z| beyond the stop level: close both legs (stop loss)

The backtest runs with a 240-bar window (about 4 hours), entry at |z| = 4, exit at 1 and stop at 6, a £500 account, no commission and 0.02% slippage.

## Files

| File | What it does |
| --- | --- |
| `fetch_prices.py` | Downloads the price data and prints the latest bars |
| `compute_zscore.py` | Computes the spread and its rolling z-score |
| `plot_zscore.py` | Plots the z-score with threshold lines |
| `signals.py` | The entry and exit rules, kept separate so they can be tested |
| `test_signals.py` | Checks the rules against known cases |
| `pairs_strategy.py` | The backtrader strategy |
| `run_backtest.py` | Runs the backtest and prints returns, Sharpe ratio, drawdown and trade statistics |

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python test_signals.py           # rule checks
python plot_zscore.py            # look at the spread
python run_backtest.py           # full backtest with charts
```

## Known limitations

- **Log prices in the backtest.** `run_backtest.py` passes log prices to backtrader as if they were prices, so position sizes and P&L are not in real pounds. The signals are right; the money figures are not. The fix is to feed raw prices and compute the spread inside the strategy.
- **Equal share counts.** Both legs trade the same number of shares rather than a hedge ratio from a regression, so the position is not market-neutral.
- **Short history.** 60 days of intraday data is too little to judge the strategy, and the parameters were tuned on the same period they are tested on.
- **Different settings in the exploration scripts.** `compute_zscore.py` and `plot_zscore.py` use a 60-bar window and ±2 thresholds, while the backtest uses 240 bars and ±4.

## Licence

MIT. See [LICENSE](LICENSE). This is a learning project, not investment advice.
