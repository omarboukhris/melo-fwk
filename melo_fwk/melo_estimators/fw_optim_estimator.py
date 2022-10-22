import pandas as pd
import tqdm
import numpy as np

from melo_fwk.market_data.product import Product
from melo_fwk.size_policies import (
	BaseSizePolicy,
	VolTarget
)
from melo_fwk.strategies import BaseStrategy
from melo_fwk.trading_systems import TradingSystem

from scipy.optimize import minimize, Bounds

from typing import List

class ForecastWeightsEstimator:
	ForecastDivMultiplier: float = 2.

	@staticmethod
	def objective(W, exp_ret, covmat):
		return -((W.T @ exp_ret) / (W.T @ covmat @ W) ** 0.5)

	@staticmethod
	def get_div_mult(covmat_ret, opt_result):
		opt_params = np.array(opt_result.x)
		covmat_ret[covmat_ret < 0] = 0.
		raw_div_mult = (opt_params.transpose() @ covmat_ret @ opt_params) ** -0.5
		div_mult = min(ForecastWeightsEstimator.ForecastDivMultiplier, raw_div_mult)
		return div_mult

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

		for year in tqdm.tqdm(range(int(self.time_period[0]), int(self.time_period[1]))):
			self.current_year = year

			opt_bounds = Bounds(0, 1)
			expected_ret, covmat_ret = self.get_expected_results_by_strategy()
			opt_cst = [
				{'type': 'eq', 'fun': lambda W: 1.0 - np.sum(W)},
				# {'type': 'eq', 'fun': lambda W: np.max(exp_ret) - W.T @ exp_ret}
			]

			opt_result = minimize(
				ForecastWeightsEstimator.objective,
				self.forecast_weights,
				args=(expected_ret, covmat_ret),
				method='SLSQP',
				bounds=opt_bounds,
				constraints=opt_cst
			)
			div_mult = ForecastWeightsEstimator.get_div_mult(covmat_ret, opt_result)
			results.append({
				"OptimResult": opt_result,
				"DivMult": div_mult
			})

		return results

	def get_expected_results_by_strategy(self):
		size_policy = self.size_policy_class_(risk_policy=self.vol_target)
		result = []
		returns = {}

		for strategy in self.strategies:
			y_prod = Product(
				name=self.product.name,
				block_size=self.product.block_size,
				datastream=self.product.datastream.get_data_by_year(self.current_year)
			)
			trading_subsys = TradingSystem(
				product=y_prod,
				trading_rules=[strategy],
				forecast_weights=[1.],
				size_policy=size_policy,
			)

			tsar = trading_subsys.run()
			key = f"{self.product.name}.{str(strategy)}"
			returns.update({key: tsar.account_series})
			result.append(tsar.get_metric_by_name(self.metric))

		return np.array(result), pd.DataFrame(returns).corr()