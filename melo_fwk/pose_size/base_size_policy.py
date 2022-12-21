import numpy as np
import pandas as pd

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.market_data.product import Product
from melo_fwk.pose_size.vol_target import VolTarget

class BaseSizePolicy:
	def __init__(
		self,
		annual_vol_target: float,
		trading_capital: float
	):
		# basket process data
		self.block_size_vect = np.array([])
		self.cap_vect = pd.DataFrame({})
		self.prod_basket = ProductBasket([])

		# single process data
		self.datastream = None
		self.block_size = 0
		self.cap = None

		# common
		self.vol_target = VolTarget(annual_vol_target, trading_capital)

	def update_trading_capital(self, trading_capital: float):
		"""Common"""
		self.vol_target.trading_capital += trading_capital

	def update_annual_vol_target(self, annual_vol_target: float):
		"""Common"""
		self.vol_target.annual_vol_target += annual_vol_target

	def setup_product_basket(self, product_basket: ProductBasket):
		"""Basket"""
		self.prod_basket = product_basket
		self.block_size_vect = product_basket.block_size_vect()
		self.cap_vect = product_basket.cap_vect()
		return self

	def position_size_df(self, forecast: pd.DataFrame) -> pd.DataFrame:
		"""Basket"""
		return pd.DataFrame(np.sign(forecast))

	def product_names(self):
		"""Basket"""
		return [p.name for p in self.prod_basket.products]

	def setup_product(self, product: Product):
		self.datastream = product.datastream
		self.block_size = product.block_size
		self.cap = product.cap
		return self

	def position_size_vect(self, forecast: pd.Series) -> pd.Series:
		return pd.Series(np.sign(forecast))
