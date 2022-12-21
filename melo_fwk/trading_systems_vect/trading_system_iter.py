import numpy as np
import pandas as pd
import tqdm

from melo_fwk.basket.results_basket import ResultsBasket
from melo_fwk.datastreams import TsarDataStream
from melo_fwk.trading_systems_vect.base_trading_system import BaseTradingSystem

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

	def run(self, verbose=True) -> ResultsBasket:
		"""process trades by block"""

		start_capital = self.size_policy.vol_target.trading_capital
		forecast_df, i = self.forecast_cumsum(), 0
		pose_df, daily_pnl_df = pd.DataFrame(dtype=np.float64), pd.DataFrame(dtype=np.float64)
		nb_batch = int(len(self.product_basket.close_df())/self.freq)
		block_size_vect = self.product_basket.block_size_vect().to_numpy()

		loop_range = tqdm.tqdm(range(nb_batch), leave=False) if verbose else range(nb_batch)
		for i in loop_range:
			# get block starting index
			idx = i * self.freq
			# get pose_series
			current_pose_block = self.size_policy.position_size_df(forecast_df).iloc[idx:idx + self.freq]
			pose_df = pd.concat([pose_df, current_pose_block])
			# get pnl
			pose_block_mat = np.einsum("i,ji->ji", block_size_vect, current_pose_block.to_numpy())
			current_daily_diff_block = self.product_basket.daily_diff_df().iloc[idx:idx + self.freq] * pose_block_mat

			daily_pnl_df = pd.concat([daily_pnl_df, current_daily_diff_block])
			# adjust vol target with observer if needed
			self.update_trading_capital(current_daily_diff_block.sum())

		# run last block
		last_idx = self.freq * (i + 1)
		if last_idx < len(self.product_basket.close_df()):
			# get pose_series
			current_pose_block = self.size_policy.position_size_df(forecast_df).iloc[last_idx:]
			pose_df = pd.concat([pose_df, current_pose_block])
			# get pnl
			pose_block_mat = np.einsum("i,ji->ji", block_size_vect, current_pose_block.to_numpy())
			current_daily_diff_block = self.product_basket.daily_diff_df().iloc[last_idx:last_idx + self.freq] * pose_block_mat
			daily_pnl_df = pd.concat([daily_pnl_df, current_daily_diff_block])

		self.size_policy.vol_target.trading_capital = start_capital
		return self.build_tsar(forecast_df, pose_df, daily_pnl_df)
