import pandas as pd
import numpy as np

from melo_fwk.trading_systems.trading_system import TradingSystem

class PositionAdjust:
	def __init__(self):
		self.curr_pose = 0

	def __call__(self, pose: int):
		"""
		TODO : Add filter on min variation (1 contract ?)
		:param pose:
		:return:
		"""
		pose_diff = pose - self.curr_pose
		thr = self.curr_pose * 0.1
		if (pose_diff > 0 and pose_diff > thr) or (pose_diff < 0 and pose_diff < thr):
			self.curr_pose = pose
		return self.curr_pose

class TradingSystemAdj(TradingSystem):
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
		super(TradingSystemAdj, self).__init__(**kwargs)

	def run(self):

		pos_adj = PositionAdjust()
		forecast_series = self.forecast_cumsum()  # .interpolate()
		pose_series = self.size_policy.position_size_vect(forecast_series).round().apply(pos_adj)  # .interpolate()
		# pose_diff = pose_series.diff()
		daily_pnl_series = self.get_daily_pnl(pose_series)  # .interpolate()
		# orderbook building ??

		return self.build_tsar(forecast_series, pose_series, daily_pnl_series)
