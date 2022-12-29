import pandas as pd
import tqdm

from melo_fwk.basket.start_basket import StratBasket
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.pose_size.vol_target import VolTarget
from melo_fwk.trading_systems import TradingSystemIter
from melo_fwk.db.market_data.product import Product

class VolTargetEstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(VolTargetEstimator, self).__init__(**kwargs)
		self.trading_capital = self.next_float_param(0.)
		self.step = self.next_float_param(0.1)
		self.start = self.next_float_param(0.1)
		self.final = self.next_float_param(1.)
		self.logger.info("Initialized Estimator")

	def run(self):
		output_dict = dict()
		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		for i, (product_name, product_dataclass) in tqdm.tqdm(enumerate(self.products.items()), leave=False):
			output_dict[product_name] = self._trade_product(product_dataclass)
		self.logger.info("Finished running estimator")

		return output_dict

	def _trade_product(self, product: Product):
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
