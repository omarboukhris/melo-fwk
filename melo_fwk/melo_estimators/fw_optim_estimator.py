import tqdm
import numpy as np

from melo_fwk.policies.vol_target_policies.base_size_policy import ConstSizePolicy
from melo_fwk.policies.vol_target_policies.vol_target import VolTarget
from melo_fwk.trading_systems.trading_system import TradingSystem

import scipy.optimize as opt

class ForecastWeightsEstimator:

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
		forecast_weights = [1./len(strategies) for _ in strategies] if forecast_weights is None else forecast_weights
		assert len(strategies) == len(forecast_weights), \
			"(ForecastWeightsEstimator) Strategies and Forecast weight do not correspond."
		assert len(products) == 1, \
			"(ForecastWeightsEstimator) Can only optimize weight for 1 product at a time"

		self.product = list(products.values())[0]
		self.current_year = -1
		self.time_period = time_period
		self.strategies = strategies
		self.forecast_weights = np.array(forecast_weights)
		self.vol_target = vol_target
		self.size_policy_class_ = size_policy_class_
		self.metric = estimator_params[0] if len(estimator_params) > 0 else "sharpe"

	def run(self):
		results = []
		self.product.datastream.with_daily_returns()
		self.product.datastream.parse_date_column()

		for year in tqdm.tqdm(range(int(self.time_period[0]), int(self.time_period[1]))):
			self.current_year = year
			results.append(opt.minimize(self.trade_with_weights, self.forecast_weights))

		return results

	def trade_with_weights(self, weights):
		size_policy = self.size_policy_class_(risk_policy=self.vol_target)

		trading_subsys = TradingSystem(
			data_source=self.product.datastream.get_data_by_year(self.current_year),
			trading_rules=self.strategies,
			forecast_weights=weights,
			size_policy=size_policy
		)

		trading_subsys.run()
		tsar = trading_subsys.get_negative_tsar()

		return tsar.account_metrics.get_metric_by_name(self.metric)

