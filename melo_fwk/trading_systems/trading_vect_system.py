import numpy as np
import pandas as pd

from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem


class TradingVectSystem(BaseTradingSystem):

	def __init__(self, **kwargs):
		super(TradingVectSystem, self).__init__(**kwargs)

	def forecast_cumsum(self):
		f_series = pd.Series(np.zeros(shape=(len(self.data_source.get_data()))))

		for trading_rule, forecast_weight in zip(self.trading_rules, self.forecast_weights):
			f_series += forecast_weight * trading_rule.forecast(self.data_source.get_data())

		return f_series

	def get_daily_pnl(self):
		open_close_diff = self.data_source.get_daily_diff_vect() * self.current_trade.quantity  # * self.leverage
		daily_pnl_series = open_close_diff if self.current_trade.is_position_long() else -open_close_diff
		return daily_pnl_series

	def trade_vect(self):

		forecast_series = self.forecast_cumsum()
		pose_series = self.size_policy.position_size_vect(forecast_series)
		daily_pnl = self.get_daily_pnl()

		self.tsar_history = {
			"Date": self.data_source.get_data()["Date"],
			"Price": self.data_source.get_data()["Close"],
			"Forecast": forecast_series,
			"PositionSize": pose_series,
			"Daily_PnL": daily_pnl
		}

