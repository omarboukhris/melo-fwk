import pandas as pd
import numpy as np

from melo_fwk.datastreams.tsar_datastream import TradingSystemAnnualResult
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem

class TradingSystem(BaseTradingSystem):
	"""Class for backtesting offline a trading system.
	This class trades only one position, one product at a time.
	To backtest for a whole portfolio, you need a TradingSystem per asset,
	then sum up after each iteration.
	Sub-classes can implement multi-threaded execution if needed.

	Needs :
	- a data source for historic price data
	- a set of trading rules
	- a set of forcast weights (sum(w_i) == 1)
	- a pose sizing policy
	- a policy for entering/exiting trades
	"""

	component_name = "TradingSystem"

	def __init__(self, **kwargs):
		super(TradingSystem, self).__init__(**kwargs)
		self.size_policy.update_datastream(self.data_source)

	def forecast_cumsum(self):
		f_series = pd.Series(np.zeros(shape=(len(self.data_source.get_dataframe()))))

		for trading_rule, forecast_weight in zip(self.trading_rules, self.forecast_weights):
			f_series += forecast_weight * trading_rule.forecast_vect_cap(self.data_source.get_close_series())

		return f_series

	def get_daily_pnl(self, pose_series: pd.Series):
		daily_pnl_series = self.data_source.get_daily_diff_series() * pose_series  # * self.block_size
		return daily_pnl_series

	def run(self):

		forecast_series = self.forecast_cumsum()  # .interpolate()
		pose_series = self.size_policy.position_size_vect(forecast_series)  # .interpolate()
		daily_pnl = self.get_daily_pnl(pose_series).fillna(0)  # .interpolate()
		# orderbook building ??

		return TradingSystemAnnualResult(
			dates=self.data_source.get_date_series(),
			price_series=self.data_source.get_close_series(),
			forecast_series=forecast_series,
			size_series=pose_series,
			account_series=daily_pnl.expanding(1).sum(),
			daily_pnl_series=daily_pnl
		)

