
import tqdm

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
		strategies = [] if strategies is None else strategies
		forecast_weights = [] if forecast_weights is None else forecast_weights
		assert len(strategies) == len(forecast_weights), \
			"(BacktestEstimator) Strategies and Forecast weight do not correspond."

		self.products = products
		self.time_period = time_period
		self.strategies = strategies
		self.forecast_weights = forecast_weights
		self.size_policy_class_ = size_policy_class_

		assert len(estimator_params) > 0, \
			"(VolTargetEstimator) Estimator should take trading capital as param"
		self.trading_capital = float(estimator_params[0])
		self.step = float(estimator_params[1]) if len(estimator_params) >= 2 else 0.1
		self.start = float(estimator_params[2]) if len(estimator_params) >= 3 else 0.1
		self.end = float(estimator_params[3]) if len(estimator_params) >= 4 else 1.

	def run(self):
		out_dict = dict()
		for product_name, product_dataclass in tqdm.tqdm(self.products.items()):
			out_dict[product_name] = self._trade_product(product_dataclass)
		return out_dict

	def _trade_product(self, product: Product):
		"""WIP -------------------------------------------"""

		vol_target = VolTarget(
			annual_vol_target=self.start,
			trading_capital=self.trading_capital
		)
		results = dict()
		n_iter = int((self.end - self.start) / self.step)
		for _ in range(n_iter):
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
				key = "{}_{}_{:.1f}".format(
					product.name, year, vol_target.annual_vol_target
				)
				results.update({key: yearly_tsar})
			vol_target.annual_vol_target += self.step

		return results
