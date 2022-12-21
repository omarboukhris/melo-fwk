from typing import List

from melo_fwk.basket.results_basket import ResultsBasket
from melo_fwk.datastreams import TsarDataStream
from melo_fwk.market_data.product import Product
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem

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

	def run_product(self, product: Product) -> TsarDataStream:
		self.size_policy.setup_product(product)
		forecast_series = self.forecast_cumsum_product(product)
		pose_series = self.size_policy.position_size_vect(forecast_series)
		daily_pnl = product.get_daily_diff_series().to_numpy() * pose_series * product.block_size

		return TradingSystem.build_tsar(product, forecast_series, pose_series, daily_pnl)

	def run(self) -> ResultsBasket:
		forecast_df = self.forecast_cumsum()
		pose_df = self.size_policy.position_size_df(forecast_df)
		pose_block_mat = np.einsum("i,ji->ji", self.product_basket.block_size_vect().to_numpy(), pose_df.to_numpy())
		daily_pnl_df = self.product_basket.daily_diff_df() * pose_block_mat

		return self.build_tsar_basket(forecast_df, pose_df, daily_pnl_df)
