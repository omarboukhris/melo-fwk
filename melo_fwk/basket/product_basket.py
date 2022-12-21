from typing import List

import pandas as pd

from melo_fwk.market_data.product import Product


class ProductBasket:

	def __init__(self, products: List[Product]):
		self.products = products

	def close_df(self) -> pd.DataFrame:
		return pd.DataFrame({
			p.name: p.datastream.get_close_series()
			for p in self.products
		})

	def daily_diff_df(self) -> pd.DataFrame:
		return pd.DataFrame({
			p.name: p.datastream.get_daily_diff_series()
			for p in self.products
		})

	def get_year(self, y: int, stitch: bool = False):
		return ProductBasket([
			p.get_year(y, stitch)
			for p in self.products
		])

	def years(self):
		return set.intersection(*map(set, [p.years() for p in self.products]))

	def block_size_vect(self) -> pd.Series:
		return pd.Series([p.block_size for p in self.products])

	def cap_vect(self) -> List[float]:
		return [p.cap for p in self.products]
