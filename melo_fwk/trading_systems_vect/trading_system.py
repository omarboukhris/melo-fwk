from typing import List

from melo_fwk.basket.results_basket import ResultsBasket
from melo_fwk.datastreams import TsarDataStream
from melo_fwk.trading_systems_vect.base_trading_system import BaseTradingSystem

import numpy as np

class TradingSystem(BaseTradingSystem):
	"""Class for backtesting offline a trading system.
	This class trades only one position, one product at a time.
	To backtest for a whole portfolio, you need a TradingSystem per asset,

	Input Parameters :
		- a data source for historic price data
		- a set of trading strategies
		- a set of forecast weights (sum(w_i) == 1)
		- a pose sizing policy
	"""

	def __init__(self, **kwargs):
		super(TradingSystem, self).__init__(**kwargs)

	def run(self) -> ResultsBasket:
		forecast_df = self.forecast_cumsum()
		pose_df = self.size_policy.position_size_df(forecast_df)
		pose_block_mat = np.einsum("i,ji->ji", self.product_basket.block_size_vect().to_numpy(), pose_df.to_numpy())
		daily_pnl_df = self.product_basket.daily_diff_df() * pose_block_mat

		return self.build_tsar(forecast_df, pose_df, daily_pnl_df)
