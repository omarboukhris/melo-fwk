import pandas as pd
import tqdm

from melo_fwk.basket.strat_basket import StratBasket
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.pose_size.vol_target import VolTarget
from melo_fwk.trading_systems import TradingSystemIter
from melo_fwk.market_data.product import Product

class VolTargetEstimator(MeloBaseEstimator):
	"""
	VolTargetEstimator class is a subclass of the MeloBaseEstimator class. It is used to optimize the
	volatility target for a trading system.
	"""

	def __init__(self, **kwargs):
		"""
		Constructor for the VolTargetEstimator class. Calls the constructor of the parent class MeloBaseEstimator
		and initializes the logger.
		It also initializes the following instance variables:
			trading_capital: The trading capital for the trading system.
			step: The step size for incrementing the volatility target.
			start: The starting value for the volatility target.
			final: The final value for the volatility target.
		"""
		super(VolTargetEstimator, self).__init__(**kwargs)
		self.trading_capital = self.estimator_params_dict.get("trading_capital", 0.)
		self.step = self.estimator_params_dict.get("step", 0.1)
		self.start = self.estimator_params_dict.get("start", 0.1)
		self.final = self.estimator_params_dict.get("final", 1.)
		self.logger.info("Initialized Estimator")

	def run(self):
		"""
		Runs the volatility target optimization for all products in the products dictionary of the VolTargetEstimator instance.
		Returns a dictionary of data frames containing the optimization results for each product.
		"""
		output_dict = dict()
		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		for i, (product_name, product_dataclass) in tqdm.tqdm(enumerate(self.products.items()), leave=False):
			output_dict[product_name] = self._trade_product(product_dataclass)
		self.logger.info("Finished running estimator")

		return output_dict

	def _trade_product(self, product: Product):
		"""
		Optimizes the volatility target for a given product.
		Returns a data frame containing the optimization results.
		"""
		size_policy = self.size_policy
		size_policy.vol_target = VolTarget(
			annual_vol_target=self.start,
			trading_capital=self.trading_capital
		)
		results = list()

		n_iter = int((self.final - self.start) / self.step)
		for _ in tqdm.tqdm(range(n_iter), leave=False):
			ts = TradingSystemIter(
				strat_basket=StratBasket(
					strat_list=self.strategies,
					weights=self.forecast_weights,
				),
				size_policy=size_policy,
			)
			tsar = ts.run_product(product)

			results.append({
				"vol_target": size_policy.vol_target.annual_vol_target,
				"gar": tsar.gar(),  # get geometric returns
			})
			size_policy.update_annual_vol_target(self.step)

		return pd.DataFrame(results)
