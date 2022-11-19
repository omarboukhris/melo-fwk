import numpy as np

from melo_fwk.datastreams.hloc_datastream import HLOCDataStream
from dataclasses import dataclass

from melo_fwk.datastreams.utils import common


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

