from typing import List

import numpy as np
import pandas as pd

from melo_fwk.datastreams.hloc_datastream import HLOCDataStream
from dataclasses import dataclass

@dataclass(frozen=True)
class Product:
	name: str
	block_size: int
	datastream: HLOCDataStream

	def years(self):
		return self.datastream.years

	def get_years(self, years: list):
		assert np.array([year in self.years() for year in years]).all(), \
			f"(AssertionError) Product {self.name} : {years} not in {self.years()}"
		return Product(
			name=self.name,
			block_size=self.block_size,
			datastream=self.datastream.get_years(years)
		)

	def get_year(self, year: int, stitch: bool = False):
		assert year in self.years(), f"(AssertionError) Product {self.name} : {year} not in {self.years()}"
		return Product(
			name=self.name,
			block_size=self.block_size,
			datastream=self.datastream.get_year(year, stitch)
		)

	def get_date_series(self):
		return self.datastream.get_date_series()

	def get_close_series(self):
		return self.datastream.get_close_series()

	def get_dataframe(self):
		return self.datastream.get_dataframe()

	def get_daily_diff_series(self):
		return self.datastream.get_daily_diff_series()

	def rolling_dataframe(self, years: List[int] = None, window_size: int = 250, min_periods: int = 250, step: int = 20):
		years = self.years() if years is None else years
		prod_datastream = self.get_years(years).datastream
		indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=window_size)
		rolling_datastream = prod_datastream.dataframe.rolling(window=indexer, min_periods=min_periods, step=step)
		for roll in rolling_datastream:
			if len(roll) >= window_size:
				yield roll

	def rolling(self, years: List[int] = None, window_size: int = 250, min_periods: int = 250, step: int = 20):
		years = self.years() if years is None else years
		prod_datastream = self.get_years(years).datastream
		indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=window_size)
		rolling_datastream = prod_datastream.dataframe.rolling(window=indexer, min_periods=min_periods, step=step)
		for roll in rolling_datastream:
			if len(roll) >= window_size:
				yield Product(
					name=self.name,
					block_size=self.block_size,
					datastream=roll,
				)
