import numpy as np
import pandas as pd

from melo_fwk.market_data.product import Product
from melo_fwk.size_policies.vol_target import VolTarget


class BaseSizePolicy:
	def __init__(self, vol_target: VolTarget = VolTarget(0., 0.)):
		self.block_size = 1.
		self.datastream = None
		self.vol_target = vol_target

	def setup_product(self, product: Product):
		self.datastream = product.datastream
		self.block_size = product.block_size
		return self

	def update_risk_policy(self, risk_policy: VolTarget):
		self.vol_target = risk_policy

	def position_size_vect(self, forecast: pd.Series) -> pd.Series:
		return pd.Series(np.ones(shape=(len(forecast),)))
