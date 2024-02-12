from melo_fwk.basket.strat_basket import StratBasket
from melo_fwk.datastreams import HLOCDataStream
from mestimators.base_estimator import MeloBaseEstimator
from mestimators.utils.weights_optim import WeightsOptim
from melo_fwk.market_data.product import Product
from melo_fwk.trading_systems import TradingSystem

import pandas as pd
import numpy as np
import tqdm

import warnings

from melo_fwk.basket.weights import Weights

warnings.filterwarnings('ignore', message='The objective has been evaluated at this point before.')

class ForecastWeightsEstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(ForecastWeightsEstimator, self).__init__(**kwargs)
		self.logger.info("Initialized Estimator")

	def run(self):
		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		out_dict = {
			product_name: self.optimize_weights_by_product(product_dataclass)
			for product_name, product_dataclass in tqdm.tqdm(self.products.items(), leave=False)
		}
		self.logger.info("Finished running estimator")
		return out_dict

	def optimize_weights_by_product(self, product: Product):
		results = []
		years = [year for year in range(self.begin, self.end)]
		rolling_datastream = product.rolling_dataframe(years)
		for i, subset_prod_ds in tqdm.tqdm(enumerate(rolling_datastream), leave=False):

			mean_returns, returns = self.get_expected_results(Product(
				name=product.name,
				block_size=product.block_size,
				cap=product.cap,
				datastream=HLOCDataStream(dataframe=subset_prod_ds)
			))

			opt_result, div_mult = WeightsOptim.optimize_weights(
				mean_returns, returns, self.forecast_weights.weights
			)

			results.append({
				"OptimResult.fun": -opt_result.fun,
				"OptimResult.x": opt_result.x,
				"DivMult": div_mult
			})

		return pd.DataFrame(results)

	def get_expected_results(self, product: Product):
		# param is pool sample from products
		mean_results = []
		returns = {}

		for strategy in self.strategies:
			trading_subsys = TradingSystem(
				strat_basket=StratBasket(
					strat_list=[strategy],
					weights=Weights([1.], 1.)
				),
				size_policy=self.size_policy,
			)

			tsar = trading_subsys.run_product(product)
			key = f"{product.name}.{str(strategy)}"
			returns.update({key: tsar.account_series})
			mean_results.append(tsar.account_series.mean())

		return np.array(mean_results), pd.DataFrame(returns)
