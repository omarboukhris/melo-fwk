
from melo_fwk.melo_estimators.utils.strat_optim import StrategyEstimator
from melo_fwk.strategies import BaseStrategy
from melo_fwk.market_data.product import Product
from melo_fwk.size_policies import BaseSizePolicy
from melo_fwk.size_policies.vol_target import VolTarget

from sklearn.model_selection import GridSearchCV

import tqdm

from typing import List

class StratOptimEstimator:

	def __init__(
		self,
		products: dict,
		time_period: List[int],
		strategies: List[BaseStrategy] = None,
		forecast_weights: List[int] = None,
		vol_target: VolTarget = VolTarget(0., 0.),
		size_policy_class_: callable = BaseSizePolicy,
		estimator_params: List[str] = None
	):
		strategies = [] if strategies is None else strategies
		assert len(strategies) != 0, \
			"(ForecastWeightsEstimator) Strategies are not defined."

		self.products = products
		self.current_year = -1
		self.time_period = time_period
		self.strategies = strategies
		StrategyEstimator.size_policy = size_policy_class_(risk_policy=vol_target)

		StrategyEstimator.metric = estimator_params[0] if len(estimator_params) > 0 else "sharpe"

	def run(self):
		out_dict = dict()
		for product_name, product_dataclass in self.products.items():
			out_dict[product_name] = self._optimize_product_strat(product_dataclass)
		return out_dict

	def _optimize_product_strat(self, product: Product):

		results = dict()

		# optimize by strat
		for strat_metadata in self.strategies:
			"""
			strat metadata contains [strat_class][strat_config_search_space]
			"""
			assert len(strat_metadata) == 2, \
				"(StratOptimEstimator) Strat metadata is incomplete (length != 2)"
			StrategyEstimator.strat_class_, strat_search_space_ = strat_metadata

			# optimize by year
			for year in tqdm.tqdm(range(int(self.time_period[0]), int(self.time_period[1]))):
				opt = GridSearchCV(
					StrategyEstimator(),
					strat_search_space_,
					cv=[(slice(None), slice(None))]
				)
				StrategyEstimator.product = Product(
					name=product.name,
					block_size=product.block_size,
					datastream=product.datastream.get_data_by_year(year))
				opt.fit(X=StrategyEstimator.product.datastream.get_dataframe())
				results.update({f"{product.name}_{year}": opt})

		# aggregate results and cross validate out of sample
		# then return
		return results
