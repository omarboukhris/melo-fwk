import numpy as np
from typing import List

import pandas as pd

from melo_fwk.market_data.product import Product


class ProductBasket:

	def __init__(self, products: List[Product]):
		self.products = {p.name: p for p in products}

	def get_by_name(self, name: str):
		return self.products[name]

	def close_df(self) -> pd.DataFrame:
		return pd.DataFrame({
			p.name: p.datastream.get_close_series()
			for p in self.products.values()
		})

	def daily_diff_df(self) -> pd.DataFrame:
		return pd.DataFrame({
			p.name: p.datastream.get_daily_diff_series()
			for p in self.products.values()
		})

	def get_year(self, y: int, stitch: bool = False):
		return ProductBasket([
			p.get_year(y, stitch)
			for p in self.products.values()
		])

	def years(self):
		return set.intersection(*map(set, [p.years() for p in self.products.values()]))

	def block_size_vect(self) -> pd.Series:
		return pd.Series([p.block_size for p in self.products.values()], dtype=np.float64)

	def cap_vect(self) -> List[float]:
		return [p.cap for p in self.products.values()]

	def to_dict(self):
		return {
			"products": [p for p in self.products.keys()],
			"years": [y for y in self.years()]
		}
