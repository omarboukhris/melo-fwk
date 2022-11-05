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

	def __init__(self, **kwargs):
		super(TradingSystem, self).__init__(**kwargs)

	def run(self):
		forecast_series = self.forecast_cumsum()
		pose_series = self.size_policy.position_size_vect(forecast_series)
		daily_pnl = self.product.get_daily_diff_series() * pose_series * self.product.block_size

		return self.build_tsar(forecast_series, pose_series, daily_pnl)

	def run_year(self, year: int, stitch=True):
		product = self.product
		self.product = self.product.get_year(year, stitch)
		self.size_policy.setup_product(self.product)
		try:
			# use get year in case of stitching
			return self.run().get_year(year)
		finally:
			self.product = product
