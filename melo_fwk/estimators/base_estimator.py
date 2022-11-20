import pandas as pd

from melo_fwk.strategies import BaseStrategy
from melo_fwk.policies.size.base_size_policy import BaseSizePolicy
from melo_fwk.loggers.global_logger import GlobalLogger

from itertools import dropwhile
from typing import List, Union

class MeloBaseEstimator:

	def __init__(
		self,
		products: dict,
		time_period: List[int],
		strategies: List[Union[BaseStrategy, tuple]],
		forecast_weights: List[int],
		size_policy: Union[BaseSizePolicy, callable],
		estimator_params: List[str]
	):
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)

		assert len(strategies) == len(forecast_weights), self.logger.error(
			"Strategies and Forecast weight do not correspond.")

		self.products = products
		self.begin, self.end = time_period
		self.strategies = strategies
		self.forecast_weights = forecast_weights
		self.size_policy = size_policy
		self.estimator_params = iter(estimator_params)

	def next_str_param(self, default_val):
		try:
			return next(self.estimator_params)
		except StopIteration:
			return default_val

	def next_int_param(self, default_val):
		return int(self.next_str_param(default_val))

	def next_float_param(self, default_val):
		return float(self.next_str_param(default_val))

	def _get_rolling_datastream(self, product):
		years = [year for year in range(self.begin, self.end)]
		prod_datastream = product.get_years(years).datastream
		indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=250)
		rolling_datastream = prod_datastream.dataframe.rolling(window=indexer, min_periods=250, step=20)
		for roll in rolling_datastream:
			if len(roll) >= 249:
				yield roll
