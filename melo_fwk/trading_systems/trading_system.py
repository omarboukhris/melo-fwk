import pandas as pd
import numpy as np

from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem

class TradingSystem(BaseTradingSystem):
	"""Class for backtesting offline a trading system.
	This class trades only one position, one product at a time.
	To backtest for a whole portfolio, you need a TradingSystem per asset,
	then sum up after each iteration.

	Input Parameters :
		- a data source for historic price data
		- a set of trading strategies
		- a set of forecast weights (sum(w_i) == 1)
		- a pose sizing policy
	"""

	component_name = "TradingSystem"

	def __init__(self, **kwargs):
		super(TradingSystem, self).__init__(**kwargs)
		self.size_policy.update_datastream(self.hloc_datastream)

	def forecast_cumsum(self):
		f_series = pd.Series(np.zeros(shape=(len(self.hloc_datastream.get_dataframe()))))

		for trading_rule, forecast_weight in zip(self.trading_rules, self.forecast_weights):
			f_series += forecast_weight * trading_rule.forecast_vect_cap(self.hloc_datastream.get_close_series())

		return f_series

	def get_daily_pnl(self, pose_series: pd.Series):
		daily_pnl_series = self.hloc_datastream.get_daily_diff_series() * pose_series * self.block_size
		return daily_pnl_series

	def run(self):

		forecast_series = self.forecast_cumsum()  # .interpolate()
		# pose_series = forecast_series.apply(self.size_policy.position_size).round()  # .interpolate()
		pose_series = self.size_policy.position_size_vect(forecast_series)  # .interpolate()
		daily_pnl = self.get_daily_pnl(pose_series).fillna(0)  # .interpolate()
		# orderbook building ??

		return self.build_tsar(forecast_series, pose_series, daily_pnl)

