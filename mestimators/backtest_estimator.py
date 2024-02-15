
import tqdm

from melo_fwk.basket.strat_basket import StratBasket
from mestimators.base_estimator import MeloBaseEstimator
from melo_fwk.trading_systems import TradingSystem


class BacktestEstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(BacktestEstimator, self).__init__(**kwargs)
		self.logger.info("BacktestEstimator Initialized")

		# read param iter/vect for TSIter/TS

	def run(self):
		out_dict = dict()

		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		strat_basket = StratBasket(
			strat_list=self.strategies,
			weights=self.forecast_weights,
		)
		trading_subsys = TradingSystem(
			strat_basket=strat_basket,
			size_policy=self.size_policy
		)

		for i, (product_name, product) in tqdm.tqdm(enumerate(self.products.items()), leave=False):
			out_dict[product_name] = {
				f"{product_name}_{year}": trading_subsys.run_product_year(product, year)
				for year in range(self.begin, self.end)
			}

		self.logger.info("Finished running estimator")
		return out_dict

