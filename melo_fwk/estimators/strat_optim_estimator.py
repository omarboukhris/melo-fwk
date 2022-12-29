import numpy as np

from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.estimators.utils.strat_optim import StrategyEstimator
from melo_fwk.db.market_data.product import Product

from skopt import BayesSearchCV
from sklearn.model_selection import TimeSeriesSplit

class StratOptimEstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(StratOptimEstimator, self).__init__(**kwargs)

		self.metric = self.next_str_param(default_val="pnl")
		self.n_iter = self.next_int_param(default_val=128)

		self.logger.info("Initialized Estimator")

	def run(self):
		out_dict = dict()
		for i, (product_name, product_dataclass) in enumerate(self.products.items()):
			self.logger.info(f"Running Strategy Optimizer for Product {product_name} {i+1}/{len(self.products)}")
			if self.begin == 0 and self.end == 0:
				begin, end = product_dataclass.years()[0], product_dataclass.years()[1]
			else:
				begin, end = self.begin, self.end
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
