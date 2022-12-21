
import tqdm

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.trading_systems import TradingSystem


class BacktestEstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(BacktestEstimator, self).__init__(**kwargs)
		self.logger.info("BacktestEstimator Initialized")

	def run(self):
		out_dict = dict()

		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		for i, (product_name, product) in tqdm.tqdm(enumerate(self.products.items()), leave=False):
			trading_subsys = TradingSystem(
				trading_rules=self.strategies,
				forecast_weights=self.forecast_weights,
				size_policy=self.size_policy
			)
			out_dict[product_name] = {
				f"{product_name}_{year}": trading_subsys.run_product_year(product, year)
				for year in range(self.begin, self.end)
			}

		self.logger.info("Finished running estimator")
		return out_dict

