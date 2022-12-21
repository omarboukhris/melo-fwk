import numpy as np
import pandas as pd

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.pose_size.vol_target import VolTarget

class BaseSizePolicy:
	def __init__(
		self,
		annual_vol_target: float,
		trading_capital: float
	):
		self.block_size_vect = np.array([])
		self.cap_vect = pd.DataFrame({})
		self.prod_basket = ProductBasket([])
		self.vol_target = VolTarget(annual_vol_target, trading_capital)

	def update_trading_capital(self, trading_capital: float):
		self.vol_target.trading_capital += trading_capital

	def update_annual_vol_target(self, annual_vol_target: float):
		self.vol_target.annual_vol_target += annual_vol_target

	def setup_product_basket(self, product_basket: ProductBasket):
		self.prod_basket = product_basket
		self.block_size_vect = product_basket.block_size_vect()
		self.cap_vect = product_basket.cap_vect()
		return self

	def position_size_df(self, forecast: pd.DataFrame) -> pd.DataFrame:
		return pd.DataFrame(np.sign(forecast))

	def product_names(self):
		return [p.name for p in self.prod_basket.products]
