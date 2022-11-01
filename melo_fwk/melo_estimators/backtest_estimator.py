
import tqdm

from melo_fwk.trading_systems import TradingSystem
from melo_fwk.market_data.product import Product
from melo_fwk.strategies import BaseStrategy
from melo_fwk.size_policies import BaseSizePolicy
from melo_fwk.size_policies.vol_target import VolTarget


from typing import List

from melo_fwk.loggers.global_logger import GlobalLogger


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
		self.logger = GlobalLogger.build_composite_for("BacktestEstimator")

		strategies = [] if strategies is None else strategies
		forecast_weights = [] if forecast_weights is None else forecast_weights
		assert len(strategies) == len(forecast_weights), self.logger.error(
			"Strategies and Forecast weight do not correspond.")

		self.products = products
		self.time_period = time_period
		self.strategies = strategies
		self.forecast_weights = forecast_weights
		self.vol_target = vol_target
		self.size_policy_class_ = size_policy_class_
		self.compound = "compound" in estimator_params

		self.logger.info("BacktestEstimator Initialized")

	def run(self):
		out_dict = dict()

		if self.compound:
			self.logger.info("Running multi-year Backtest with trading capital adjustment")
			trade_fn_ = self._trade_product_compound
		else:
			self.logger.info("Running multi-year Backtest with fixed volatility target")
			trade_fn_ = self._trade_product

		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		for i, (product_name, product_dataclass) in tqdm.tqdm(enumerate(self.products.items()), leave=False):
			out_dict[product_name] = trade_fn_(product_dataclass)
		self.logger.info("Finished running estimator")
		return out_dict

	def _trade_product(self, product: Product):

		size_policy = self.size_policy_class_(
			risk_policy=self.vol_target,
			block_size=product.block_size
		)

		trading_subsys = TradingSystem(
			product=product,
			trading_rules=self.strategies,
			forecast_weights=self.forecast_weights,
			size_policy=size_policy
		)

		tsar = trading_subsys.run()
		results = dict()
		for year in range(int(self.time_period[0]), int(self.time_period[1])):
			yearly_tsar = tsar.get_data_by_year(year)
			results.update({f"{product.name}_{year}": yearly_tsar})

		return results

	def _trade_product_compound(self, product: Product):
		results = dict()
		for year in range(int(self.time_period[0]), int(self.time_period[1])):
			size_policy = self.size_policy_class_(risk_policy=self.vol_target)
			trading_subsys = TradingSystem(
				product=product.get_year(year),
				trading_rules=self.strategies,
				forecast_weights=self.forecast_weights,
				size_policy=size_policy
			)

			tsar = trading_subsys.run().get_data_by_year(year)
			results.update({f"{product.name}_{year}": tsar})
			self.vol_target.trading_capital += tsar.annual_delta()

		return results
