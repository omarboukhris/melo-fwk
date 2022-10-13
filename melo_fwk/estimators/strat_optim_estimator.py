import tqdm

from melo_fwk.datastreams.product import Product
from melo_fwk.policies.vol_target_policy import ConstSizePolicy, VolTarget
from melo_fwk.trading_system import TradingSystem

from skopt import BayesSearchCV

"""
estimator from sk
"""
class TradingLoopOptimizer:

	def __init__(self, **kwargs):
		self.strat_params = kwargs

	def score(self, X: tuple):
		size_policy, strat_class, product, metric = X

		trading_subsys = TradingSystem(
			data_source=product,
			trading_rules=[strat_class(**self.strat_params)],
			forecast_weights=[1.],
			size_policy=size_policy
		)

		trading_subsys.run()
		tsar = trading_subsys.get_tsar()
		return tsar.account_metrics.get_metric_by_name(metric)


class StratOptimEstimator:

	def __init__(
		self,
		products: dict,
		time_period: list,
		strategies: list = None,
		_: list = None,
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
		self.size_policy = size_policy_class_(risk_policy=vol_target)
		self.metric = estimator_params[0] if len(estimator_params) > 0 else "sharpe"

	def run(self):
		out_dict = dict()
		for product_name, product_dataclass in self.products.items():
			out_dict[product_name] = self._optimize_product_strat(product_dataclass)
		return out_dict

	def _optimize_product_strat(self, product: Product):

		results = dict()
		product.datastream.with_daily_returns()
		product.datastream.parse_date_column()

		# optimize by strat
		for strat_metadata in self.strategies:
			"""
			strat metadata contains [strat_class][strat_config_search_space]
			"""
			assert len(strat_metadata) == 2, \
				"(StratOptimEstimator) Strat metadata is incomplete (length != 2)"
			# optimize by year
			for year in tqdm.tqdm(range(int(self.time_period[0]), int(self.time_period[1]))):
				opt = BayesSearchCV(
					TradingLoopOptimizer(),
					strat_metadata[1],  # optimization search space
					n_iter=32,
					cv=3
				)
				opt.fit(X=(
					product.datastream.get_data_by_year(year),
					strat_metadata[0],
					self.size_policy,
					self.metric
				))
				results.update({f"{product.filepath}_{year}": opt})

		# aggregate results and cross validate out of sample
		# then return
		return results
