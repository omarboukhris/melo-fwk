
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem

import numpy as np
import pandas as pd

class TradingVectSystem(BaseTradingSystem):

	def __init__(self, **kwargs):
		super(TradingVectSystem, self).__init__(**kwargs)
		self.size_policy.update_datastream(self.data_source)

	def forecast_cumsum(self):
		f_series = pd.Series(np.zeros(shape=(len(self.data_source.get_data()))))

		for trading_rule, forecast_weight in zip(self.trading_rules, self.forecast_weights):
			f_series += forecast_weight * trading_rule.forecast_vect_cap(self.data_source.get_data())

		return f_series

	def get_daily_pnl(self, pose_series: pd.Series):
		daily_pnl_series = self.data_source.get_daily_diff_vect() * pose_series  # * self.block_size
		return daily_pnl_series

	def run(self):

		forecast_series = self.forecast_cumsum()
		pose_series = self.size_policy.position_size_vect(forecast_series).fillna(0)
		daily_pnl = self.get_daily_pnl(pose_series).fillna(0)
		# orderbook building ??

		self.tsar_history = {
			"Date": self.data_source.get_dates(),
			"Price": self.data_source.get_close(),
			"Forecast": forecast_series,
			"PositionSize": pose_series,
			"Daily_PnL": daily_pnl
		}

