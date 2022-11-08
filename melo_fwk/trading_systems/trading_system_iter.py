import numpy as np
import pandas as pd
import tqdm

from melo_fwk.datastreams import TsarDataStream
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem

class TradingSystemIter(BaseTradingSystem):
	"""Class for backtesting offline a trading system.
	This class trades only one position, one product at a time.
	To backtest for a whole portfolio, you need a TradingSystem per asset,

	This implementation processes data by block

	Input Parameters :
		- a data source for historic price data
		- a set of trading strategies
		- a set of forecast weights (sum(w_i) == 1)
		- a pose sizing policy
	"""

	def __init__(self, **kwargs):
		super(TradingSystemIter, self).__init__(**kwargs)

		self.freq = kwargs["freq"] if "freq" in kwargs.keys() else 5

	def run(self) -> TsarDataStream:
		"""process trades by block"""

		start_capital = self.size_policy.vol_target.trading_capital
		forecast_series, i = self.forecast_cumsum(), 0
		pose_series, daily_pnl = pd.Series(dtype=np.float64), pd.Series(dtype=np.float64)
		nb_batch = int(len(self.product.get_dataframe())/self.freq)
		for i in tqdm.tqdm(range(nb_batch), leave=True):
			# get block starting index
			idx = i * self.freq
			# get pose_series
			current_pose_block = self.size_policy.position_size_vect(forecast_series).iloc[idx:idx + self.freq]
			pose_series = pd.concat([pose_series, current_pose_block])
			# get pnl
			current_daily_diff_block = self.product.get_daily_diff_series().iloc[idx:idx + self.freq] * current_pose_block * self.product.block_size
			daily_pnl = pd.concat([daily_pnl, current_daily_diff_block])
			# adjust vol target with observer if needed
			self.update_trading_capital(current_daily_diff_block.sum())

		# run last block
		last_idx = self.freq * (i + 1)
		if last_idx < len(self.product.get_dataframe()):
			# get pose_series
			current_pose_block = self.size_policy.position_size_vect(forecast_series).iloc[last_idx:]
			pose_series = pd.concat([pose_series, current_pose_block])
			# get pnl
			current_daily_diff_block = self.product.get_daily_diff_series().iloc[last_idx:] * current_pose_block * self.product.block_size
			daily_pnl = pd.concat([daily_pnl, current_daily_diff_block])

		self.size_policy.vol_target.trading_capital = start_capital
		return self.build_tsar(forecast_series, pose_series, daily_pnl)
