from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.start_basket import StratBasket
from melo_fwk.strategies import BaseStrategy
from melo_fwk.pose_size import BaseSizePolicy
from melo_fwk.loggers.global_logger import GlobalLogger

from typing import List, Union, Type

from melo_fwk.trading_systems import TradingSystem
from melo_fwk.utils.weights import Weights


class MeloBaseEstimator:

	def __init__(
		self,
		products: dict,
		time_period: List[int],
		strategies: List[Union[BaseStrategy, tuple]],
		forecast_weights: Weights,
		size_policy: Union[BaseSizePolicy, Type[BaseSizePolicy]],
		estimator_params: List[str]
	):
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)

		assert len(strategies) == len(forecast_weights.weights), self.logger.error(
			"Strategies and Forecast weight do not correspond.")

		self.products = products
		self.begin, self.end = time_period
		self.strategies = strategies
		self.forecast_weights = forecast_weights
		self.size_policy = size_policy
		self.estimator_params = iter(estimator_params)

	def build_trading_system_cluster(self):
		strat_basket = StratBasket(
			strat_list=self.strategies,
			weights=self.forecast_weights,
		)
		prod_basket = ProductBasket([p for p in self.products.values()])
		return TradingSystem(
			product_basket=prod_basket,
			strat_basket=strat_basket,
			size_policy=self.size_policy,
		)

	def next_str_param(self, default_val):
		try:
			return next(self.estimator_params)
		except StopIteration:
			return default_val

	def next_int_param(self, default_val):
		return int(self.next_str_param(default_val))

	def next_float_param(self, default_val):
		return float(self.next_str_param(default_val))
