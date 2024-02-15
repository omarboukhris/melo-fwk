import numpy as np

from melo_fwk.basket.strat_basket import StratBasket
from melo_fwk.trading_systems.trading_system import TradingSystem
from melo_fwk.basket.weights import Weights


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
		strat_basket = StratBasket(
			strat_list=[self.strat_class_(**self.strat_params)],
			weights=Weights([1.], 1.)
		)

		trading_subsys = TradingSystem(
			strat_basket=strat_basket,
			size_policy=self.size_policy
		)

		tsar = trading_subsys.run_product_year(self.product, X[0])
		# optimizer is minimizing
		return np.nan_to_num(tsar.get_metric_by_name(self.metric))
