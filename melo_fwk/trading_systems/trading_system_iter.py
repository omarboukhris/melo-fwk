import numpy as np
import pandas as pd
import tqdm

from melo_fwk.basket.results_basket import ResultsBasket
from melo_fwk.datastreams import TsarDataStream
from melo_fwk.db.market_data.product import Product
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
		self.block_size_vect = np.array([])
		self.freq = kwargs["freq"] if "freq" in kwargs.keys() else 5

	def run_product(self, product: Product, verbose: bool = True) -> TsarDataStream:
		self.size_policy.setup_product(product)
		start_capital = self.size_policy.vol_target.trading_capital
		forecast_series, i = self.strat_basket.forecast_cumsum_product(product), 0
		pose_series, daily_pnl = pd.Series(dtype=np.float64), pd.Series(dtype=np.float64)
		nb_batch = int(len(product.get_dataframe())/self.freq)

		loop_range = tqdm.tqdm(range(nb_batch), leave=False) if verbose else range(nb_batch)
		for i in loop_range:
			# get block starting index
			idx = i * self.freq
			# get pose_series
			current_pose_block = self.size_policy.position_size_vect(forecast_series).iloc[idx:idx + self.freq]
			# get pnl
			current_daily_diff_block = product.get_daily_diff_series().iloc[idx:idx + self.freq] * current_pose_block * product.block_size

			pose_series = pd.concat([pose_series, current_pose_block])
			daily_pnl = pd.concat([daily_pnl, current_daily_diff_block])
			# adjust vol target with observer if needed
			self.update_trading_capital(current_daily_diff_block.sum())

		# run last block
		last_idx = self.freq * (i + 1)
		if last_idx < len(product.get_dataframe()):
			# get pose_series
			current_pose_block = self.size_policy.position_size_vect(forecast_series).iloc[last_idx:]
			pose_series = pd.concat([pose_series, current_pose_block])
			# get pnl
			current_daily_diff_block = product.get_daily_diff_series().iloc[last_idx:] * current_pose_block * product.block_size
			daily_pnl = pd.concat([daily_pnl, current_daily_diff_block])

		self.size_policy.vol_target.trading_capital = start_capital
		return TradingSystemIter.build_tsar(product, forecast_series, pose_series, daily_pnl)


	def run(self, verbose=True) -> ResultsBasket:
		"""process trades by block"""
		self.size_policy = self.size_policy.setup_product_basket(self.product_basket)
		self.block_size_vect = self.product_basket.block_size_vect().to_numpy()

		start_capital = self.size_policy.vol_target.trading_capital
		forecast_df, i = self.strat_basket.forecast_cumsum(self.product_basket), 0
		pose_df, daily_pnl_df = pd.DataFrame(dtype=np.float64), pd.DataFrame(dtype=np.float64)
		nb_batch = int(len(self.product_basket.close_df())/self.freq)

		loop_range = tqdm.tqdm(range(nb_batch), leave=False) if verbose else range(nb_batch)
		for i in loop_range:
			# get block starting index
			idx = i * self.freq

			# get pose_series and pnl
			current_daily_diff_block, current_pose_block = self.process_block(forecast_df, idx)

			#update result
			pose_df = pd.concat([pose_df, current_pose_block])
			daily_pnl_df = pd.concat([daily_pnl_df, current_daily_diff_block])

			# adjust vol target with observer if needed
			self.update_trading_capital(current_daily_diff_block.sum())

		# run last block
		last_idx = self.freq * (i + 1)
		if last_idx < len(self.product_basket.close_df()):
			# get pose_series and pnl
			current_daily_diff_block, current_pose_block = self.process_block(forecast_df, last_idx)

			#update result
			pose_df = pd.concat([pose_df, current_pose_block])
			daily_pnl_df = pd.concat([daily_pnl_df, current_daily_diff_block])

		self.size_policy.vol_target.trading_capital = start_capital
		return self.build_tsar_basket(forecast_df, pose_df, daily_pnl_df)

	def process_block(self, forecast_df, idx):
		current_pose_block = self.size_policy.position_size_df(forecast_df).iloc[idx:idx + self.freq]
		pose_block_mat = np.einsum("i,ji->ji", self.block_size_vect, current_pose_block.to_numpy())
		current_daily_diff_block = self.product_basket.daily_diff_df().iloc[idx:idx + self.freq] * pose_block_mat
		return current_daily_diff_block, current_pose_block
