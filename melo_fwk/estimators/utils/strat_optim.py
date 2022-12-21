import numpy as np

from minimelo.trading_systems.trading_system import TradingSystem

class StrategyEstimator:

	def __init__(self, **kwargs):
		self.product = kwargs.pop("product", None)
		self.size_policy = kwargs.pop("size_policy", None)
		self.strat_class_ = kwargs.pop("strat_class_", None)
		self.metric = kwargs.pop("metric", None)
		self.strat_params = kwargs

	def get_params(self, deep=True):
		return self.strat_params

	def set_params(self, **kwargs):
		return StrategyEstimator(**kwargs)

	def fit(self, X):
		return self

	def score(self, X: np.ndarray):
		strat = self.strat_class_(**self.strat_params)

		trading_subsys = TradingSystem(
			product=self.product,
			trading_rules=[strat],
			forecast_weights=[1.],
			size_policy=self.size_policy
		)

		tsar = trading_subsys.run_year(X[0])
		# optimizer is minimizing
		return np.nan_to_num(tsar.get_metric_by_name(self.metric))
