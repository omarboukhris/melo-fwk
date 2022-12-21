
import tqdm

from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.trading_systems import TradingSystem


class BacktestEstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(BacktestEstimator, self).__init__(**kwargs)
		self.compound = "compound" in self.estimator_params
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
			trading_subsys = TradingSystem(
				product=product_dataclass,
				trading_rules=self.strategies,
				forecast_weights=self.forecast_weights,
				size_policy=self.size_policy
			)
			out_dict[product_name] = trade_fn_(trading_subsys)
		self.logger.info("Finished running estimator")
		return out_dict

	def _trade_product(self, trading_subsys: BaseTradingSystem):
		results = {
			f"{trading_subsys.product.name}_{year}": trading_subsys.run_year(year)
			for year in range(self.begin, self.end)
		}

		return results

	def _trade_product_compound(self, trading_subsys: BaseTradingSystem):
		results = {
			f"{trading_subsys.product.name}_{year}": trading_subsys.compound_by_year()
			for year in range(self.begin, self.end)
		}

		return results
