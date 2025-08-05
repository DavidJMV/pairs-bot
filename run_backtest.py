import numpy as np
import yfinance as yf
import backtrader as bt
from pairs_strategy import PairsStrategy

if __name__ == '__main__':
    try:
        cerebro = bt.Cerebro()

        print("Downloading data...")
        # 1. Download 60 days of 5-minute bars for both tickers
        df = yf.download(
            tickers=['SHEL.L', 'BP.L'],
            period='60d',
            interval='5m',
            auto_adjust=True,
            progress=False
        )
        
        # 2. Extract Close prices and drop any NaNs
        df_close = df['Close'].dropna()
        print(f"Data range: {df_close.index[0]} to {df_close.index[-1]}")
        print(f"Total bars: {len(df_close)}")

        # 3. Compute log prices (natural log)
        df_log = np.log(df_close)

        # 4. Create separate DataFrames for each stock with proper OHLCV structure
        shell_df = df_log[['SHEL.L']].copy()
        shell_df.columns = ['close']
        shell_df['open'] = shell_df['close']
        shell_df['high'] = shell_df['close'] 
        shell_df['low'] = shell_df['close']
        shell_df['volume'] = 1000

        bp_df = df_log[['BP.L']].copy()
        bp_df.columns = ['close']
        bp_df['open'] = bp_df['close']
        bp_df['high'] = bp_df['close']
        bp_df['low'] = bp_df['close'] 
        bp_df['volume'] = 1000

        data_shell = bt.feeds.PandasData(dataname=shell_df)
        data_bp = bt.feeds.PandasData(dataname=bp_df)

        cerebro.adddata(data_shell)
        cerebro.adddata(data_bp)

        # 5. Add your pairs strategy - parameters should match strategy file
        cerebro.addstrategy(PairsStrategy, 
                           window=240,      # 4 hour window for very stable signals
                           entry_z=4.0,     # Only extreme signals
                           exit_z=1.0,      # Let winners run to mean reversion
                           max_z=6.0)       # INCREASED: Allow proper mean reversion before stop loss

        # 6. Test with ZERO commissions (Trading 212, Freetrade, etc.)
        cerebro.broker.setcommission(commission=0.0, margin=1.0)  # Commission-free trading
        cerebro.broker.set_slippage_perc(perc=0.0002)  # Only spread costs

        # Add analyzers for comprehensive performance analysis
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown') 
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        # 7. Back to £500 account
        initial_cash = 500
        cerebro.broker.setcash(initial_cash)
        
        print(f"\nRunning backtest with £{initial_cash} initial capital...")
        print("Note: This simulates commission-free trading (Trading 212, Freetrade)")
        results = cerebro.run()
        strat = results[0]
        
        final_value = cerebro.broker.getvalue()
        pnl = final_value - initial_cash
        total_return = (pnl / initial_cash) * 100

        # Print comprehensive results with time analysis
        print(f"\n{'='*50}")
        print("BACKTEST RESULTS - COMMISSION-FREE SIMULATION")
        print(f"{'='*50}")
        print(f'Initial Capital: £{initial_cash:.2f}')
        print(f'Final Portfolio Value: £{final_value:.2f}')
        print(f'Total P&L: £{pnl:+.2f}')
        print(f'Total Return: {total_return:+.2f}%')
        
        # Calculate time period and annualized return
        start_date = df_close.index[0]
        end_date = df_close.index[-1]
        days = (end_date - start_date).days
        print(f'Backtest Period: {days} days ({days/365:.1f} years)')
        
        # Annualized return calculation
        if days > 0:
            annualized_return = ((final_value / initial_cash) ** (365/days) - 1) * 100
            print(f'Annualized Return: {annualized_return:+.1f}%')

        # Extract analyzer results
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        returns = strat.analyzers.returns.get_analysis()
        trades = strat.analyzers.trades.get_analysis()

        print(f"\nPERFORMANCE METRICS")
        print(f"{'='*50}")
        sharpe_ratio = sharpe.get('sharperatio', None)
        if sharpe_ratio is not None:
            print(f"Sharpe Ratio: {sharpe_ratio:.3f}")
        else:
            print("Sharpe Ratio: N/A")
            
        max_dd = drawdown.get('max', {}).get('drawdown', None)
        if max_dd is not None:
            print(f"Max Drawdown: {max_dd:.2f}%")
        else:
            print("Max Drawdown: N/A")

        print(f"\nTRADE ANALYSIS")
        print(f"{'='*50}")
        if trades.get('total', {}).get('total', 0) > 0:
            total_trades = trades['total']['total']
            won_trades = trades.get('won', {}).get('total', 0)
            lost_trades = trades.get('lost', {}).get('total', 0)
            win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0
            
            print(f"Total Trades: {total_trades}")
            print(f"Winning Trades: {won_trades}")
            print(f"Losing Trades: {lost_trades}")
            print(f"Win Rate: {win_rate:.1f}%")
            
            if 'won' in trades and 'pnl' in trades['won']:
                avg_win = trades['won']['pnl']['average']
                print(f"Average Win: £{avg_win:.2f}")
            
            if 'lost' in trades and 'pnl' in trades['lost']:
                avg_loss = trades['lost']['pnl']['average']
                print(f"Average Loss: £{avg_loss:.2f}")
        else:
            print("No trades executed during backtest period")

        # 8. Plot the equity curve & trades
        print(f"\nGenerating plots...")
        cerebro.plot()

    except Exception as e:
        print(f"Error running backtest: {e}")
        import traceback
        traceback.print_exc()