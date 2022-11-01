import matplotlib.pyplot as plt
import pandas as pd
import tqdm

from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.market_data.product import Product
from melo_fwk.strategies import BaseStrategy
from melo_fwk.size_policies import BaseSizePolicy
from melo_fwk.size_policies.vol_target import VolTarget


from typing import List

class VolTargetEstimator:

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
		self.logger = GlobalLogger.build_composite_for("VolTargetEstimator")

		strategies = [] if strategies is None else strategies
		forecast_weights = [] if forecast_weights is None else forecast_weights
		assert len(strategies) == len(forecast_weights), self.logger.error(
			"Strategies and Forecast weight do not correspond.")

		self.products = products
		self.time_period = time_period
		self.strategies = strategies
		self.forecast_weights = forecast_weights
		self.size_policy_class_ = size_policy_class_

		assert len(estimator_params) > 0, self.logger.error(
			"Estimator should take trading capital as param")
		self.trading_capital = float(estimator_params[0])
		self.step = float(estimator_params[1]) if len(estimator_params) >= 2 else 0.1
		self.start = float(estimator_params[2]) if len(estimator_params) >= 3 else 0.1
		self.end = float(estimator_params[3]) if len(estimator_params) >= 4 else 2.

		self.logger.info("Initialized Estimator")

	def run(self):
		out_dict = dict()
		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		for i, (product_name, product_dataclass) in tqdm.tqdm(enumerate(self.products.items()), leave=False):
			out_dict[product_name] = self._trade_product(product_dataclass)
		self.logger.info("Finished running estimator")

		for key, result in out_dict.items():
			key = key.replace(".", "_")
			for year, df in result.items():
				df.plot(x="vol_target", y="GAR")
				plt.savefig(f"data/residual/{key}_{year}.png")
				plt.close()

		return out_dict

	def _trade_product(self, product: Product):
		"""WIP -------------------------------------------"""

		vol_target = VolTarget(
			annual_vol_target=self.start,
			trading_capital=self.trading_capital
		)
		results = dict()
		for year in range(int(self.time_period[0]), int(self.time_period[1])):
			results[year] = []

		n_iter = int((self.end - self.start) / self.step)
		for _ in tqdm.tqdm(range(n_iter), leave=False):
			size_policy = self.size_policy_class_(risk_policy=vol_target)
			ts = TradingSystem(
				product=product,
				trading_rules=self.strategies,
				forecast_weights=self.forecast_weights,
				size_policy=size_policy,
			)
			tsar = ts.run()

			for year in range(int(self.time_period[0]), int(self.time_period[1])):
				yearly_tsar = tsar.get_data_by_year(year)
				results[year].append({
					"vol_target": vol_target.annual_vol_target,
					"GAR": yearly_tsar.gar(),  # get geometric returns
				})
			vol_target.annual_vol_target += self.step

		for year in range(int(self.time_period[0]), int(self.time_period[1])):
			results[year] = pd.DataFrame(results[year])

		return results
