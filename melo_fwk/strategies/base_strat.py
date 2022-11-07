
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

	def forecast_vect(self, data: pd.Series) -> pd.Series:
		pass

	def forecast_vect_cap(self, data: pd.Series) -> pd.Series:
		f_vect = self.forecast_vect(data)
		f_series = pd.Series([
			min(f_val, self.cap) if f_val > 0 else max(f_val, -self.cap)
			for f_val in f_vect
		], dtype=float)
		return f_series

	def estimate_forecast_scale(self, ratio: float = 0.6):
		sample_products = MarketDataLoader.sample_products_pool(ratio)

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
		scale_f = 10 / mean_ps.mean()

		self.scale = scale_f
		# scaled_ps = (scale_f * mean_ps)
		# print(mean_ps.mean(), scale_f, scaled_ps.mean())

		# Make plotter, link to appropriate reporter : OptimStrat report
		# plt.hist(mean, bins=100)
		# plt.hist(scaled_ps.to_numpy(), bins=100, color="red", alpha=0.5)
		# plt.show()
