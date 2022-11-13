
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.market_data.product import Product
from melo_fwk.policies.size import BaseSizePolicy
from melo_fwk.strategies import BaseStrategy
from melo_fwk.trading_systems import TradingSystem

from scipy.optimize import minimize, Bounds
from skopt import gp_minimize
from typing import List
import pandas as pd
import numpy as np
import tqdm

import warnings
warnings.filterwarnings('ignore', message='The objective has been evaluated at this point before.')

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
		size_policy: BaseSizePolicy = None,
		estimator_params: List[str] = None
	):
		self.logger = GlobalLogger.build_composite_for("ForecastWeightsEstimator")

		strategies = [] if strategies is None else strategies
		forecast_weights = [1./len(strategies) for _ in strategies] if forecast_weights is None else forecast_weights
		assert len(strategies) == len(forecast_weights), self.logger.error(
			"Strategies and Forecast weight do not correspond.")

		self.products = products
		self.time_period = time_period
		self.strategies = strategies
		self.forecast_weights = np.array(forecast_weights)
		self.size_policy = size_policy
		self.metric = estimator_params[0] if len(estimator_params) > 0 else "sharpe"

		self.logger.info("Initialized Estimator")

	def run(self):
		out_dict = dict()
		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		for product_name, product_dataclass in tqdm.tqdm(self.products.items(), leave=False):
			out_dict[product_name] = self._optimize_weights_by_product(product_dataclass)
		self.logger.info("Finished running estimator")
		return out_dict

	def _optimize_weights_by_product(self, product: Product):
		results = {}
		for year in tqdm.tqdm(range(int(self.time_period[0]), int(self.time_period[1])), leave=False):

			opt_bounds = Bounds(0., 1.)
			expected_ret, covmat_ret = self.get_expected_results(product, year)
			opt_cst = {'type': 'eq', 'fun': lambda W: 1.0 - np.sum(W)}

			opt_result = minimize(
				ForecastWeightsEstimator.objective,
				self.forecast_weights,
				args=(expected_ret, covmat_ret),
				method='SLSQP',
				bounds=opt_bounds,
				constraints=opt_cst,
				tol=1e-5
			)
			div_mult = ForecastWeightsEstimator.get_div_mult(covmat_ret, opt_result)
			results[year] = {
				"OptimResult": opt_result,
				"DivMult": div_mult
			}

		return results

	def get_expected_results(self, product: Product, year: int):
		# param is pool sample from products
		result = []
		returns = {}

		for strategy in self.strategies:
			trading_subsys = TradingSystem(
				product=product,
				trading_rules=[strategy],
				forecast_weights=[1.],
				size_policy=self.size_policy,
			)

			tsar = trading_subsys.run_year(year)
			key = f"{product.name}.{str(strategy)}"
			returns.update({key: tsar.account_series})
			result.append(tsar.get_metric_by_name(self.metric))

		return np.array(result), pd.DataFrame(returns).corr()
