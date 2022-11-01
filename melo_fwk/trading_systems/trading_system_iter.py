import pandas as pd
import numpy as np

from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem

class TradingSystemIter(BaseTradingSystem):
	"""Class for backtesting offline a trading system.
	This class trades only one position, one product at a time.
	To backtest for a whole portfolio, you need a TradingSystem per asset,
	then sum up after each iteration.

	This implementation processes data by block and

	Input Parameters :
		- a data source for historic price data
		- a set of trading strategies
		- a set of forecast weights (sum(w_i) == 1)
		- a pose sizing policy
	"""

	def __init__(self, **kwargs):
		super(TradingSystemIter, self).__init__(**kwargs)

		self.starting_capital = kwargs["starting_capital"]
		self.observer = kwargs["observers"]
		self.freq = kwargs["freq"] if "freq" in kwargs.keys() else 1

	def run(self):
		# process by block
		forecast_series, i = self.forecast_cumsum(), 0
		pose_series, daily_pnl = pd.Series(), pd.Series()
		for i in range(int(len(self.product.get_dataframe())/self.freq)):
			# get block starting index
			idx = i * self.freq
			# get pose_series
			pose_series = pd.concat([
				pose_series,
				self.size_policy.position_size_vect(forecast_series).iat[idx:idx + self.freq]
			])
			# get pnl
			daily_pnl = pd.concat([
				daily_pnl,
				self.product.get_daily_diff_series() * pose_series * self.product.block_size
			])
			# adjust vol target with observer if needed
			self.observer(self.size_policy, daily_pnl)

		# run last block
		last_idx = self.freq * (i + 1)
		if last_idx < len(self.product.get_dataframe()):
			pose_series = pd.concat([
				pose_series,
				self.size_policy.position_size_vect(forecast_series).iat[last_idx:]
			])
			daily_pnl = pd.concat([
				daily_pnl,
				self.product.get_daily_diff_series() * pose_series * self.product.block_size
			])

		return self.build_tsar(forecast_series, pose_series, daily_pnl)
