from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.datastreams import HLOCDataStream
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.market_data.product import Product
from melo_fwk.trading_systems import TradingSystem

from scipy.optimize import minimize, Bounds
import pandas as pd
import numpy as np
import tqdm

import warnings
warnings.filterwarnings('ignore', message='The objective has been evaluated at this point before.')

class ForecastWeightsEstimator(MeloBaseEstimator):
	ForecastDivMultiplier: float = 2.

	@staticmethod
	def objective(W, exp_ret, covmat):
		return -(W.T @ exp_ret) * ((W.T @ covmat @ W) ** -0.5)

	@staticmethod
	def get_div_mult(corrmat_ret, opt_result):
		opt_params = np.array(opt_result.x)
		corrmat_ret[corrmat_ret < 0] = 0.
		raw_div_mult = (opt_params.T @ corrmat_ret @ opt_params) ** -0.5
		div_mult = min(ForecastWeightsEstimator.ForecastDivMultiplier, raw_div_mult)
		return div_mult

	def __init__(self, **kwargs):
		super(ForecastWeightsEstimator, self).__init__(**kwargs)
		self.logger.info("Initialized Estimator")

	def run(self):
		out_dict = dict()
		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		for product_name, product_dataclass in tqdm.tqdm(self.products.items(), leave=False):
			out_dict[product_name] = self.optimize_weights_by_product(product_dataclass)
		self.logger.info("Finished running estimator")
		return out_dict

	def optimize_weights_by_product(self, product: Product):
		results = []
		years = [year for year in range(self.begin, self.end)]
		rolling_datastream = product.rolling_dataframe(years)
		for i, subset_prod_ds in tqdm.tqdm(enumerate(rolling_datastream), leave=False):

			opt_bounds = Bounds(0., 1.)
			expected_ret, returns = self.get_expected_results(Product(
				name=product.name,
				block_size=product.block_size,
				cap=product.cap,
				datastream=HLOCDataStream(dataframe=subset_prod_ds)
			))
			opt_cst = {'type': 'eq', 'fun': lambda W: 1.0 - np.sum(W)}

			opt_result = minimize(
				ForecastWeightsEstimator.objective,
				np.array(self.forecast_weights),
				args=(expected_ret, returns.cov()),
				method='SLSQP',
				bounds=opt_bounds,
				constraints=opt_cst,
				tol=1e-5
			)
			div_mult = ForecastWeightsEstimator.get_div_mult(returns.corr(), opt_result)
			results.append({
				"OptimResult.fun": -opt_result.fun,
				"OptimResult.x": opt_result.x,
				"DivMult": div_mult
			})

		return pd.DataFrame(results)

	def get_expected_results(self, product: Product):
		# param is pool sample from products
		result = []
		returns = {}

		for strategy in self.strategies:
			trading_subsys = TradingSystem(
				trading_rules=[strategy],
				forecast_weights=[1.],
				size_policy=self.size_policy,
			)

			tsar = trading_subsys.run_product(product)
			key = f"{product.name}.{str(strategy)}"
			returns.update({key: tsar.account_series})
			result.append(tsar.account_series.mean())

		return np.array(result), pd.DataFrame(returns)
