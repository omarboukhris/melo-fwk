import numpy as np

from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.estimators.utils.strat_optim import StrategyEstimator
from melo_fwk.market_data.product import Product
from melo_fwk.policies.size.base_size_policy import BaseSizePolicy

from skopt import BayesSearchCV
from sklearn.model_selection import TimeSeriesSplit

from typing import List

class StratOptimEstimator:

	def __init__(
		self,
		products: dict,
		time_period: List[int],
		strategies: List[tuple] = None,
		forecast_weights: List[int] = None,
		size_policy: BaseSizePolicy = None,
		estimator_params: List[str] = None
	):
		self.logger = GlobalLogger.build_composite_for("StratOptimEstimator")

		strategies = [] if strategies is None else strategies
		assert len(strategies) != 0, self.logger.error("Strategies are not defined.")

		self.products = products
		self.current_year = -1
		self.time_period = time_period
		self.strategies = strategies
		self.size_policy = size_policy
		self.metric = estimator_params[0] if len(estimator_params) > 0 else "pnl"
		self.n_iter = int(estimator_params[1]) if len(estimator_params) > 1 else 128

		self.logger.info("Initialized Estimator")

	def run(self):
		out_dict = dict()
		for i, (product_name, product_dataclass) in enumerate(self.products.items()):
			self.logger.info(f"Running Strategy Optimizer for Product {product_name} {i+1}/{len(self.products)}")
			if self.time_period == [0, 0]:
				begin, end = product_dataclass.years()[0], product_dataclass.years()[1]
			else:
				begin, end = self.time_period
			out_dict[product_name] = self._optimize_product_strat(product_dataclass, begin, end)
		self.logger.info("Finished running estimator")
		return out_dict

	def _optimize_product_strat(self, product: Product, begin: int, end: int):
		results = dict()

		for strat_metadata in self.strategies:
			"""
			strat metadata contains [strat_class][strat_config_search_space]
			"""
			assert len(strat_metadata) == 2, \
				"(StratOptimEstimator) Strat metadata is incomplete (length != 2)"
			strat_class_, strat_search_space_ = strat_metadata

			self.logger.info(f"Optimizing Strategy <{strat_class_.__name__}>")

			X = np.array([year for year in range(begin, end)])
			# set max_train_size for out of sample or expanding cv
			tscv = TimeSeriesSplit(n_splits=len(X)-1, test_size=1, max_train_size=3)

			static_params = {
				"product": [product],
				"strat_class_": [strat_class_],
				"size_policy": [self.size_policy],
				"metric": [self.metric],
			}
			strat_search_space_.update(static_params)

			self.logger.info(f"Running BayesSearchCV for {self.n_iter * (len(X)-1)} fits")
			opt = BayesSearchCV(
				StrategyEstimator(**static_params),
				strat_search_space_,
				n_iter=self.n_iter,
				n_jobs=12, n_points=12,
				cv=tscv, verbose=1,
			)
			opt.fit(X=X)
			results.update({f"{strat_class_.__name__}": opt})

		return results
