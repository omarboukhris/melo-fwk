import pandas as pd
import tqdm
from sklearn.model_selection import GridSearchCV

from melo_fwk.market_data.utils.product import Product
from melo_fwk.datastreams.hloc_datastream import HLOCDataStream
from melo_fwk.policies.vol_target_policies.base_size_policy import ISizePolicy, ConstSizePolicy
from melo_fwk.policies.vol_target_policies.vol_target import VolTarget
from melo_fwk.trading_systems.trading_system import TradingSystem

from skopt import BayesSearchCV

# ###################################################################
# Optimzer shouldn't evaluate the same point twice
# This filters warnings w/ message
# "The objective has been evaluated at this point before."
import warnings
warnings.filterwarnings('ignore',
	message='The objective has been evaluated at this point before.')
# ###################################################################

class StrategyEstimator:
	hloc_df: pd.Series
	size_policy: ISizePolicy
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

		trading_subsys = TradingSystem(
			data_source=StrategyEstimator.hloc_df,
			trading_rules=[StrategyEstimator.strat_class_(**self.strat_params)],
			forecast_weights=[1.],
			size_policy=StrategyEstimator.size_policy
		)

		tsar = trading_subsys.run()
		estimated_result = tsar.get_metric_by_name(StrategyEstimator.metric)
		return estimated_result

class StratOptimEstimator:

	def __init__(
		self,
		products: dict,
		time_period: list,
		strategies: list = None,
		forecast_weights: list = None,
		vol_target: VolTarget = VolTarget(0., 0.),
		size_policy_class_: callable = ConstSizePolicy,
		estimator_params: list = None
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
				StrategyEstimator.hloc_df = product.datastream.get_data_by_year(year)
				opt.fit(X=StrategyEstimator.hloc_df.get_dataframe())
				results.update({f"{product.name}_{year}": opt})

		# aggregate results and cross validate out of sample
		# then return
		return results
