
import tqdm

from melo_fwk.trading_systems.trading_system import TradingSystem
from melo_fwk.market_data.product import Product
from melo_fwk.strategies.base_strat import BaseStrategy
from melo_fwk.position_size_policies import (
	BaseSizePolicy,
	VolTarget
)

from typing import List

class BacktestEstimator:

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
		self.vol_target = vol_target
		self.size_policy_class_ = size_policy_class_
		self.reinvest = "reinvest" in estimator_params

	def run(self):
		out_dict = dict()
		if self.reinvest:
			for product_name, product_dataclass in self.products.items():
				out_dict[product_name] = self._trade_product_reinvest(product_dataclass)
		else:
			for product_name, product_dataclass in self.products.items():
				out_dict[product_name] = self._trade_product(product_dataclass)
		return out_dict

	def _trade_product(self, product: Product):

		vol_target = VolTarget(
			annual_vol_target=self.vol_target.annual_vol_target,
			trading_capital=self.vol_target.trading_capital)
		size_policy = self.size_policy_class_(risk_policy=vol_target)

		trading_subsys = TradingSystem(
			product=product,
			trading_rules=self.strategies,
			forecast_weights=self.forecast_weights,
			size_policy=size_policy
		)

		tsar = trading_subsys.run()
		results = dict()
		for year in tqdm.tqdm(range(int(self.time_period[0]), int(self.time_period[1]))):
			yearly_tsar = tsar.get_data_by_year(year)
			results.update({f"{product.name}_{year}": yearly_tsar})

		return results

	def _trade_product_reinvest(self, product: Product):
		balance = self.vol_target.trading_capital
		results = dict()

		for year in tqdm.tqdm(range(int(self.time_period[0]), int(self.time_period[1]))):
			vol_target = VolTarget(
				annual_vol_target=self.vol_target.annual_vol_target,
				trading_capital=balance if self.reinvest else self.vol_target.trading_capital)
			size_policy = self.size_policy_class_(risk_policy=vol_target)

			yearly_prod = Product(
				name=product.name,
				block_size=product.block_size,
				datastream=product.datastream.get_data_by_year(year)
			)
			trading_subsys = TradingSystem(
				product=yearly_prod,
				trading_rules=self.strategies,
				forecast_weights=self.forecast_weights,
				size_policy=size_policy
			)

			tsar = trading_subsys.run()
			# change output file path
			results.update({f"{product.name}_{year}": tsar})
			balance += tsar.annual_delta()

		return results
