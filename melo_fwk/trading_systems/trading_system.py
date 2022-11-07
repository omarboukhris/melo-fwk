
from melo_fwk.datastreams import TsarDataStream
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem

class TradingSystem(BaseTradingSystem):
	"""Class for backtesting offline a trading system.
	This class trades only one position, one product at a time.
	To backtest for a whole portfolio, you need a TradingSystem per asset,

	Input Parameters :
		- a data source for historic price data
		- a set of trading strategies
		- a set of forecast weights (sum(w_i) == 1)
		- a pose sizing policy
	"""

	def __init__(self, **kwargs):
		super(TradingSystem, self).__init__(**kwargs)

	def run(self) -> TsarDataStream:
		forecast_series = self.forecast_cumsum()
		pose_series = self.size_policy.position_size_vect(forecast_series)
		daily_pnl = self.product.get_daily_diff_series() * pose_series * self.product.block_size

		return self.build_tsar(forecast_series, pose_series, daily_pnl)
