
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG, EURUSD


class SmaCross(Strategy):
    n1 = 4
    n2 = 32

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()


bt = Backtest(GOOG, SmaCross,
    cash=10000, commission=.002,
    exclusive_orders=True)

stats = bt.optimize(
    n1=range(5, 60, 5),
    n2=range(10, 140, 5),
    maximize='Equity Final [$]',
    constraint=lambda param: param.n1 < param.n2)

print(stats)
print("=========================================================")

SmaCross.n1, SmaCross.n2 = stats._strategy.n1, stats._strategy.n2
bt = Backtest(GOOG, SmaCross,
    cash=10000, commission=.002,
    exclusive_orders=True)

output = bt.run()
print(output)
bt.plot()
