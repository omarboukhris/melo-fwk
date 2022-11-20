import matplotlib.pyplot as plt
import pandas as pd
import tqdm

from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.policies.size.vol_target import VolTarget
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.market_data.product import Product

class VolTargetEstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(VolTargetEstimator, self).__init__(**kwargs)
		self.trading_capital = self.next_float_param(0.)
		self.step = self.next_float_param(0.1)
		self.start = self.next_float_param(0.1)
		self.final = self.next_float_param(1.)
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

		size_policy = self.size_policy
		size_policy.vol_target = VolTarget(
			annual_vol_target=self.start,
			trading_capital=self.trading_capital
		)
		results = dict()
		for year in range(self.begin, self.end):
			results[year] = []

		n_iter = int((self.final - self.start) / self.step)
		for _ in tqdm.tqdm(range(n_iter), leave=False):
			ts = TradingSystem(
				product=product,
				trading_rules=self.strategies,
				forecast_weights=self.forecast_weights,
				size_policy=size_policy,
			)
			tsar = ts.run()

			for year in range(self.begin, self.end):
				yearly_tsar = tsar.get_year(year)
				results[year].append({
					"vol_target": size_policy.vol_target.annual_vol_target,
					"GAR": yearly_tsar.gar(self.trading_capital),  # get geometric returns
				})
			size_policy.update_annual_vol_target(self.step)

		for year in range(self.begin, self.end):
			results[year] = pd.DataFrame(results[year])

		return results
