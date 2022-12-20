
from dataclasses import dataclass, field
from typing import ClassVar

import pandas as pd
import tqdm

from melo_fwk.market_data import MarketDataLoader

@dataclass
class BaseStrategy:
	cap: ClassVar[float] = 20.
	scale: float = field(default=1.)

	def __post_init__(self):
		# if self.scale == 1.:
		# 	self.estimate_forecast_scale()
		pass

	def forecast_vect(self, data: pd.DataFrame) -> pd.DataFrame:
		pass

	def forecast_vect_cap(self, data: pd.DataFrame) -> pd.DataFrame:
		f_vect = self.forecast_vect(data).clip(upper=self.cap, lower=-self.cap, axis=0)
		return f_vect

	def to_dict(self):
		pass

	""" rewrite for dataframe """
	def estimate_forecast_scale(self, ratio: float = 0.6):
		sample_products = MarketDataLoader.sample_products_alpha(ratio)

		results = {}

		for product in sample_products:
			for year in product.datastream.years:

				self.scale = 1.
				price_series = product.datastream.get_year(year).get_close_series()
				forecast_series = self.forecast_vect(price_series)
				results.update({f"{product.name}.{year}": forecast_series})

		mean = []
		for key, result in results.items():
			r = pd.Series(result)
			r.apply(abs).apply(mean.append)

		mean_ps = pd.Series(mean)
		scale_f = 10 / mean_ps.mean() if mean_ps.mean() != 0 else 1.

		self.scale = float(scale_f)
		return self