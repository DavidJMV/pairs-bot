import backtrader as bt
from signals import generate_signal

class PairsStrategy(bt.Strategy):
    params = dict(
        window=240,          # rolling window for z-score - 4 hour window
        entry_z=4.0,         # entry threshold - only extreme signals
        exit_z=1.0,          # exit threshold - let winners run longer
        max_z=6.0            # emergency exit - allow mean reversion
    )

    def __init__(self):
        # Keep references to the two price lines (already log prices from run_backtest.py)
        self.shell = self.datas[0].close    # SHEL.L log price
        self.bp    = self.datas[1].close    # BP.L log price

        # Calculate spread directly (no need for Log() since data is already log prices)
        self.log_spread = self.shell - self.bp
        self.mu    = bt.indicators.SimpleMovingAverage(self.log_spread, period=self.p.window)
        self.sigma = bt.indicators.StandardDeviation(self.log_spread, period=self.p.window)
        
        # Track current position state
        self.position_state = 0  # 0=flat, 1=long spread, -1=short spread

    def next(self):
        # Skip if we don't have enough data for indicators
        if len(self) < self.p.window:
            return
            
        # Avoid division by zero
        if self.sigma[0] == 0:
            return
            
        # Compute current z-score
        z = (self.log_spread[0] - self.mu[0]) / self.sigma[0]
        
        # Determine current position
        shell_pos = self.getposition(self.datas[0]).size
        bp_pos = self.getposition(self.datas[1]).size
        
        pos = 0
        if shell_pos > 0 and bp_pos < 0:
            pos = 1  # long spread (long SHEL, short BP)
        elif shell_pos < 0 and bp_pos > 0:
            pos = -1  # short spread (short SHEL, long BP)

        new_pos, action = generate_signal(z, pos, self.p.entry_z, self.p.exit_z, self.p.max_z)

        # Debug output to understand exit behavior
        if pos != 0:
            self.log(f'IN POSITION: Z={z:.2f}, Action={action}, Entry_Z={self.p.entry_z}, Exit_Z={self.p.exit_z}, Max_Z={self.p.max_z}')

        if action == 'enter_long':
            # Long spread: buy SHEL, sell BP
            # Use 90% of available cash for maximum sizing on rare signals
            available_cash = min(450, self.broker.getcash() * 0.9)
            size = max(20, int(available_cash / 80))  # Larger positions
            
            if not shell_pos and not bp_pos:  # Only enter if flat
                self.buy(data=self.datas[0], size=size)
                self.sell(data=self.datas[1], size=size)
                self.position_state = 1
                self.log(f'ENTER LONG SPREAD: Z={z:.2f}, Size={size}')

        elif action == 'enter_short':
            # Short spread: sell SHEL, buy BP
            available_cash = min(450, self.broker.getcash() * 0.9)
            size = max(20, int(available_cash / 80))
            
            if not shell_pos and not bp_pos:  # Only enter if flat
                self.sell(data=self.datas[0], size=size)
                self.buy(data=self.datas[1], size=size)
                self.position_state = -1
                self.log(f'ENTER SHORT SPREAD: Z={z:.2f}, Size={size}')

        elif action == 'exit':
            # Close both legs
            if shell_pos != 0:
                self.close(data=self.datas[0])
                self.log(f'EXIT SPREAD: Z={z:.2f}, Reason: {"Normal" if abs(z) < self.p.exit_z else "Stop Loss"}')
            if bp_pos != 0:
                self.close(data=self.datas[1])
            self.position_state = 0
            
    def log(self, txt, dt=None):
        """Logging function for strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}: {txt}')

    def notify_order(self, order):
        """Track order status"""
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED: {order.data._name}, Size: {order.executed.size}, Price: {order.executed.price:.4f}')
            else:
                self.log(f'SELL EXECUTED: {order.data._name}, Size: {order.executed.size}, Price: {order.executed.price:.4f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order {order.getstatusname()}: {order.data._name}')

    def notify_trade(self, trade):
        """Track completed trades"""
        if trade.isclosed:
            self.log(f'TRADE CLOSED: {trade.data._name}, P&L: {trade.pnl:.2f}')
