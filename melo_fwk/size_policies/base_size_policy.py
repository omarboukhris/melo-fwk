import numpy as np
import pandas as pd

from melo_fwk.market_data.product import Product
from melo_fwk.size_policies.vol_target import VolTarget


class BaseSizePolicy:
	def __init__(
		self,
		annual_vol_target: float,
		trading_capital: float
	):
		self.block_size = 1.
		self.datastream = None
		self.vol_target = VolTarget(annual_vol_target, trading_capital)

	def update_trading_capital(self, trading_capital: float):
		self.vol_target.trading_capital += trading_capital

	def update_annual_vol_target(self, annual_vol_target: float):
		self.vol_target.annual_vol_target += annual_vol_target

	def setup_product(self, product: Product):
		self.datastream = product.datastream
		self.block_size = product.block_size
		return self

	def position_size_vect(self, forecast: pd.Series) -> pd.Series:
		return pd.Series(np.ones(shape=(len(forecast),)))
