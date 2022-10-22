
from melo_fwk.trading_systems.trading_system import TradingSystem
from melo_fwk.market_data.product import Product
from melo_fwk.size_policies import BaseSizePolicy

import pandas as pd

class StrategyEstimator:
	product: Product
	size_policy: BaseSizePolicy
	strat_class_: callable
	metric: str

	def __init__(self, **kwargs):
		self.strat_params = kwargs

	def get_params(self, deep=True):
		return self.strat_params

	def set_params(self, **kwargs):
		return StrategyEstimator(**kwargs)

	def fit(self, X):
		return self

	def score(self, X: pd.Series):
		strat = StrategyEstimator.strat_class_(**self.strat_params)

		trading_subsys = TradingSystem(
			product=StrategyEstimator.product,
			trading_rules=[strat],
			forecast_weights=[1.],
			size_policy=StrategyEstimator.size_policy
		)

		tsar = trading_subsys.run()
		estimated_result = tsar.get_metric_by_name(StrategyEstimator.metric)
		return estimated_result
